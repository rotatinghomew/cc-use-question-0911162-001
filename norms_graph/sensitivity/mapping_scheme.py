from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from norms_graph.clauses.contract import ContractError, DomainRecord, identifier, stable_hash
from norms_graph.semantics.scope_bridge import canonical_term, map_field

RESOLUTION_NUMERIC = 'numeric'
RESOLUTION_RESOLVED = 'resolved'
RESOLUTION_UNRESOLVED = 'unresolved'

TERM_STATUSES = (RESOLUTION_NUMERIC, RESOLUTION_RESOLVED, RESOLUTION_UNRESOLVED)


@dataclass(frozen=True)
class TermResolution:
    field: str
    source_term: str
    resolved_value: Any
    status: str
    confidence: float
    reason: str

    def as_dict(self) -> dict[str, Any]:
        return {'field': self.field, 'source_term': self.source_term,
                'resolved_value': self.resolved_value, 'status': self.status,
                'confidence': self.confidence, 'reason': self.reason}


@dataclass(frozen=True)
class MappingScheme:
    scheme_id: str
    aliases: Mapping[str, str] = field(default_factory=dict)
    vocabulary: frozenset[str] = frozenset()
    description: str = ''

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> 'MappingScheme':
        if not isinstance(value, Mapping):
            raise ContractError('mapping scheme must be an object')
        scheme_id = value.get('scheme_id')
        if not scheme_id or not str(scheme_id).strip():
            raise ContractError('mapping scheme requires a scheme_id')
        raw_aliases = value.get('aliases', {})
        if not isinstance(raw_aliases, Mapping):
            raise ContractError('mapping scheme aliases must be an object')
        aliases = {canonical_term(key): canonical_term(target) for key, target in raw_aliases.items()}
        raw_vocabulary = value.get('vocabulary', [])
        if not isinstance(raw_vocabulary, (list, tuple, set, frozenset)):
            raise ContractError('mapping scheme vocabulary must be a list')
        vocabulary = frozenset(canonical_term(item) for item in raw_vocabulary)
        return cls(identifier(scheme_id), dict(sorted(aliases.items())), vocabulary,
                   str(value.get('description', '')))

    def as_dict(self) -> dict[str, Any]:
        return {'scheme_id': self.scheme_id, 'description': self.description,
                'aliases': dict(self.aliases), 'vocabulary': sorted(self.vocabulary)}

    @property
    def fingerprint(self) -> str:
        return stable_hash({'scheme_id': self.scheme_id, 'aliases': self.aliases,
                            'vocabulary': sorted(self.vocabulary)})


def resolve_field(scheme: MappingScheme, field_name: str, value: Any) -> TermResolution:
    """Resolve one payload value under a mapping scheme.

    Numeric and boolean values pass through untouched. String terms are resolved
    through the alias table and vocabulary. A term that cannot be resolved is
    returned with status ``unresolved`` together with the reason — never silently
    coerced to zero or dropped from the evidence chain.
    """
    if isinstance(value, bool) or isinstance(value, (int, float)) or value is None:
        return TermResolution(field_name, '' if value is None else str(value), value,
                              RESOLUTION_NUMERIC, 1.0, 'numeric_passthrough')
    source = canonical_term(value)
    if not source:
        return TermResolution(field_name, source, value, RESOLUTION_UNRESOLVED, 0.0,
                              'empty_term')
    alias_target = scheme.aliases.get(source)
    if alias_target is not None:
        if scheme.vocabulary and alias_target not in scheme.vocabulary:
            return TermResolution(field_name, source, source, RESOLUTION_UNRESOLVED, 0.0,
                                  'alias_target_not_in_vocabulary')
        confidence = map_field(source, alias_target, value, scheme.aliases).confidence
        return TermResolution(field_name, source, alias_target, RESOLUTION_RESOLVED,
                              confidence, 'alias_match')
    if not scheme.vocabulary:
        return TermResolution(field_name, source, source, RESOLUTION_UNRESOLVED, 0.0,
                              'no_vocabulary_defined')
    if source in scheme.vocabulary:
        return TermResolution(field_name, source, source, RESOLUTION_RESOLVED, 1.0,
                              'vocabulary_match')
    return TermResolution(field_name, source, source, RESOLUTION_UNRESOLVED, 0.0,
                          'term_not_in_vocabulary')


@dataclass(frozen=True)
class ResolvedView:
    scheme_id: str
    scheme_fingerprint: str
    record_id: str
    payload: dict[str, Any]
    resolutions: tuple[TermResolution, ...]
    unresolved_fields: tuple[str, ...]
    view_fingerprint: str

    def as_dict(self) -> dict[str, Any]:
        return {'scheme_id': self.scheme_id, 'scheme_fingerprint': self.scheme_fingerprint,
                'record_id': self.record_id, 'payload': self.payload,
                'resolutions': [item.as_dict() for item in self.resolutions],
                'unresolved_fields': list(self.unresolved_fields),
                'view_fingerprint': self.view_fingerprint}


def apply_scheme(scheme: MappingScheme, record: DomainRecord) -> ResolvedView:
    """Project a record through the mapping scheme.

    Resolved terms are replaced by their canonical concept token so downstream
    rule evaluation sees the mapped口径. Unresolved terms keep their original
    raw value (evidence is preserved) and are enumerated separately so the
    sensitivity layer can flag the conflict core as indeterminate.
    """
    payload: dict[str, Any] = {}
    resolutions: list[TermResolution] = []
    unresolved: list[str] = []
    for field_name, value in record.payload.items():
        resolution = resolve_field(scheme, field_name, value)
        resolutions.append(resolution)
        if resolution.status == RESOLUTION_UNRESOLVED:
            unresolved.append(field_name)
            payload[field_name] = record.payload.get(field_name)
        else:
            payload[field_name] = resolution.resolved_value
    fingerprint = stable_hash({'record_id': record.record_id, 'scheme': scheme.fingerprint,
                               'payload': payload, 'unresolved_fields': unresolved})
    return ResolvedView(scheme.scheme_id, scheme.fingerprint, record.record_id, payload,
                        tuple(resolutions), tuple(unresolved), fingerprint)


def view_record(record: DomainRecord, view: ResolvedView) -> DomainRecord:
    return DomainRecord(record.record_id, view.payload, record.state, record.version,
                        record.occurred_at, record.source)

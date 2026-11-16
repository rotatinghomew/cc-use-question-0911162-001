from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from norms_graph.analysis.conflict_graph import GUARDS, decide
from norms_graph.clauses.contract import Decision, DomainRecord, ContractError, stable_hash
from norms_graph.conflict_signal.conflict_pressure import conflict_pressure
from norms_graph.semantics.normalization import RULES
from norms_graph.sensitivity.mapping_scheme import (
    MappingScheme, ResolvedView, RESOLUTION_UNRESOLVED, apply_scheme, view_record,
)

CORE_SUBSTANTIVE = 'substantive'
CORE_RANKING_ONLY = 'ranking_only'
CORE_UNRESOLVED = 'unresolved'
CORE_UNCHANGED = 'unchanged'

CORE_STATUSES = (CORE_SUBSTANTIVE, CORE_RANKING_ONLY, CORE_UNRESOLVED, CORE_UNCHANGED)

# Below the info threshold the conflict pressure would count as "no conflict".
ZERO_CONFLICT_PRESSURE = 0.36
# Floating point tolerance used when comparing replayed decision scores.
DEFAULT_SCORE_TOLERANCE = 1e-9


def rule_catalog_fingerprint() -> str:
    """Fingerprint of the rule/guard catalog actually used by the engine.

    Sensitivity claims are only valid when two mapping schemes are evaluated
    against the same rule version (catalog). A mismatch is reported instead of
    producing a misleading comparison.
    """
    rule_names = tuple(rule.__name__ for rule in RULES)
    guard_names = tuple(guard.__name__ for guard in GUARDS)
    return stable_hash({'rules': rule_names, 'guards': guard_names})[:24]


@dataclass(frozen=True)
class CoreEvaluation:
    record_id: str
    rule_version_group: str
    outcome: str
    decision_score: float
    pressure: float
    severity: str
    has_unresolved: bool
    unresolved_fields: tuple[str, ...]
    decision: Decision
    view: ResolvedView
    raw_record: DomainRecord

    def as_dict(self) -> dict[str, Any]:
        return {'record_id': self.record_id, 'rule_version_group': self.rule_version_group,
                'outcome': self.outcome, 'decision_score': self.decision_score,
                'pressure': self.pressure, 'severity': self.severity,
                'has_unresolved': self.has_unresolved,
                'unresolved_fields': list(self.unresolved_fields),
                'view': self.view.as_dict(),
                'raw_record': {'record_id': self.raw_record.record_id,
                               'payload': self.raw_record.payload},
                'decision_signature': decision_signature(self.decision)}


def decision_signature(decision: Decision) -> dict[str, Any]:
    """Replay-stable decision content excluding the wall-clock timestamp."""
    body = decision.as_dict()
    body.pop('decided_at', None)
    return body


def replay_context(records: Sequence[DomainRecord], index: int) -> dict[str, Any]:
    """Reconstruct the exact context the application built for record ``index``.

    ``Application.process`` derives context from the repository contents at the
    moment the record is processed, i.e. the records already ingested in fixture
    order. Replaying that prefix makes the sensitivity analysis reproducible
    against the published dossier rather than drifting with repository state.
    """
    from norms_graph.semantics.scope_bridge import derive_context
    from norms_graph.conflict_signal.conflict_pressure import augment_context

    current = records[index]
    prefix = list(records[:index + 1])

    class PrefixRepository:
        def list_records(self) -> list[DomainRecord]:
            # Mirror Repository.list_records, which orders by record_id.
            return sorted(prefix, key=lambda item: item.record_id)

    context = dict(derive_context(current, PrefixRepository()))
    context.update(augment_context(current, PrefixRepository()))
    return context


def evaluate_under_scheme(scheme: MappingScheme, records: Sequence[DomainRecord]) -> list[CoreEvaluation]:
    """Run the full decision engine for every record under one mapping scheme."""
    results: list[CoreEvaluation] = []
    for index, record in enumerate(records):
        view = apply_scheme(scheme, record)
        projected = view_record(record, view)
        context = replay_context(records, index)
        decision = decide(projected, context)
        signal = conflict_pressure(projected.payload)
        results.append(CoreEvaluation(
            record_id=record.record_id,
            rule_version_group=str(record.payload.get('rule_version', 'unknown')),
            outcome=decision.outcome,
            decision_score=decision.score,
            pressure=signal.score,
            severity=signal.severity,
            has_unresolved=bool(view.unresolved_fields),
            unresolved_fields=view.unresolved_fields,
            decision=decision,
            view=view,
            raw_record=record,
        ))
    return results


def rank_cores(cores: Sequence[CoreEvaluation]) -> dict[str, int]:
    """Deterministic pressure ranking: highest pressure first, record_id tiebreak."""
    ordered = sorted(cores, key=lambda core: (-core.pressure, core.record_id))
    return {core.record_id: position + 1 for position, core in enumerate(ordered)}


def _spearman_rho(left: Mapping[str, int], right: Mapping[str, int]) -> float | None:
    keys = sorted(set(left) & set(right))
    if len(keys) < 2:
        return None
    n = len(keys)
    d_squared = sum((left[key] - right[key]) ** 2 for key in keys)
    return 1.0 - (6.0 * d_squared) / (n * (n * n - 1))


def _classify(baseline: CoreEvaluation, candidate: CoreEvaluation,
              baseline_rank: int, candidate_rank: int,
              group_baseline_rank: int, group_candidate_rank: int) -> str:
    # Unresolved evidence always wins: an indeterminate core must never be
    # presented as a confirmed substantive change or as zero conflict.
    if baseline.has_unresolved or candidate.has_unresolved:
        return CORE_UNRESOLVED
    if baseline.outcome != candidate.outcome or baseline.severity != candidate.severity:
        return CORE_SUBSTANTIVE
    # A move in either the portfolio rank or the same-rule-version rank is a
    # genuine ordering change, even when the core's own metrics are unchanged
    # (relative reordering caused by another core moving).
    if baseline_rank != candidate_rank or group_baseline_rank != group_candidate_rank:
        return CORE_RANKING_ONLY
    if abs(baseline.pressure - candidate.pressure) > 1e-12 or \
            abs(baseline.decision_score - candidate.decision_score) > 1e-12:
        # Metrics moved but were not enough to change any ordering or severity.
        return CORE_RANKING_ONLY
    return CORE_UNCHANGED


def _core_comparison(baseline: CoreEvaluation, candidate: CoreEvaluation,
                     baseline_rank: int, candidate_rank: int,
                     group_baseline_rank: int, group_candidate_rank: int) -> dict[str, Any]:
    status = _classify(baseline, candidate, baseline_rank, candidate_rank,
                       group_baseline_rank, group_candidate_rank)
    return {
        'record_id': baseline.record_id,
        'rule_version_group': baseline.rule_version_group,
        'status': status,
        'baseline': baseline.as_dict(),
        'candidate': candidate.as_dict(),
        'ranking': {
            'overall': {'baseline': baseline_rank, 'candidate': candidate_rank,
                        'delta': candidate_rank - baseline_rank},
            'within_rule_version': {'baseline': group_baseline_rank,
                                    'candidate': group_candidate_rank,
                                    'delta': group_candidate_rank - group_baseline_rank},
        },
        'deltas': {
            'pressure': candidate.pressure - baseline.pressure,
            'decision_score': candidate.decision_score - baseline.decision_score,
        },
    }


def _zero_conflict_cores(cores: Sequence[CoreEvaluation]) -> list[str]:
    """Cores with no conflict claim. Unresolved cores never qualify — missing
    evidence must not be read as zero conflict."""
    return [core.record_id for core in cores
            if not core.has_unresolved and core.pressure < ZERO_CONFLICT_PRESSURE
            and core.severity == 'info']


def _summary(cores: Sequence[CoreEvaluation], ranking: Mapping[str, int]) -> dict[str, Any]:
    outcomes: dict[str, int] = {}
    severities: dict[str, int] = {}
    for core in cores:
        outcomes[core.outcome] = outcomes.get(core.outcome, 0) + 1
        severities[core.severity] = severities.get(core.severity, 0) + 1
    pressures = [core.pressure for core in cores]
    return {
        'core_count': len(cores),
        'outcomes': outcomes,
        'severities': severities,
        'unresolved_core_count': sum(core.has_unresolved for core in cores),
        'zero_conflict_core_count': len(_zero_conflict_cores(cores)),
        'zero_conflict_record_ids': _zero_conflict_cores(cores),
        'mean_pressure': sum(pressures) / len(pressures) if pressures else 0.0,
        'max_pressure': max(pressures) if pressures else 0.0,
        'ranking': dict(sorted(ranking.items(), key=lambda item: item[1])),
    }


def build_sensitivity_report(records: Sequence[DomainRecord], baseline: MappingScheme,
                             candidates: Sequence[MappingScheme]) -> dict[str, Any]:
    """Build the traceable sensitivity report comparing mapping schemes on the
    same rule version set. Multiple candidate schemes may coexist; each gets a
    pairwise comparison against the baseline without overwriting it."""
    if not records:
        raise ContractError('sensitivity analysis requires at least one record')
    if not candidates:
        raise ContractError('sensitivity analysis requires at least one candidate scheme')
    scheme_ids = [baseline.scheme_id] + [scheme.scheme_id for scheme in candidates]
    if len(set(scheme_ids)) != len(scheme_ids):
        raise ContractError('mapping scheme identifiers must be unique within a report')

    catalog = rule_catalog_fingerprint()
    baseline_cores = evaluate_under_scheme(baseline, records)
    baseline_ranking = rank_cores(baseline_cores)
    baseline_summary = _summary(baseline_cores, baseline_ranking)

    groups: dict[str, list[CoreEvaluation]] = {}
    for core in baseline_cores:
        groups.setdefault(core.rule_version_group, []).append(core)
    group_baseline_ranks = {group: rank_cores(members) for group, members in groups.items()}

    comparisons: list[dict[str, Any]] = []
    for scheme in candidates:
        candidate_cores = evaluate_under_scheme(scheme, records)
        candidate_ranking = rank_cores(candidate_cores)
        candidate_summary = _summary(candidate_cores, candidate_ranking)
        candidate_groups: dict[str, list[CoreEvaluation]] = {}
        for core in candidate_cores:
            candidate_groups.setdefault(core.rule_version_group, []).append(core)
        group_candidate_ranks = {group: rank_cores(members)
                                 for group, members in candidate_groups.items()}

        baseline_by_id = {core.record_id: core for core in baseline_cores}
        candidate_by_id = {core.record_id: core for core in candidate_cores}
        if set(baseline_by_id) != set(candidate_by_id):
            raise ContractError('candidate scheme produced a different set of conflict cores')

        core_comparisons = [
            _core_comparison(
                baseline_by_id[record_id], candidate_by_id[record_id],
                baseline_ranking[record_id], candidate_ranking[record_id],
                group_baseline_ranks[baseline_by_id[record_id].rule_version_group][record_id],
                group_candidate_ranks[candidate_by_id[record_id].rule_version_group][record_id],
            )
            for record_id in sorted(baseline_by_id)
        ]
        status_counts: dict[str, int] = {}
        for item in core_comparisons:
            status_counts[item['status']] = status_counts.get(item['status'], 0) + 1

        group_comparisons = []
        for group in sorted(groups):
            left_ids = {core.record_id for core in groups[group]}
            right_ids = {core.record_id for core in candidate_groups.get(group, [])}
            group_comparisons.append({
                'rule_version_group': group,
                'core_count': len(left_ids),
                'same_core_set': left_ids == right_ids,
                'rank_correlation': _spearman_rho(group_baseline_ranks[group],
                                                  group_candidate_ranks.get(group, {})),
            })

        comparisons.append({
            'candidate_scheme': scheme.as_dict(),
            'candidate_scheme_fingerprint': scheme.fingerprint,
            'candidate_summary': candidate_summary,
            'status_counts': {status: status_counts.get(status, 0) for status in CORE_STATUSES},
            'overall_rank_correlation': _spearman_rho(baseline_ranking, candidate_ranking),
            'ranking': {'baseline': baseline_ranking, 'candidate': candidate_ranking},
            'rule_version_groups': group_comparisons,
            'cores': core_comparisons,
        })

    return {
        'report_kind': 'mapping_sensitivity',
        'rule_catalog_fingerprint': catalog,
        'baseline_scheme': baseline.as_dict(),
        'baseline_scheme_fingerprint': baseline.fingerprint,
        'baseline_summary': baseline_summary,
        'record_count': len(records),
        'record_fingerprints': [
            stable_hash({'record_id': record.record_id, 'payload': record.payload})
            for record in records
        ],
        'comparisons': comparisons,
    }

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable, Mapping

@dataclass(frozen=True)
class DomainSignal:
    code: str
    score: float
    severity: str
    evidence: dict[str, Any]

def number(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    try:
        value = float(payload.get(key, default))
    except (TypeError, ValueError):
        return default
    return default if value != value or value in (float('inf'), float('-inf')) else value

def ratio(payload: Mapping[str, Any], key: str, default: float = 0.0) -> float:
    value = number(payload, key, default)
    if value > 1.0:
        value /= 100.0
    return max(0.0, min(1.0, value))

def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def conflict_pressure(payload: Mapping[str, Any]) -> DomainSignal:
    clauses = max(1.0, number(payload, 'clause_count', 1.0))
    unresolved = max(0.0, number(payload, 'unresolved_terms'))
    exceptions = max(0.0, number(payload, 'exception_count'))
    compatibility = ratio(payload, 'compatibility_rate')
    priority = min(1.0, number(payload, 'priority_level') / 5.0)
    scope = str(payload.get('applicability_tier', '')).strip().lower()
    obligation = str(payload.get('obligation_mode', '')).strip().lower()
    semantic_gap = min(1.0, unresolved / clauses)
    exception_load = min(1.0, exceptions / clauses)
    categorical_conflict = 0.2 if obligation in {'must','prohibit','mandatory'} and scope in {'global','strict','high'} else 0.0
    pressure = clamp(semantic_gap * .32 + exception_load * .18 + (1-compatibility) * .30 + priority * .12 + categorical_conflict)
    severity = 'critical' if pressure >= .68 else 'warning' if pressure >= .36 else 'info'
    return DomainSignal('conflict_pressure', pressure, severity, {'semantic_gap': semantic_gap, 'exception_load': exception_load, 'compatibility': compatibility, 'categorical_conflict': categorical_conflict})

def peer_distribution(records: Iterable[Any], group_field: str = 'jurisdiction') -> dict[str, Any]:
    groups = {}
    for record in records:
        payload = getattr(record, 'payload', record); groups.setdefault(str(payload.get(group_field, 'unknown')), []).append(conflict_pressure(payload).score)
    peaks = {key: max(values) for key, values in groups.items()}
    return {'groups': peaks, 'count': sum(len(v) for v in groups.values()), 'critical_components': sum(v >= .68 for v in peaks.values()), 'average': sum(sum(v) for v in groups.values()) / max(1, sum(len(v) for v in groups.values()))}

def augment_context(record: Any, repository: Any) -> dict[str, Any]:
    signal = conflict_pressure(record.payload); peers = peer_distribution(repository.list_records())
    return {'domain_signal': signal.score, 'domain_severity': signal.severity, 'critical_components': peers['critical_components'], 'peer_average': peers['average']}

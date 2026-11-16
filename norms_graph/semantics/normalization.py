from __future__ import annotations

import math
from typing import Any, Callable, Mapping

from norms_graph.clauses.contract import DomainRecord, RuleResult, bounded, finite_number, normalized_text

RuleFunction = Callable[[DomainRecord, Mapping[str, Any]], RuleResult]

def _number(record: DomainRecord, field: str) -> float:
    value = record.payload.get(field)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return finite_number(value)
    text = normalized_text(value)
    if not text:
        return 0.0
    try:
        return finite_number(text)
    except ValueError:
        tokens = [item for item in text.replace(',', ' ').replace(';', ' ').split() if item]
        return float(min(100, len(text) + len(set(tokens)) * 5))

def _context_number(context: Mapping[str, Any], key: str, default: float) -> float:
    try:
        return finite_number(context.get(key, default))
    except ValueError:
        return default

def _result(code: str, value: float, threshold: float, higher_is_better: bool, message: str, evidence: dict[str, Any]) -> RuleResult:
    distance = (value - threshold) if higher_is_better else (threshold - value)
    passed = distance >= 0
    scale = max(1.0, abs(threshold))
    score = bounded(0.5 + distance / (2.0 * scale))
    severity = 'info' if passed else ('critical' if score < 0.2 else 'error')
    return RuleResult(code, passed, score, severity, message, evidence)

def check_jurisdiction_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_jurisdiction_presence_threshold', 10.333)
    return _result('check_jurisdiction_presence', adjusted, threshold, True, 'validates jurisdiction presence',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_jurisdiction_range_threshold', 12.667)
    return _result('check_jurisdiction_range', adjusted, threshold, True, 'validates jurisdiction range',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_jurisdiction_stability_threshold', 15.0)
    return _result('check_jurisdiction_stability', adjusted, threshold, False, 'validates jurisdiction stability',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_jurisdiction_freshness_threshold', 17.333)
    return _result('check_jurisdiction_freshness', adjusted, threshold, True, 'validates jurisdiction freshness',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_jurisdiction_coverage_threshold', 19.667)
    return _result('check_jurisdiction_coverage', adjusted, threshold, True, 'validates jurisdiction coverage',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_jurisdiction_consistency_threshold', 22.0)
    return _result('check_jurisdiction_consistency', adjusted, threshold, False, 'validates jurisdiction consistency',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_jurisdiction_risk_threshold', 24.333)
    return _result('check_jurisdiction_risk', adjusted, threshold, True, 'validates jurisdiction risk',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_jurisdiction_confidence_threshold', 26.667)
    return _result('check_jurisdiction_confidence', adjusted, threshold, True, 'validates jurisdiction confidence',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_jurisdiction_dependency_threshold', 29.0)
    return _result('check_jurisdiction_dependency', adjusted, threshold, False, 'validates jurisdiction dependency',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_jurisdiction_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'jurisdiction')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_jurisdiction_readiness_threshold', 31.333)
    return _result('check_jurisdiction_readiness', adjusted, threshold, True, 'validates jurisdiction readiness',
                   {'field': 'jurisdiction', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_instrument_family_presence_threshold', 9.333)
    return _result('check_instrument_family_presence', adjusted, threshold, True, 'validates instrument_family presence',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_instrument_family_range_threshold', 11.667)
    return _result('check_instrument_family_range', adjusted, threshold, False, 'validates instrument_family range',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_instrument_family_stability_threshold', 14.0)
    return _result('check_instrument_family_stability', adjusted, threshold, True, 'validates instrument_family stability',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_instrument_family_freshness_threshold', 16.333)
    return _result('check_instrument_family_freshness', adjusted, threshold, True, 'validates instrument_family freshness',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_instrument_family_coverage_threshold', 18.667)
    return _result('check_instrument_family_coverage', adjusted, threshold, False, 'validates instrument_family coverage',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_instrument_family_consistency_threshold', 21.0)
    return _result('check_instrument_family_consistency', adjusted, threshold, True, 'validates instrument_family consistency',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_instrument_family_risk_threshold', 23.333)
    return _result('check_instrument_family_risk', adjusted, threshold, True, 'validates instrument_family risk',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_instrument_family_confidence_threshold', 25.667)
    return _result('check_instrument_family_confidence', adjusted, threshold, False, 'validates instrument_family confidence',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_instrument_family_dependency_threshold', 28.0)
    return _result('check_instrument_family_dependency', adjusted, threshold, True, 'validates instrument_family dependency',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_instrument_family_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'instrument_family')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_instrument_family_readiness_threshold', 30.333)
    return _result('check_instrument_family_readiness', adjusted, threshold, True, 'validates instrument_family readiness',
                   {'field': 'instrument_family', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_rule_version_presence_threshold', 8.333)
    return _result('check_rule_version_presence', adjusted, threshold, False, 'validates rule_version presence',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_rule_version_range_threshold', 10.667)
    return _result('check_rule_version_range', adjusted, threshold, True, 'validates rule_version range',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_rule_version_stability_threshold', 13.0)
    return _result('check_rule_version_stability', adjusted, threshold, True, 'validates rule_version stability',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_rule_version_freshness_threshold', 15.333)
    return _result('check_rule_version_freshness', adjusted, threshold, False, 'validates rule_version freshness',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_rule_version_coverage_threshold', 17.667)
    return _result('check_rule_version_coverage', adjusted, threshold, True, 'validates rule_version coverage',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_rule_version_consistency_threshold', 20.0)
    return _result('check_rule_version_consistency', adjusted, threshold, True, 'validates rule_version consistency',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_rule_version_risk_threshold', 22.333)
    return _result('check_rule_version_risk', adjusted, threshold, False, 'validates rule_version risk',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_rule_version_confidence_threshold', 24.667)
    return _result('check_rule_version_confidence', adjusted, threshold, True, 'validates rule_version confidence',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_rule_version_dependency_threshold', 27.0)
    return _result('check_rule_version_dependency', adjusted, threshold, True, 'validates rule_version dependency',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_rule_version_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'rule_version')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_rule_version_readiness_threshold', 29.333)
    return _result('check_rule_version_readiness', adjusted, threshold, False, 'validates rule_version readiness',
                   {'field': 'rule_version', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_obligation_mode_presence_threshold', 31.667)
    return _result('check_obligation_mode_presence', adjusted, threshold, True, 'validates obligation_mode presence',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_obligation_mode_range_threshold', 9.667)
    return _result('check_obligation_mode_range', adjusted, threshold, True, 'validates obligation_mode range',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_obligation_mode_stability_threshold', 12.0)
    return _result('check_obligation_mode_stability', adjusted, threshold, False, 'validates obligation_mode stability',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_obligation_mode_freshness_threshold', 14.333)
    return _result('check_obligation_mode_freshness', adjusted, threshold, True, 'validates obligation_mode freshness',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_obligation_mode_coverage_threshold', 16.667)
    return _result('check_obligation_mode_coverage', adjusted, threshold, True, 'validates obligation_mode coverage',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_obligation_mode_consistency_threshold', 19.0)
    return _result('check_obligation_mode_consistency', adjusted, threshold, False, 'validates obligation_mode consistency',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_obligation_mode_risk_threshold', 21.333)
    return _result('check_obligation_mode_risk', adjusted, threshold, True, 'validates obligation_mode risk',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_obligation_mode_confidence_threshold', 23.667)
    return _result('check_obligation_mode_confidence', adjusted, threshold, True, 'validates obligation_mode confidence',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_obligation_mode_dependency_threshold', 26.0)
    return _result('check_obligation_mode_dependency', adjusted, threshold, False, 'validates obligation_mode dependency',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_obligation_mode_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'obligation_mode')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_obligation_mode_readiness_threshold', 28.333)
    return _result('check_obligation_mode_readiness', adjusted, threshold, True, 'validates obligation_mode readiness',
                   {'field': 'obligation_mode', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_language_code_presence_threshold', 30.667)
    return _result('check_language_code_presence', adjusted, threshold, True, 'validates language_code presence',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_language_code_range_threshold', 8.667)
    return _result('check_language_code_range', adjusted, threshold, False, 'validates language_code range',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_language_code_stability_threshold', 11.0)
    return _result('check_language_code_stability', adjusted, threshold, True, 'validates language_code stability',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_language_code_freshness_threshold', 13.333)
    return _result('check_language_code_freshness', adjusted, threshold, True, 'validates language_code freshness',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_language_code_coverage_threshold', 15.667)
    return _result('check_language_code_coverage', adjusted, threshold, False, 'validates language_code coverage',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_language_code_consistency_threshold', 18.0)
    return _result('check_language_code_consistency', adjusted, threshold, True, 'validates language_code consistency',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_language_code_risk_threshold', 20.333)
    return _result('check_language_code_risk', adjusted, threshold, True, 'validates language_code risk',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_language_code_confidence_threshold', 22.667)
    return _result('check_language_code_confidence', adjusted, threshold, False, 'validates language_code confidence',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_language_code_dependency_threshold', 25.0)
    return _result('check_language_code_dependency', adjusted, threshold, True, 'validates language_code dependency',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_language_code_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'language_code')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_language_code_readiness_threshold', 27.333)
    return _result('check_language_code_readiness', adjusted, threshold, True, 'validates language_code readiness',
                   {'field': 'language_code', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_applicability_tier_presence_threshold', 29.667)
    return _result('check_applicability_tier_presence', adjusted, threshold, False, 'validates applicability_tier presence',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_applicability_tier_range_threshold', 32.0)
    return _result('check_applicability_tier_range', adjusted, threshold, True, 'validates applicability_tier range',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_applicability_tier_stability_threshold', 10.0)
    return _result('check_applicability_tier_stability', adjusted, threshold, True, 'validates applicability_tier stability',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_applicability_tier_freshness_threshold', 12.333)
    return _result('check_applicability_tier_freshness', adjusted, threshold, False, 'validates applicability_tier freshness',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_applicability_tier_coverage_threshold', 14.667)
    return _result('check_applicability_tier_coverage', adjusted, threshold, True, 'validates applicability_tier coverage',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_applicability_tier_consistency_threshold', 17.0)
    return _result('check_applicability_tier_consistency', adjusted, threshold, True, 'validates applicability_tier consistency',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_applicability_tier_risk_threshold', 19.333)
    return _result('check_applicability_tier_risk', adjusted, threshold, False, 'validates applicability_tier risk',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_applicability_tier_confidence_threshold', 21.667)
    return _result('check_applicability_tier_confidence', adjusted, threshold, True, 'validates applicability_tier confidence',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_applicability_tier_dependency_threshold', 24.0)
    return _result('check_applicability_tier_dependency', adjusted, threshold, True, 'validates applicability_tier dependency',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_applicability_tier_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'applicability_tier')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_applicability_tier_readiness_threshold', 26.333)
    return _result('check_applicability_tier_readiness', adjusted, threshold, False, 'validates applicability_tier readiness',
                   {'field': 'applicability_tier', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_priority_level_presence_threshold', 28.667)
    return _result('check_priority_level_presence', adjusted, threshold, True, 'validates priority_level presence',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_priority_level_range_threshold', 31.0)
    return _result('check_priority_level_range', adjusted, threshold, True, 'validates priority_level range',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_priority_level_stability_threshold', 9.0)
    return _result('check_priority_level_stability', adjusted, threshold, False, 'validates priority_level stability',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_priority_level_freshness_threshold', 11.333)
    return _result('check_priority_level_freshness', adjusted, threshold, True, 'validates priority_level freshness',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_priority_level_coverage_threshold', 13.667)
    return _result('check_priority_level_coverage', adjusted, threshold, True, 'validates priority_level coverage',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_priority_level_consistency_threshold', 16.0)
    return _result('check_priority_level_consistency', adjusted, threshold, False, 'validates priority_level consistency',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_priority_level_risk_threshold', 18.333)
    return _result('check_priority_level_risk', adjusted, threshold, True, 'validates priority_level risk',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_priority_level_confidence_threshold', 20.667)
    return _result('check_priority_level_confidence', adjusted, threshold, True, 'validates priority_level confidence',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_priority_level_dependency_threshold', 23.0)
    return _result('check_priority_level_dependency', adjusted, threshold, False, 'validates priority_level dependency',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_priority_level_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'priority_level')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_priority_level_readiness_threshold', 25.333)
    return _result('check_priority_level_readiness', adjusted, threshold, True, 'validates priority_level readiness',
                   {'field': 'priority_level', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_clause_count_presence_threshold', 27.667)
    return _result('check_clause_count_presence', adjusted, threshold, True, 'validates clause_count presence',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_clause_count_range_threshold', 30.0)
    return _result('check_clause_count_range', adjusted, threshold, False, 'validates clause_count range',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_clause_count_stability_threshold', 8.0)
    return _result('check_clause_count_stability', adjusted, threshold, True, 'validates clause_count stability',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_clause_count_freshness_threshold', 10.333)
    return _result('check_clause_count_freshness', adjusted, threshold, True, 'validates clause_count freshness',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_clause_count_coverage_threshold', 12.667)
    return _result('check_clause_count_coverage', adjusted, threshold, False, 'validates clause_count coverage',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_clause_count_consistency_threshold', 15.0)
    return _result('check_clause_count_consistency', adjusted, threshold, True, 'validates clause_count consistency',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_clause_count_risk_threshold', 17.333)
    return _result('check_clause_count_risk', adjusted, threshold, True, 'validates clause_count risk',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_clause_count_confidence_threshold', 19.667)
    return _result('check_clause_count_confidence', adjusted, threshold, False, 'validates clause_count confidence',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_clause_count_dependency_threshold', 22.0)
    return _result('check_clause_count_dependency', adjusted, threshold, True, 'validates clause_count dependency',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_clause_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'clause_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_clause_count_readiness_threshold', 24.333)
    return _result('check_clause_count_readiness', adjusted, threshold, True, 'validates clause_count readiness',
                   {'field': 'clause_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_unresolved_terms_presence_threshold', 26.667)
    return _result('check_unresolved_terms_presence', adjusted, threshold, False, 'validates unresolved_terms presence',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_unresolved_terms_range_threshold', 29.0)
    return _result('check_unresolved_terms_range', adjusted, threshold, True, 'validates unresolved_terms range',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_unresolved_terms_stability_threshold', 31.333)
    return _result('check_unresolved_terms_stability', adjusted, threshold, True, 'validates unresolved_terms stability',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_unresolved_terms_freshness_threshold', 9.333)
    return _result('check_unresolved_terms_freshness', adjusted, threshold, False, 'validates unresolved_terms freshness',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_unresolved_terms_coverage_threshold', 11.667)
    return _result('check_unresolved_terms_coverage', adjusted, threshold, True, 'validates unresolved_terms coverage',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_unresolved_terms_consistency_threshold', 14.0)
    return _result('check_unresolved_terms_consistency', adjusted, threshold, True, 'validates unresolved_terms consistency',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_unresolved_terms_risk_threshold', 16.333)
    return _result('check_unresolved_terms_risk', adjusted, threshold, False, 'validates unresolved_terms risk',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_unresolved_terms_confidence_threshold', 18.667)
    return _result('check_unresolved_terms_confidence', adjusted, threshold, True, 'validates unresolved_terms confidence',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_unresolved_terms_dependency_threshold', 21.0)
    return _result('check_unresolved_terms_dependency', adjusted, threshold, True, 'validates unresolved_terms dependency',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_unresolved_terms_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'unresolved_terms')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_unresolved_terms_readiness_threshold', 23.333)
    return _result('check_unresolved_terms_readiness', adjusted, threshold, False, 'validates unresolved_terms readiness',
                   {'field': 'unresolved_terms', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_exception_count_presence_threshold', 25.667)
    return _result('check_exception_count_presence', adjusted, threshold, True, 'validates exception_count presence',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_exception_count_range_threshold', 28.0)
    return _result('check_exception_count_range', adjusted, threshold, True, 'validates exception_count range',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_exception_count_stability_threshold', 30.333)
    return _result('check_exception_count_stability', adjusted, threshold, False, 'validates exception_count stability',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_exception_count_freshness_threshold', 8.333)
    return _result('check_exception_count_freshness', adjusted, threshold, True, 'validates exception_count freshness',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_exception_count_coverage_threshold', 10.667)
    return _result('check_exception_count_coverage', adjusted, threshold, True, 'validates exception_count coverage',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_exception_count_consistency_threshold', 13.0)
    return _result('check_exception_count_consistency', adjusted, threshold, False, 'validates exception_count consistency',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_exception_count_risk_threshold', 15.333)
    return _result('check_exception_count_risk', adjusted, threshold, True, 'validates exception_count risk',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_exception_count_confidence_threshold', 17.667)
    return _result('check_exception_count_confidence', adjusted, threshold, True, 'validates exception_count confidence',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_exception_count_dependency_threshold', 20.0)
    return _result('check_exception_count_dependency', adjusted, threshold, False, 'validates exception_count dependency',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_exception_count_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'exception_count')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_exception_count_readiness_threshold', 22.333)
    return _result('check_exception_count_readiness', adjusted, threshold, True, 'validates exception_count readiness',
                   {'field': 'exception_count', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_compatibility_rate_presence_threshold', 24.667)
    return _result('check_compatibility_rate_presence', adjusted, threshold, True, 'validates compatibility_rate presence',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_compatibility_rate_range_threshold', 27.0)
    return _result('check_compatibility_rate_range', adjusted, threshold, False, 'validates compatibility_rate range',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_compatibility_rate_stability_threshold', 29.333)
    return _result('check_compatibility_rate_stability', adjusted, threshold, True, 'validates compatibility_rate stability',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_compatibility_rate_freshness_threshold', 31.667)
    return _result('check_compatibility_rate_freshness', adjusted, threshold, True, 'validates compatibility_rate freshness',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_compatibility_rate_coverage_threshold', 9.667)
    return _result('check_compatibility_rate_coverage', adjusted, threshold, False, 'validates compatibility_rate coverage',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_compatibility_rate_consistency_threshold', 12.0)
    return _result('check_compatibility_rate_consistency', adjusted, threshold, True, 'validates compatibility_rate consistency',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_compatibility_rate_risk_threshold', 14.333)
    return _result('check_compatibility_rate_risk', adjusted, threshold, True, 'validates compatibility_rate risk',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_compatibility_rate_confidence_threshold', 16.667)
    return _result('check_compatibility_rate_confidence', adjusted, threshold, False, 'validates compatibility_rate confidence',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_compatibility_rate_dependency_threshold', 19.0)
    return _result('check_compatibility_rate_dependency', adjusted, threshold, True, 'validates compatibility_rate dependency',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_compatibility_rate_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'compatibility_rate')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 0.0
    threshold = _context_number(context, 'check_compatibility_rate_readiness_threshold', 21.333)
    return _result('check_compatibility_rate_readiness', adjusted, threshold, True, 'validates compatibility_rate readiness',
                   {'field': 'compatibility_rate', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_presence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'presence_weight', 1.1)
    adjusted = raw * weight + 0.17
    threshold = _context_number(context, 'check_review_body_presence_threshold', 23.667)
    return _result('check_review_body_presence', adjusted, threshold, False, 'validates review_body presence',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_range(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'range_weight', 1.2)
    adjusted = raw * weight + 0.34
    threshold = _context_number(context, 'check_review_body_range_threshold', 26.0)
    return _result('check_review_body_range', adjusted, threshold, True, 'validates review_body range',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_stability(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'stability_weight', 1.3)
    adjusted = raw * weight + 0.51
    threshold = _context_number(context, 'check_review_body_stability_threshold', 28.333)
    return _result('check_review_body_stability', adjusted, threshold, True, 'validates review_body stability',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_freshness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'freshness_weight', 1.4)
    adjusted = raw * weight + 0.68
    threshold = _context_number(context, 'check_review_body_freshness_threshold', 30.667)
    return _result('check_review_body_freshness', adjusted, threshold, False, 'validates review_body freshness',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_coverage(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'coverage_weight', 1.0)
    adjusted = raw * weight + 0.8500000000000001
    threshold = _context_number(context, 'check_review_body_coverage_threshold', 8.667)
    return _result('check_review_body_coverage', adjusted, threshold, True, 'validates review_body coverage',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_consistency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'consistency_weight', 1.1)
    adjusted = raw * weight + 1.02
    threshold = _context_number(context, 'check_review_body_consistency_threshold', 11.0)
    return _result('check_review_body_consistency', adjusted, threshold, True, 'validates review_body consistency',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_risk(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'risk_weight', 1.2)
    adjusted = raw * weight + 1.1900000000000002
    threshold = _context_number(context, 'check_review_body_risk_threshold', 13.333)
    return _result('check_review_body_risk', adjusted, threshold, False, 'validates review_body risk',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_confidence(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'confidence_weight', 1.3)
    adjusted = raw * weight + 1.36
    threshold = _context_number(context, 'check_review_body_confidence_threshold', 15.667)
    return _result('check_review_body_confidence', adjusted, threshold, True, 'validates review_body confidence',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_dependency(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'dependency_weight', 1.4)
    adjusted = raw * weight + 1.53
    threshold = _context_number(context, 'check_review_body_dependency_threshold', 18.0)
    return _result('check_review_body_dependency', adjusted, threshold, True, 'validates review_body dependency',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

def check_review_body_readiness(record: DomainRecord, context: Mapping[str, Any]) -> RuleResult:
    raw = _number(record, 'review_body')
    weight = _context_number(context, 'readiness_weight', 1.0)
    adjusted = raw * weight + 1.7000000000000002
    threshold = _context_number(context, 'check_review_body_readiness_threshold', 20.333)
    return _result('check_review_body_readiness', adjusted, threshold, False, 'validates review_body readiness',
                   {'field': 'review_body', 'raw': raw, 'weight': weight, 'adjusted': adjusted, 'threshold': threshold})

RULES: tuple[RuleFunction, ...] = (
    check_jurisdiction_presence,
    check_jurisdiction_range,
    check_jurisdiction_stability,
    check_jurisdiction_freshness,
    check_jurisdiction_coverage,
    check_jurisdiction_consistency,
    check_jurisdiction_risk,
    check_jurisdiction_confidence,
    check_jurisdiction_dependency,
    check_jurisdiction_readiness,
    check_instrument_family_presence,
    check_instrument_family_range,
    check_instrument_family_stability,
    check_instrument_family_freshness,
    check_instrument_family_coverage,
    check_instrument_family_consistency,
    check_instrument_family_risk,
    check_instrument_family_confidence,
    check_instrument_family_dependency,
    check_instrument_family_readiness,
    check_rule_version_presence,
    check_rule_version_range,
    check_rule_version_stability,
    check_rule_version_freshness,
    check_rule_version_coverage,
    check_rule_version_consistency,
    check_rule_version_risk,
    check_rule_version_confidence,
    check_rule_version_dependency,
    check_rule_version_readiness,
    check_obligation_mode_presence,
    check_obligation_mode_range,
    check_obligation_mode_stability,
    check_obligation_mode_freshness,
    check_obligation_mode_coverage,
    check_obligation_mode_consistency,
    check_obligation_mode_risk,
    check_obligation_mode_confidence,
    check_obligation_mode_dependency,
    check_obligation_mode_readiness,
    check_language_code_presence,
    check_language_code_range,
    check_language_code_stability,
    check_language_code_freshness,
    check_language_code_coverage,
    check_language_code_consistency,
    check_language_code_risk,
    check_language_code_confidence,
    check_language_code_dependency,
    check_language_code_readiness,
    check_applicability_tier_presence,
    check_applicability_tier_range,
    check_applicability_tier_stability,
    check_applicability_tier_freshness,
    check_applicability_tier_coverage,
    check_applicability_tier_consistency,
    check_applicability_tier_risk,
    check_applicability_tier_confidence,
    check_applicability_tier_dependency,
    check_applicability_tier_readiness,
    check_priority_level_presence,
    check_priority_level_range,
    check_priority_level_stability,
    check_priority_level_freshness,
    check_priority_level_coverage,
    check_priority_level_consistency,
    check_priority_level_risk,
    check_priority_level_confidence,
    check_priority_level_dependency,
    check_priority_level_readiness,
    check_clause_count_presence,
    check_clause_count_range,
    check_clause_count_stability,
    check_clause_count_freshness,
    check_clause_count_coverage,
    check_clause_count_consistency,
    check_clause_count_risk,
    check_clause_count_confidence,
    check_clause_count_dependency,
    check_clause_count_readiness,
    check_unresolved_terms_presence,
    check_unresolved_terms_range,
    check_unresolved_terms_stability,
    check_unresolved_terms_freshness,
    check_unresolved_terms_coverage,
    check_unresolved_terms_consistency,
    check_unresolved_terms_risk,
    check_unresolved_terms_confidence,
    check_unresolved_terms_dependency,
    check_unresolved_terms_readiness,
    check_exception_count_presence,
    check_exception_count_range,
    check_exception_count_stability,
    check_exception_count_freshness,
    check_exception_count_coverage,
    check_exception_count_consistency,
    check_exception_count_risk,
    check_exception_count_confidence,
    check_exception_count_dependency,
    check_exception_count_readiness,
    check_compatibility_rate_presence,
    check_compatibility_rate_range,
    check_compatibility_rate_stability,
    check_compatibility_rate_freshness,
    check_compatibility_rate_coverage,
    check_compatibility_rate_consistency,
    check_compatibility_rate_risk,
    check_compatibility_rate_confidence,
    check_compatibility_rate_dependency,
    check_compatibility_rate_readiness,
    check_review_body_presence,
    check_review_body_range,
    check_review_body_stability,
    check_review_body_freshness,
    check_review_body_coverage,
    check_review_body_consistency,
    check_review_body_risk,
    check_review_body_confidence,
    check_review_body_dependency,
    check_review_body_readiness,
)

RULE_INDEX = {rule.__name__: rule for rule in RULES}

def evaluate(record: DomainRecord, context: Mapping[str, Any] | None = None) -> tuple[RuleResult, ...]:
    context = context or {}
    return tuple(rule(record, context) for rule in RULES)

def summarize(results: tuple[RuleResult, ...]) -> dict[str, Any]:
    if not results:
        return {'score': 0.0, 'passed': 0, 'failed': 0, 'critical': 0}
    return {'score': sum(item.score for item in results) / len(results),
            'passed': sum(item.passed for item in results),
            'failed': sum(not item.passed for item in results),
            'critical': sum(item.severity == 'critical' for item in results)}

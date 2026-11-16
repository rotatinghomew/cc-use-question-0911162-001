from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from norms_graph.clauses.contract import ContractError, DomainRecord, stable_hash
from norms_graph.sensitivity.mapping_scheme import MappingScheme, apply_scheme
from norms_graph.sensitivity.sensitivity_report import (
    CORE_UNRESOLVED, DEFAULT_SCORE_TOLERANCE, ZERO_CONFLICT_PRESSURE,
    build_sensitivity_report, decision_signature, evaluate_under_scheme, rank_cores,
    rule_catalog_fingerprint,
)

SENSITIVITY_FILE = 'sensitivity-report.json'
SENSITIVITY_TOLERANCE_FILE = 'sensitivity-tolerance.json'


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def verify_summary_against_decisions(bundle_root: str | Path) -> list[str]:
    """Cross-check the published summary statistics against the underlying
    decision evidence. Applies to every dossier, including already-published
    bundles that carry no sensitivity report, so legacy dossiers are re-checked
    under their original口径 rather than being exempted."""
    root = Path(bundle_root)
    errors: list[str] = []
    summary_path = root / 'summary.json'
    decisions_path = root / 'decisions.json'
    if not summary_path.is_file() or not decisions_path.is_file():
        return errors
    summary = _load_json(summary_path)
    decisions = _load_json(decisions_path)
    if not isinstance(decisions, list):
        return ['decisions.json must be a list']
    if summary.get('decision_count') != len(decisions):
        errors.append('summary decision_count does not match decisions.json')
    outcomes: dict[str, int] = {}
    for decision in decisions:
        outcomes[decision['outcome']] = outcomes.get(decision['outcome'], 0) + 1
    if summary.get('outcomes') != outcomes:
        errors.append('summary outcomes do not match decisions.json')
    if summary.get('record_count') != summary.get('decision_count'):
        errors.append('summary record_count and decision_count disagree')
    scores = [float(decision['score']) for decision in decisions]
    if scores:
        if abs(summary.get('average_score', 0.0) - sum(scores) / len(scores)) > 1e-9:
            errors.append('summary average_score does not match decisions.json')
        if abs(summary.get('minimum_score', 0.0) - min(scores)) > 1e-9:
            errors.append('summary minimum_score does not match decisions.json')
        if abs(summary.get('maximum_score', 0.0) - max(scores)) > 1e-9:
            errors.append('summary maximum_score does not match decisions.json')
    return errors


def verify_rules_csv_against_decisions(bundle_root: str | Path) -> list[str]:
    """The rules.csv rule rows must reconcile with the rule evidence embedded in
    each decision — dossier statistics cannot drift from the clause evidence."""
    root = Path(bundle_root)
    rules_path = root / 'rules.csv'
    decisions_path = root / 'decisions.json'
    if not rules_path.is_file() or not decisions_path.is_file():
        return []
    import csv
    errors: list[str] = []
    with rules_path.open(encoding='utf-8', newline='') as handle:
        rule_rows = list(csv.DictReader(handle))
    decisions = _load_json(decisions_path)
    expected = sum(len(decision.get('rules', ())) for decision in decisions)
    if len(rule_rows) != expected:
        errors.append('rules.csv row count does not match embedded rule evidence')
    return errors


def _replay_records(report: Mapping[str, Any]) -> list[DomainRecord]:
    """Reconstruct the original DomainRecord objects from the report's embedded
    raw clause evidence. Because both the raw payload and the mapped view are
    embedded, every mapping resolution and decision can be recomputed offline
    without trusting the report's numbers."""
    first_comparison = report['comparisons'][0]
    if not first_comparison['cores']:
        raise ContractError('sensitivity report contains no conflict cores')
    records: list[DomainRecord] = []
    for stored_core in first_comparison['cores']:
        raw = stored_core['baseline']['raw_record']
        records.append(DomainRecord(raw['record_id'], raw['payload'], 'drafted'))
    # Anchor on the stable content fingerprint (id + payload); the DomainRecord
    # fingerprint also contains a wall-clock timestamp and is not replay-stable.
    expected_fingerprints = report['record_fingerprints']
    actual_fingerprints = [
        stable_hash({'record_id': record.record_id, 'payload': record.payload})
        for record in records
    ]
    if actual_fingerprints != expected_fingerprints:
        raise ContractError('sensitivity report record fingerprints are inconsistent')
    return records


def verify_sensitivity_report(report: Mapping[str, Any],
                              decisions: Sequence[Mapping[str, Any]] | None = None,
                              score_tolerance: float = DEFAULT_SCORE_TOLERANCE) -> list[str]:
    """Recompute every claim in the sensitivity report from its embedded evidence.

    ``decisions`` is the published dossier's decisions.json; when supplied, the
    baseline conflict cores are reconciled against the original published口径.
    """
    errors: list[str] = []
    if report.get('report_kind') != 'mapping_sensitivity':
        return ['sensitivity report has unexpected report_kind']
    if report.get('rule_catalog_fingerprint') != rule_catalog_fingerprint():
        errors.append('rule catalog fingerprint does not match the current engine')

    baseline = MappingScheme.from_dict(report['baseline_scheme'])
    if baseline.fingerprint != report['baseline_scheme_fingerprint']:
        errors.append('baseline scheme fingerprint mismatch')

    records = _replay_records(report)
    rebuilt = build_sensitivity_report(
        records, baseline,
        [MappingScheme.from_dict(item['candidate_scheme']) for item in report['comparisons']],
    )

    if rebuilt['baseline_summary'] != report['baseline_summary']:
        errors.append('baseline summary cannot be reproduced from embedded evidence')

    # Missing evidence must never be counted as zero conflict. This invariant
    # is enforced for the baseline and, below, for every candidate scheme.
    zero_ids = set(report['baseline_summary'].get('zero_conflict_record_ids', []))
    for core in evaluate_under_scheme(baseline, records):
        if core.record_id in zero_ids and core.has_unresolved:
            errors.append(f'unresolved core {core.record_id} is counted as zero conflict')
        if not core.has_unresolved and core.pressure < ZERO_CONFLICT_PRESSURE \
                and core.severity == 'info' and core.record_id not in zero_ids:
            errors.append(f'zero-conflict core {core.record_id} missing from summary')

    if len(rebuilt['comparisons']) != len(report['comparisons']):
        errors.append('comparison count cannot be reproduced')
        return errors

    for rebuilt_comparison, stored_comparison in zip(rebuilt['comparisons'], report['comparisons']):
        candidate = MappingScheme.from_dict(stored_comparison['candidate_scheme'])
        if candidate.fingerprint != stored_comparison['candidate_scheme_fingerprint']:
            errors.append('candidate scheme fingerprint mismatch')
        # The "missing is not zero conflict" invariant must also hold per candidate.
        candidate_zero = set(
            stored_comparison.get('candidate_summary', {}).get('zero_conflict_record_ids', []))
        for core in evaluate_under_scheme(candidate, records):
            if core.record_id in candidate_zero and core.has_unresolved:
                errors.append(
                    f"unresolved core {core.record_id} counted as zero conflict under candidate "
                    f"{candidate.scheme_id}")
        if rebuilt_comparison['status_counts'] != stored_comparison['status_counts']:
            errors.append('conflict core status counts cannot be reproduced')
        if rebuilt_comparison['overall_rank_correlation'] != stored_comparison['overall_rank_correlation']:
            errors.append('overall rank correlation cannot be reproduced')
        rebuilt_cores = {item['record_id']: item for item in rebuilt_comparison['cores']}
        for stored_core in stored_comparison['cores']:
            rebuilt_core = rebuilt_cores.get(stored_core['record_id'])
            if rebuilt_core is None:
                errors.append(f"core {stored_core['record_id']} missing from recomputation")
                continue
            if rebuilt_core['status'] != stored_core['status']:
                errors.append(f"core {stored_core['record_id']} status cannot be reproduced")
            if rebuilt_core['ranking'] != stored_core['ranking']:
                errors.append(f"core {stored_core['record_id']} ranking cannot be reproduced")
            for side in ('baseline', 'candidate'):
                stored_side = stored_core[side]
                rebuilt_side = rebuilt_core[side]
                if abs(stored_side['pressure'] - rebuilt_side['pressure']) > 1e-12:
                    errors.append(f"core {stored_core['record_id']} {side} pressure cannot be reproduced")
                if stored_side['has_unresolved'] != rebuilt_side['has_unresolved'] or \
                        stored_side['unresolved_fields'] != rebuilt_side['unresolved_fields']:
                    errors.append(f"core {stored_core['record_id']} {side} unresolved flags cannot be reproduced")
                if stored_side['outcome'] != rebuilt_side['outcome']:
                    errors.append(f"core {stored_core['record_id']} {side} outcome cannot be reproduced")
                if abs(stored_side['decision_score'] - rebuilt_side['decision_score']) > score_tolerance:
                    errors.append(f"core {stored_core['record_id']} {side} decision score cannot be reproduced")
                # Embedded raw evidence must re-resolve identically under the scheme.
                scheme = baseline if side == 'baseline' else candidate
                raw = DomainRecord(stored_side['raw_record']['record_id'],
                                   stored_side['raw_record']['payload'], 'drafted')
                replayed_view = apply_scheme(scheme, raw)
                if replayed_view.view_fingerprint != stored_side['view']['view_fingerprint']:
                    errors.append(f"core {stored_core['record_id']} {side} view fingerprint cannot be reproduced")
                if replayed_view.unresolved_fields != tuple(stored_side['unresolved_fields']):
                    errors.append(f"core {stored_core['record_id']} {side} unresolved fields cannot be reproduced")

    # Reconcile baseline cores with the originally published dossier decisions.
    if decisions is not None:
        published = {decision['record_id']: decision for decision in decisions}
        baseline_cores = evaluate_under_scheme(baseline, records)
        if set(published) != {core.record_id for core in baseline_cores}:
            errors.append('published dossier covers a different set of records than the sensitivity baseline')
        else:
            for core in baseline_cores:
                published_decision = published[core.record_id]
                if published_decision['outcome'] != core.outcome:
                    errors.append(f"baseline core {core.record_id} outcome diverges from published dossier")
                if abs(float(published_decision['score']) - core.decision_score) > score_tolerance:
                    errors.append(f"baseline core {core.record_id} score diverges from published dossier")
                signature = decision_signature(core.decision)
                published_signature = dict(published_decision)
                published_signature.pop('decided_at', None)
                if signature != published_signature:
                    errors.append(f"baseline core {core.record_id} rule evidence diverges from published dossier")
    return errors


def verify_sensitivity_bundle(bundle_root: str | Path) -> list[str]:
    """Full verification entry used by the CLI: dossier consistency plus, when
    present, replay of the sensitivity report against the published evidence."""
    root = Path(bundle_root)
    errors = verify_summary_against_decisions(root)
    errors.extend(verify_rules_csv_against_decisions(root))
    report_path = root / SENSITIVITY_FILE
    if not report_path.is_file():
        return errors
    report = _load_json(report_path)
    decisions_path = root / 'decisions.json'
    decisions = _load_json(decisions_path) if decisions_path.is_file() else None
    tolerance = DEFAULT_SCORE_TOLERANCE
    tolerance_path = root / SENSITIVITY_TOLERANCE_FILE
    if tolerance_path.is_file():
        tolerance = float(_load_json(tolerance_path).get('score_tolerance', tolerance))
    errors.extend(verify_sensitivity_report(report, decisions, tolerance))
    return errors

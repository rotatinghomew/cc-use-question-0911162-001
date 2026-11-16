from __future__ import annotations

import unittest

from norms_graph.clauses.contract import ContractError, DomainRecord
from norms_graph.semantics.scope_bridge import canonical_term
from norms_graph.sensitivity.mapping_scheme import MappingScheme
from norms_graph.sensitivity.sensitivity_report import (
    CORE_RANKING_ONLY, CORE_SUBSTANTIVE, CORE_UNCHANGED, CORE_UNRESOLVED,
    build_sensitivity_report, evaluate_under_scheme, rank_cores,
    rule_catalog_fingerprint,
)


def make_record(record_id: str, **overrides) -> DomainRecord:
    payload = {
        'jurisdiction': 'eu', 'instrument_family': 'ai_act', 'rule_version': 'rv_alpha',
        'obligation_mode': 'advisory', 'language_code': 'en', 'applicability_tier': 'low',
        'priority_level': 2.0, 'clause_count': 10.0, 'unresolved_terms': 1.0,
        'exception_count': 1.0, 'compatibility_rate': 0.9, 'review_body': 'board_a',
    }
    payload.update(overrides)
    return DomainRecord(record_id, payload, 'drafted')


def vocabulary(records):
    terms = set()
    for record in records:
        for value in record.payload.values():
            if isinstance(value, str):
                terms.add(canonical_term(value))
    return frozenset(terms)


class SensitivityReportTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            make_record('norm_clause-001', rule_version='rv_alpha', unresolved_terms=1.0),
            make_record('norm_clause-002', rule_version='rv_alpha', unresolved_terms=2.0,
                        review_body='board_b'),
            make_record('norm_clause-003', rule_version='rv_beta', jurisdiction='us',
                        review_body='board_c'),
        ]
        self.baseline = MappingScheme('baseline', {}, vocabulary(self.records))

    def test_catalog_fingerprint_is_stable(self):
        self.assertEqual(rule_catalog_fingerprint(), rule_catalog_fingerprint())
        self.assertEqual(len(rule_catalog_fingerprint()), 24)

    def test_identical_schemes_leave_every_core_unchanged(self):
        report = build_sensitivity_report(self.records, self.baseline, [
            MappingScheme('candidate-copy', {}, vocabulary(self.records)),
        ])
        comparison = report['comparisons'][0]
        self.assertEqual(comparison['status_counts'][CORE_UNCHANGED], len(self.records))
        self.assertEqual(comparison['overall_rank_correlation'], 1.0)

    def test_comparison_is_partitioned_by_rule_version(self):
        report = build_sensitivity_report(self.records, self.baseline, [
            MappingScheme('candidate-copy', {}, vocabulary(self.records)),
        ])
        groups = {g['rule_version_group']: g for g in report['comparisons'][0]['rule_version_groups']}
        self.assertEqual(set(groups), {'rv_alpha', 'rv_beta'})
        self.assertTrue(all(g['same_core_set'] for g in groups.values()))

    def test_unresolved_terms_are_flagged_and_not_zero_conflict(self):
        # Vocabulary omits only the review_body tokens used by 001/002, while
        # board_c (used by 003) stays resolvable.
        partial_vocab = vocabulary(self.records) - {'board_a', 'board_b'}
        candidate = MappingScheme('partial', {}, partial_vocab)
        report = build_sensitivity_report(self.records, self.baseline, [candidate])
        comparison = report['comparisons'][0]
        unresolved_ids = {
            core['record_id'] for core in comparison['cores']
            if core['status'] == CORE_UNRESOLVED
        }
        self.assertEqual(unresolved_ids, {'norm_clause-001', 'norm_clause-002'})
        # The invariant is per-scheme: a core unresolved under a scheme must not
        # appear in THAT scheme's zero-conflict list. Under the fully-resolved
        # baseline these same cores may legitimately be zero conflict, and that
        # is preserved (missing evidence only blocks the claim where it is missing).
        candidate_zero = set(
            report['comparisons'][0]['candidate_summary']['zero_conflict_record_ids'])
        self.assertFalse(unresolved_ids & candidate_zero)
        # The candidate summary must explicitly count the indeterminate cores.
        self.assertEqual(
            report['comparisons'][0]['candidate_summary']['unresolved_core_count'], 2)
        # And every indeterminate core carries its unresolved field evidence.
        for core in report['comparisons'][0]['cores']:
            if core['record_id'] in unresolved_ids:
                self.assertTrue(core['candidate']['has_unresolved'])
                self.assertIn('review_body', core['candidate']['unresolved_fields'])
                self.assertTrue(core['candidate']['view']['payload']['review_body'])

    def test_substantive_change_when_severity_crosses_threshold(self):
        records = [r.with_payload({'obligation_mode': 'guidance_only',
                                   'applicability_tier': 'narrow_scope',
                                   'unresolved_terms': 3.0})
                   if r.record_id == 'norm_clause-001' else r for r in self.records]
        baseline = MappingScheme('baseline', {}, vocabulary(records))
        candidate = MappingScheme(
            'escalate', {'guidance_only': 'mandatory', 'narrow_scope': 'strict'},
            (vocabulary(records) - {'guidance_only', 'narrow_scope'}) | {'mandatory', 'strict'})
        report = build_sensitivity_report(records, baseline, [candidate])
        statuses = {c['record_id']: c['status'] for c in report['comparisons'][0]['cores']}
        self.assertEqual(statuses['norm_clause-001'], CORE_SUBSTANTIVE)
        core = next(c for c in report['comparisons'][0]['cores']
                    if c['record_id'] == 'norm_clause-001')
        self.assertEqual(core['baseline']['severity'], 'info')
        self.assertEqual(core['candidate']['severity'], 'warning')

    def test_ranking_only_change_preserves_severity(self):
        records = [r.with_payload({'obligation_mode': 'guidance_only',
                                   'applicability_tier': 'narrow_scope'})
                   if r.record_id == 'norm_clause-001' else r for r in self.records]
        baseline = MappingScheme('baseline', {}, vocabulary(records))
        candidate = MappingScheme(
            'escalate', {'guidance_only': 'mandatory', 'narrow_scope': 'strict'},
            (vocabulary(records) - {'guidance_only', 'narrow_scope'}) | {'mandatory', 'strict'})
        report = build_sensitivity_report(records, baseline, [candidate])
        comparison = report['comparisons'][0]
        target = next(c for c in comparison['cores'] if c['record_id'] == 'norm_clause-001')
        self.assertEqual(target['status'], CORE_RANKING_ONLY)
        self.assertLess(comparison['overall_rank_correlation'], 1.0)

    def test_report_embeds_raw_and_mapped_evidence(self):
        report = build_sensitivity_report(self.records, self.baseline, [
            MappingScheme('candidate-copy', {}, vocabulary(self.records)),
        ])
        core = report['comparisons'][0]['cores'][0]
        self.assertEqual(core['baseline']['raw_record']['payload']['rule_version'], 'rv_alpha')
        self.assertIn('view_fingerprint', core['baseline']['view'])
        self.assertIn('decision_signature', core['baseline'])

    def test_rank_cores_are_deterministic_and_total(self):
        cores = evaluate_under_scheme(self.baseline, self.records)
        first = rank_cores(cores)
        second = rank_cores(cores)
        self.assertEqual(first, second)
        self.assertEqual(set(first.values()), set(range(1, len(cores) + 1)))

    def test_duplicate_scheme_ids_are_rejected(self):
        with self.assertRaisesRegex(ContractError, 'unique'):
            build_sensitivity_report(self.records, self.baseline, [
                MappingScheme('baseline', {}, vocabulary(self.records)),
            ])

    def test_empty_inputs_are_rejected(self):
        with self.assertRaisesRegex(ContractError, 'at least one record'):
            build_sensitivity_report([], self.baseline, [self.baseline])
        with self.assertRaisesRegex(ContractError, 'at least one candidate'):
            build_sensitivity_report(self.records, self.baseline, [])


if __name__ == '__main__':
    unittest.main()

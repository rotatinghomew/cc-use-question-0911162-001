from __future__ import annotations

import unittest

from norms_graph.clauses.contract import ContractError, DomainRecord
from norms_graph.sensitivity.mapping_scheme import (
    MappingScheme, RESOLUTION_NUMERIC, RESOLUTION_RESOLVED, RESOLUTION_UNRESOLVED,
    apply_scheme, resolve_field,
)


def make_record() -> DomainRecord:
    return DomainRecord('norm_clause-s01', {
        'jurisdiction': 'United Kingdom',
        'instrument_family': 'ai_act',
        'rule_version': 'rv_alpha',
        'obligation_mode': 2,
        'clause_count': 10.0,
    }, 'drafted')


class MappingSchemeTests(unittest.TestCase):
    def test_numeric_values_pass_through(self):
        scheme = MappingScheme('s', {}, frozenset())
        resolution = resolve_field(scheme, 'obligation_mode', 2)
        self.assertEqual(resolution.status, RESOLUTION_NUMERIC)
        self.assertEqual(resolution.resolved_value, 2)
        self.assertEqual(resolution.confidence, 1.0)

    def test_alias_resolves_to_canonical_concept(self):
        scheme = MappingScheme('s', {'united_kingdom': 'eu'}, frozenset({'eu', 'ai_act'}))
        resolution = resolve_field(scheme, 'jurisdiction', 'United Kingdom')
        self.assertEqual(resolution.status, RESOLUTION_RESOLVED)
        self.assertEqual(resolution.resolved_value, 'eu')

    def test_vocabulary_match_resolves_without_alias(self):
        scheme = MappingScheme('s', {}, frozenset({'ai_act'}))
        resolution = resolve_field(scheme, 'instrument_family', 'ai_act')
        self.assertEqual(resolution.status, RESOLUTION_RESOLVED)
        self.assertEqual(resolution.resolved_value, 'ai_act')

    def test_unknown_term_is_unresolved_not_zero(self):
        scheme = MappingScheme('s', {}, frozenset({'ai_act'}))
        resolution = resolve_field(scheme, 'jurisdiction', 'atlantis')
        self.assertEqual(resolution.status, RESOLUTION_UNRESOLVED)
        # The raw term is preserved as evidence; it is never coerced to zero.
        self.assertEqual(resolution.resolved_value, 'atlantis')
        self.assertEqual(resolution.confidence, 0.0)

    def test_alias_target_outside_vocabulary_is_unresolved(self):
        scheme = MappingScheme('s', {'united_kingdom': 'eu'}, frozenset({'ai_act'}))
        resolution = resolve_field(scheme, 'jurisdiction', 'United Kingdom')
        self.assertEqual(resolution.status, RESOLUTION_UNRESOLVED)
        self.assertIn('not_in_vocabulary', resolution.reason)

    def test_apply_scheme_preserves_unresolved_raw_evidence(self):
        scheme = MappingScheme('s', {}, frozenset({'ai_act', 'rv_alpha'}))
        view = apply_scheme(scheme, make_record())
        self.assertIn('jurisdiction', view.unresolved_fields)
        # Original raw text survives in the mapped payload.
        self.assertEqual(view.payload['jurisdiction'], 'United Kingdom')
        self.assertEqual(view.payload['instrument_family'], 'ai_act')
        self.assertEqual(view.payload['obligation_mode'], 2)

    def test_scheme_fingerprint_is_stable_and_distinct(self):
        first = MappingScheme('s', {'a': 'b'}, frozenset({'b'}))
        second = MappingScheme('s', {'a': 'b'}, frozenset({'b'}))
        third = MappingScheme('s', {'a': 'c'}, frozenset({'c'}))
        self.assertEqual(first.fingerprint, second.fingerprint)
        self.assertNotEqual(first.fingerprint, third.fingerprint)

    def test_from_dict_validates_shape(self):
        with self.assertRaisesRegex(ContractError, 'scheme_id'):
            MappingScheme.from_dict({'aliases': {}})
        with self.assertRaisesRegex(ContractError, 'aliases must be an object'):
            MappingScheme.from_dict({'scheme_id': 's', 'aliases': []})
        scheme = MappingScheme.from_dict({'scheme_id': 'S 1', 'aliases': {'A': 'B'},
                                          'vocabulary': ['B']})
        self.assertEqual(scheme.scheme_id, 's-1')
        self.assertEqual(scheme.aliases, {'a': 'b'})
        self.assertEqual(set(scheme.vocabulary), {'b'})


if __name__ == '__main__':
    unittest.main()

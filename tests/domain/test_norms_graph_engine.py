from __future__ import annotations

import unittest
from norms_graph.clauses.contract import DomainRecord
from norms_graph.semantics.scope_bridge import conformance_profile, convert_unit, map_field, reuse_matrix


class SemanticBridgeTests(unittest.TestCase):
    def record(self, key, market="my"):
        return DomainRecord(key, {"jurisdiction": market, "instrument_family": "safety", "rule_version": "2",
            "obligation_mode": "metric", "language_code": "ms", "applicability_tier": 2, "priority_level": .8,
            "clause_count": 10, "unresolved_terms": 1, "exception_count": 1, "compatibility_rate": .9, "review_body": "lab"})

    def test_unit_and_alias_mapping(self):
        self.assertAlmostEqual(convert_unit(0, "celsius", "fahrenheit"), 32.0)
        self.assertFalse(map_field("patient_id", "subject_id", "x", {"patient_id": "subject_id"}).lossy)

    def test_clauses_and_reuse(self):
        profile = conformance_profile(self.record("a"))
        self.assertGreater(profile["mapping_coverage"], profile["semantic_loss"])
        self.assertEqual(reuse_matrix([self.record("a"), self.record("b", "th")])["market_count"], 2.0)

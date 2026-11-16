from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from norms_graph.clauses.contract import records_from_fixture, stable_hash
from norms_graph.coordination_hub import run, sensitivity
from norms_graph.console import main as console_main
from norms_graph.publication.coordination_dossier import verify_bundle
from norms_graph.sensitivity.sensitivity_report import build_sensitivity_report
from norms_graph.sensitivity.verification import (
    SENSITIVITY_FILE, verify_sensitivity_bundle, verify_sensitivity_report,
    verify_summary_against_decisions,
)

FIXTURE = Path(__file__).resolve().parents[2] / 'fixtures' / 'sensitivity' / 'scenario.json'
BASELINE = Path(__file__).resolve().parents[2] / 'fixtures' / 'sensitivity' / 'baseline-scheme.json'
HARMONIZED = Path(__file__).resolve().parents[2] / 'fixtures' / 'sensitivity' / 'candidate-scheme-harmonized.json'
PARTIAL = Path(__file__).resolve().parents[2] / 'fixtures' / 'sensitivity' / 'candidate-scheme-partial.json'


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / 'state.sqlite3'
        self.output = self.root / 'dossier'
        run(FIXTURE, self.database, self.output)
        self.result = sensitivity(FIXTURE, BASELINE, [HARMONIZED, PARTIAL], self.output)
        self.report = json.loads((self.output / SENSITIVITY_FILE).read_text(encoding='utf-8'))
        self.decisions = json.loads((self.output / 'decisions.json').read_text(encoding='utf-8'))

    def test_published_sensitivity_bundle_verifies_clean(self):
        self.assertTrue(self.result['ok'], self.result['errors'])
        self.assertEqual(verify_sensitivity_bundle(self.output), [])
        self.assertEqual(verify_bundle(self.output), [])

    def test_baseline_reconciles_with_published_dossier(self):
        # The exact same engine replay must match the originally published decisions.
        errors = verify_sensitivity_report(self.report, self.decisions)
        self.assertEqual(errors, [])

    def test_tampered_pressure_is_detected(self):
        tampered = json.loads(json.dumps(self.report))
        tampered['comparisons'][0]['cores'][0]['candidate']['pressure'] = 0.999
        self.assertTrue(verify_sensitivity_report(tampered, self.decisions))

    def test_tampered_status_is_detected(self):
        tampered = json.loads(json.dumps(self.report))
        tampered['comparisons'][0]['status_counts']['substantive'] += 1
        tampered['comparisons'][0]['status_counts']['unchanged'] -= 1
        self.assertTrue(verify_sensitivity_report(tampered, self.decisions))

    def test_tampered_ranking_is_detected(self):
        tampered = json.loads(json.dumps(self.report))
        tampered['comparisons'][0]['cores'][0]['ranking']['overall']['candidate'] = 99
        self.assertTrue(verify_sensitivity_report(tampered, self.decisions))

    def test_unresolved_core_counted_as_zero_conflict_is_detected(self):
        tampered = json.loads(json.dumps(self.report))
        # Force an unresolved core into the zero-conflict list.
        partial_comparison = next(
            c for c in tampered['comparisons']
            if c['candidate_scheme']['scheme_id'] == 'candidate-partial-glossary')
        unresolved_id = next(
            core['record_id'] for core in partial_comparison['cores']
            if core['status'] == 'unresolved')
        tampered['baseline_summary']['zero_conflict_record_ids'].append(unresolved_id)
        self.assertTrue(verify_sensitivity_report(tampered, self.decisions))

    def test_scheme_fingerprint_tampering_is_detected(self):
        tampered = json.loads(json.dumps(self.report))
        tampered['baseline_scheme_fingerprint'] = '0' * 64
        self.assertTrue(verify_sensitivity_report(tampered, self.decisions))

    def test_catalog_mismatch_is_reported(self):
        tampered = json.loads(json.dumps(self.report))
        tampered['rule_catalog_fingerprint'] = 'deadbeefdeadbeefdeadbeef'
        errors = verify_sensitivity_report(tampered, self.decisions)
        self.assertTrue(any('catalog' in error for error in errors))

    def test_manifest_covers_sensitivity_file(self):
        manifest = json.loads((self.output / 'manifest.json').read_text(encoding='utf-8'))
        self.assertIn(SENSITIVITY_FILE, manifest['files'])
        self.assertEqual(manifest['files'][SENSITIVITY_FILE],
                         stable_hash(self.report))

    def test_summary_statistics_match_decision_evidence(self):
        self.assertEqual(verify_summary_against_decisions(self.output), [])

    def test_summary_tampering_is_caught_by_bundle_verification(self):
        summary_path = self.output / 'summary.json'
        summary = json.loads(summary_path.read_text(encoding='utf-8'))
        summary['decision_count'] = summary['decision_count'] + 1
        summary_path.write_text(json.dumps(summary), encoding='utf-8')
        errors = verify_bundle(self.output)
        self.assertTrue(any('decision_count' in error for error in errors))


class LegacyDossierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / 'state.sqlite3'
        self.output = self.root / 'dossier'
        run(FIXTURE, self.database, self.output)

    def test_legacy_bundle_without_sensitivity_report_still_verifies(self):
        # Already-published dossiers carry no sensitivity-report.json and must
        # keep verifying under their original口径.
        self.assertFalse((self.output / SENSITIVITY_FILE).exists())
        self.assertEqual(verify_bundle(self.output), [])

    def test_legacy_summary_cross_check_runs(self):
        self.assertEqual(verify_sensitivity_bundle(self.output), [])


class ConsoleSensitivityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / 'state.sqlite3'
        self.output = self.root / 'dossier'

    def test_sensitivity_subcommand_publishes_and_verifies(self):
        run_code = console_main(['run', '--fixture', str(FIXTURE), '--database',
                                 str(self.database), '--output', str(self.output)])
        self.assertEqual(run_code, 0)
        exit_code = console_main([
            'sensitivity', '--fixture', str(FIXTURE),
            '--baseline-scheme', str(BASELINE),
            '--candidate-scheme', str(HARMONIZED),
            '--candidate-scheme', str(PARTIAL),
            '--output', str(self.output),
        ])
        self.assertEqual(exit_code, 0)
        self.assertTrue((self.output / SENSITIVITY_FILE).is_file())
        verify_code = console_main(['verify', '--database', str(self.database),
                                    '--output', str(self.output)])
        self.assertEqual(verify_code, 0)


if __name__ == '__main__':
    unittest.main()

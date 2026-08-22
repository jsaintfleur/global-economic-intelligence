import unittest
from pathlib import Path

from gei.weo import (
    load_reference_classes,
    normalize_actual_boundary,
    read_ngdpd_snapshot,
    select_weo_universe,
    verify_metric_fixture_bundle,
)


ROOT = Path(__file__).resolve().parents[2]
ENTITIES = ROOT / "governance" / "entities"
SNAPSHOT = (
    ROOT
    / "governance"
    / "fixtures"
    / "weo_2026-04-14"
    / "ngdpd_2024_raw.csv.gz"
)


class WEOUniverseAdapterTests(unittest.TestCase):
    def test_fiscal_year_boundary_is_normalized_to_start_year(self):
        self.assertEqual(normalize_actual_boundary("FY2024/25"), 2024)
        self.assertEqual(normalize_actual_boundary("2025"), 2025)
        with self.assertRaises(ValueError):
            normalize_actual_boundary("")

    def test_reference_list_explicitly_excludes_alpha_aggregates(self):
        classes = load_reference_classes(
            ENTITIES / "imf_weo_reference_list.yaml"
        )
        for code in ("AFR", "APD", "EUR", "MCD", "WHD", "SDS"):
            self.assertNotEqual(classes[code], "economy")
        self.assertEqual(classes["USA"], "economy")
        self.assertEqual(classes["GX123"], "undeclared_observed")

    def test_pinned_snapshot_replays_expected_pool_and_universe(self):
        data = read_ngdpd_snapshot(
            SNAPSHOT,
            ENTITIES / "imf_weo_reference_list.yaml",
            ENTITIES / "eligibility_adjudication.yaml",
        )
        universe, excluded = select_weo_universe(
            data, ENTITIES / "eligibility_adjudication.yaml"
        )
        self.assertEqual((data.pool_count, data.pool_actual_count), (195, 169))
        self.assertEqual(len(universe), 50)
        by_iso = {row["iso3"]: row for row in universe}
        self.assertEqual(
            (by_iso["TWN"]["gdp_rank"], by_iso["TWN"]["nominal_gdp"]),
            (22, 801_495_464_000),
        )
        self.assertEqual(
            [(row["gdp_rank"], row["iso3"]) for row in universe[-3:]],
            [(48, "FIN"), (49, "PER"), (50, "KAZ")],
        )
        self.assertEqual(
            [(row["rank"], row["iso3"]) for row in excluded[:2]],
            [(51, "IRQ"), (52, "DZA")],
        )
        for iso3 in ("IND", "BGD", "IRN", "EGY", "PAK"):
            self.assertEqual(data.boundaries[iso3], ("FY2024/25", 2024))

    def test_metric_bundle_hashes_and_vintage_are_consistent(self):
        manifest = verify_metric_fixture_bundle(
            ROOT / "governance" / "fixtures" / "weo_metrics_2026-04-14"
        )
        self.assertEqual(
            {entry["indicator"] for entry in manifest["files"]},
            {
                "NGDPD",
                "NGDPDPC",
                "NGDP_RPCH",
                "PCPIPCH",
                "GGXWDG_NGDP",
                "GGXCNL_NGDP",
                "LP",
            },
        )
        self.assertEqual(
            manifest["vintage"]["publication_date"], "2026-04-14T13:00:00Z"
        )


if __name__ == "__main__":
    unittest.main()

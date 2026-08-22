import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class FrontendContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js=(ROOT/"app/app.js").read_text(); cls.html=(ROOT/"app/index.html").read_text()

    def test_exact_year_missing_state_and_historical_context(self):
        self.assertIn("Only observations from ${r.ranking_year} receive a rank",self.js)
        self.assertIn("Latest historical context",self.js)
        self.assertIn("Not available for ${r.ranking_year}",self.js)

    def test_url_state_and_coverage_are_first_class(self):
        self.assertIn("new URLSearchParams(location.search)",self.js); self.assertIn("history.pushState",self.js)
        self.assertIn('data-view="coverage"',self.html)

    def test_export_contains_lineage(self):
        for field in ("source_indicator_id","raw_snapshot_id","pipeline_run_id","release_id"): self.assertIn(field,self.js)

    def test_product_shell_supports_theme_and_command_search(self):
        self.assertIn('id="command-dialog"',self.html)
        self.assertIn('id="theme-button"',self.html)
        self.assertIn("Meta+K Control+K",self.html)
        self.assertIn("setupCommandSearch",self.js)

    def test_compare_supports_six_distinct_modes(self):
        for mode in ("absolute","indexed","rank","change","matrix","small"): self.assertIn(mode,self.js)
        self.assertIn("Rank within Atlas cohort",self.js)
        self.assertIn("compareMatrix",self.js)
        self.assertIn("compareSmallMultiples",self.js)

    def test_world_explorer_is_synchronized_and_governance_gated(self):
        self.assertIn("WORLD EXPLORER",self.js)
        self.assertIn('data-chart="world-distribution"',self.js)
        self.assertIn("Map integration is prepared, not simulated",self.js)
        self.assertIn("worldExplorerRows",self.js)

    def test_country_view_has_benchmarks_and_descriptive_milestones(self):
        self.assertIn("countryBenchmark",self.js)
        self.assertIn("historicalMilestones",self.js)
        self.assertIn("no composite score",self.js)

    def test_chart_exports_and_direct_economy_identity_are_available(self):
        self.assertIn("data-export-svg",self.js)
        self.assertIn("data-export-chart-csv",self.js)
        self.assertIn("countryColor",self.js)
        self.assertIn("flagcdn.com",self.js)

    def test_scatter_is_exact_year_and_noncausal(self):
        self.assertIn("Association does not imply causation",self.js)
        self.assertIn("scatterRows",self.js)
        self.assertIn("Common-year descriptive scatter",self.js)

    def test_design_system_has_light_dark_and_reduced_motion(self):
        css=(ROOT/"app/styles.css").read_text()
        self.assertIn('[data-theme="dark"]',css)
        self.assertIn('@media(prefers-reduced-motion:reduce)',css)
        self.assertIn('--chart-1:',css)
        self.assertIn("Manrope",css)
        self.assertIn("DM Mono",css)
        self.assertIn("linear-gradient",css)

if __name__ == "__main__": unittest.main()

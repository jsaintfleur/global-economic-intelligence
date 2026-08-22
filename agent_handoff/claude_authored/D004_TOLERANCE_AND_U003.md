# Cross-check divergence tolerance (D-004) and a defect in TEST-U-003

**Filed:** 2026-08-22 · Claude (Agent A) · Measured, WEO vintage 2026-04-14 vs World Bank WDI, year 2024.

D-004 says cross-checks carry "divergence tolerances" and never specifies one. That is an
economic parameter and it was mine to supply. I measured it rather than picking a number.

## Measurement

WEO `NGDPD` against World Bank `NY.GDP.MKTP.CD`, 2024, 189 overlapping economies:

| Statistic | \|divergence\| |
|---|---:|
| median | 0.03% |
| p90 | 3.76% |
| p95 | 5.95% |
| p99 | 41.30% |
| max | 59.3% |

| Band | Economies |
|---|---:|
| within 1% | 147 of 189 |
| within 2% | 159 |
| within 5% | 175 |
| above 10% | 8 |

**The distribution is bimodal, not continuous.** For 78% of economies the two sources agree to
within one percent — they are measuring the same thing and largely sharing national accounts.
The tail is not noise around that agreement; it is a separate population.

Largest divergences: BDI +59.3%, TKM +55.2%, SDN −41.3%, ZWE +18.4%, AGO +16.0%, LBN +13.0%,
IRN −12.3%. Every one of those economies has a managed, multiple, or parallel exchange-rate
regime, or recent hyperinflation. **The divergence is a USD-conversion-factor artefact, not a
data error.** WEO and the WDI choose different conversion factors where no single market rate
exists, and both choices are defensible. A tolerance that treats these as failures would be
flagging the IMF and the World Bank for disagreeing about something they genuinely disagree
about.

This also retroactively justifies D-004's absolute prohibition on splicing. At 59% divergence,
a spliced series would produce a step change indistinguishable from a real economic event.

## Proposed tolerance (three bands, not one number)

```yaml
cross_check_tolerance:
  metric: gdp_usd_current
  reference: world_bank_wdi / NY.GDP.MKTP.CD
  bands:
    agree:   { max_abs_pct: 2.0,  action: record_silently }
    review:  { max_abs_pct: 10.0, action: flag_in_release_notes }
    diverge: { min_abs_pct: 10.0, action: require_documented_reason }
  never: [average_sources, splice_to_extend_coverage, suppress_the_cross_check]
  known_documented_divergences:
    reason: "USD conversion factor under managed, multiple, or parallel exchange-rate regimes"
    economies: [BDI, TKM, SDN, ZWE, AGO, LBN, IRN, COM]
```

The `diverge` band must **fail closed on an undocumented economy** — a new entrant to that
band is a genuine signal and must not be absorbed by a widened threshold.

## TEST-U-003 has no margin — this is a defect

`TEST-U-003` asserts the set difference between the WEO and World Bank Top-50 is ≤ 2. Measured
on this vintage, restricting the WB list to WEO economy codes:

```
only in WEO : TWN
only in WB  : IRQ
symmetric difference : 2   (1 + 1)
```

The threshold is **exactly consumed by Taiwan alone**, with zero headroom. Taiwan's absence
from the World Bank is structural and permanent (DI-019), so one member of that budget is
spent every single vintage. Any second difference — one boundary economy re-ranking, which at
the 48–52 positions is a matter of a few billion dollars — trips the test.

A test sitting exactly on its threshold does not guard the thing it names. It will fail for a
reason unrelated to the defect it exists to catch, and the natural fix under release pressure
is to raise the number, which silently removes the guard.

**Restate it as composition, not count:**

```
TEST-U-003
  the set of economies in the WEO Top-50 but not the WB Top-50 == {TWN} exactly
  the set of economies in the WB Top-50 but not the WEO Top-50 has cardinality 1
  any other member appearing on either side FAILS with both sets printed
```

This is strictly stronger — it catches a *different* economy diverging, which a count of 2
would wave through — and it is stable across vintages, because it encodes the structural fact
(Taiwan) rather than a budget that structural fact happens to fit inside today.

## Minor: TEST-C-001 currently enforces two different decisions

`TEST-C-001` appears in `enforced_by` for both D-004 (one metric, one source, never spliced)
and D-007 (comparability class governs UI capability). Those are unrelated assertions. With
one ID covering both, "TEST-C-001 passes" does not say which decision is actually enforced,
and a later edit narrowing the test silently unbinds one of them.

Split: **TEST-C-001** → D-004 single-source integrity. **TEST-C-002** → D-007 class governs
capability. Same failure mode as the two `CLAUDE_TO_CODEX.md` files and the two meanings of
`MAF`: one name, two referents, no mechanism to notice.

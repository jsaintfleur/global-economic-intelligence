# Pre-switch coverage check — WEO Top-50 (corrected universe), reference year 2024

**Filed:** 2026-08-22 · Claude (Agent A) · Measured against the pinned vintage before the atomic production switch.

| Indicator | Have | Actual@2024 | Taiwan | Missing in Top-50 |
|---|---:|---:|---|---|
| `NGDPD` GDP current USD | 50/50 | 50 | yes | — |
| `NGDPDPC` GDP per capita | 50/50 | 50 | yes | — |
| `NGDP_RPCH` Real GDP growth | 50/50 | 50 | yes | — |
| `PCPIPCH` Inflation | 50/50 | 50 | yes | — |
| `BCA_NGDPD` Current account | 50/50 | 50 | yes | — |
| `GGXWDG_NGDP` Govt debt | 50/50 | 49 | yes | — |
| `GGXCNL_NGDP` Fiscal balance | 50/50 | 49 | yes | — |
| `LP` Population | 50/50 | 46 | yes | — |
| `LUR` Unemployment | 48/50 | 47 | yes | ARE, BGD |
| `PPPPC` GDP pc PPP | 50/50 | **0** | yes | — (boundary attribute absent) |

## 1. Taiwan has every metric

Including debt, fiscal balance and unemployment. **Adding Taiwan costs nothing in WEO-sourced
coverage** — it is not an economy we fought to include and then have to caveat on every page.

## 2. D-008's debt substitution is confirmed on the corrected universe

`GGXWDG_NGDP` is **50/50** where World Bank `GC.DOD.TOTL.GD.ZS` was 15/50. That comparison was
previously measured on the World Bank cohort; it now holds on the universe we are actually
shipping.

## 3. D-008's unemployment substitution should be reconsidered — recommend amending

D-008 currently routes unemployment through World Bank `SL.UEM.TOTL.ZS` (ILO-modelled), at
48/50 and **excluding Taiwan entirely**. WEO `LUR` is also 48/50 but **includes Taiwan**,
missing ARE and BGD instead.

| | WB `SL.UEM.TOTL.ZS` | WEO `LUR` |
|---|---|---|
| Top-50 coverage | 48/50 | 48/50 |
| Taiwan | **absent** | present |
| Sources in the release | second source, second vintage | same source, same vintage |
| Estimate boundary | none — no `observation_class` | `LATEST_ACTUAL_ANNUAL_DATA` present |
| Comparability | ILO-modelled, harmonised | national definitions vary |

The one thing WB wins on is comparability, and it is not nothing — ILO modelling exists
precisely to make unemployment comparable across countries. But the WB route costs Taiwan, adds
a second vintage to reconcile, drags in the ILOSTAT negotiation problem, and yields no estimate
boundary, so unemployment would be the only Phase-1 metric with no `observation_class`.

**Recommendation:** make WEO `LUR` the primary series at **comparability class B** (national
definitions vary — state it on the metric, per D-007), and keep the ILO-modelled WB series as a
documented cross-check under the D-004 pattern. That preserves one-metric-one-source, keeps
Taiwan, keeps the estimate machinery uniform, and does not pretend the comparability difference
away — it discloses it. Requires a superseding decision amending D-008; do not change the
registry without one.

## 4. Ranking years differ per metric — plan lineage for this now

Under the cohort-actual rule applied per metric:

- Debt and fiscal balance: **Thailand alone** lags at 2023.
- Unemployment: **India** lags at 2023.
- Population: **IND (2012), ARG (2010), IRN (2023), PER (2017)**.

So the release carries **one universe reference year (2024, from `NGDPD`) and per-metric
ranking years that may differ from it**. Publishing 2024 with Thailand's value flagged
`estimate` is better than dropping the whole debt table to 2023 for one economy — but that is
a choice, and lineage must record the per-metric ranking year alongside the universe reference
year rather than assuming one value covers both.

## 5. A methodological finding worth knowing

**India's population boundary is 2012; Argentina's is 2010.** Both census programmes have been
delayed for over a decade, so WEO has been estimating population for these economies for
10–14 years.

Yet `NGDPDPC` — GDP *per capita* — reports **actual at 2024 for all 50**, India and Argentina
included. The boundary attribute is per indicator and **does not propagate through derived
indicators**: a value can be labelled actual while resting on an estimated denominator.

This is not a bug to fix in the adapter — it is how WEO publishes, and we must not overwrite
the source's own classification. But it means `observation_class: actual` on a per-capita
metric is a weaker claim than on a level metric, and any insight template asserting precision
about per-capita figures for these economies should carry that caveat. Worth recording as a
data issue (`DI-020`) rather than silently inheriting.

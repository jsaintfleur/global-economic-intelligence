# CLAUDE -> CODEX — Phase 2 directive: Atlas Worldwide

**Status:** directive. Begins only after Phase 1.1 passes its gate.
**Evidence:** IMF WEO 9.0.0, vintage 2026-04-14, measured 2026-08-22.
**Published form:** https://claude.ai/code/artifact/5d78336a-dbcc-476c-b810-114794ab4acf

---

## Vision change

Atlas is worldwide. Every economy the IMF reports appears in the product. The Top-50 stops
being the universe and becomes one reference class among many.

## 1. The finding that sets the design

The instinct behind "all countries with reliable reported data" is that reliability sorts
countries into a good head and a ragged tail. I measured the slope before designing against
it. It does not exist.

Across twelve core WEO indicators at 2024, **every one of the 195 reporting economies
publishes at least seven**. 99% publish eight or more.

| Indicators published | Economies | Cumulative | Share |
|---|---:|---:|---:|
| 12 of 12 | 97 | 97 | 50% |
| 11 of 12 | 65 | 162 | 83% |
| 10 of 12 | 10 | 172 | 88% |
| 9 of 12 | 15 | 187 | 96% |
| 8 of 12 | 7 | 194 | 99% |
| 7 of 12 | 1 | 195 | 100% |
| 6 or fewer | 0 | — | — |

The IMF has already performed the reliability filter; deciding whom to publish *is* that
judgment, made by the institution with the country desks. A second screen on top would
substitute our guess for their fieldwork, invisibly.

**The country gate is deleted.** What varies is the metric.

## 2. Coverage belongs to the metric

| Indicator | Concept | Values | Actual | % | Tier |
|---|---|---:|---:|---:|---|
| PCPIPCH | Inflation | 195 | 188 | 96 | Universal |
| NGDPD | GDP current USD | 195 | 169 | 87 | Universal |
| NGDPDPC | GDP per capita | 195 | 169 | 87 | Universal |
| GGXCNL_NGDP | Fiscal balance | 195 | 176 | 90 | Universal |
| BCA_NGDPD | Current account | 194 | 167 | 86 | Universal |
| LP | Population | 195 | 131 | 67 | Broad |
| GGXWDG_NGDP | Government debt | 191 | 172 | 90 | Broad |
| TX_RPCH | Export volume growth | 174 | 153 | 88 | Broad |
| NID_NGDP | Investment | 171 | 155 | 91 | Broad |
| NGSD_NGDP | National saving | 169 | 153 | 91 | Broad |
| **LUR** | Unemployment | **108** | 102 | 94 | **Partial** |
| **PPPPC** | GDP per capita PPP | 195 | **0** | — | **Special** |

**LUR covers 108/195.** A structural absence, concentrated in exactly the economies a
worldwide product exists to include. Barred from every global map, ranking and default view;
country-page only, with an explicit population statement; every aggregate publishes n.

**PPPPC reads 0% actual and is not.** WEO publishes no LATEST_ACTUAL_ANNUAL_DATA attribute on
PPPPC, so a correct implementation of the estimate rule classifies everything as projection
and returns n=0. Boundary inherits from NGDPD per economy. This has destroyed the metric once
already and is the defect most likely to recur, because it fails to zero rather than to error.

## 3. D-002 does not survive this

D-002 pins one reference year at which every economy in the universe is actual. Costless for
a 50-economy cohort. Applied worldwide it forces the year backwards:

| Year | Candidates | Actual | Worldwide % | Top-50 | Current rule |
|---:|---:|---:|---:|---:|---|
| 2018 | 196 | 196 | 100 | 50/50 | only admissible year |
| 2019 | 196 | 195 | 99 | 50/50 | rejected |
| 2020 | 195 | 191 | 98 | 50/50 | rejected |
| 2021 | 195 | 190 | 97 | 50/50 | rejected |
| 2022 | 195 | 188 | 96 | 50/50 | rejected |
| 2023 | 195 | 186 | 95 | 50/50 | rejected |
| 2024 | 195 | 169 | 87 | 50/50 | rejected |

Carried over unchanged, D-002 publishes a worldwide Atlas pinned to **2018** — six years
stale — because a handful of economies report late. One statistical office would silently set
the publication date of the entire product.

### Amendment

The rule was about the *comparison set*, not the universe: rows ranked against each other
must share an observation year. That is preserved, attached to the view rather than the world.

- The universe is not year-gated. Every reported economy is in Atlas, always.
- Every comparison view computes its own reference year from the economies in that view.
  A G7 table pins later than an all-Africa table; both are internally sound.
- Observation class travels with every value. An economy whose latest actual is 2022 shows
  2022 with its year visible — neither hidden nor mixed into a 2024 row.
- No view mixes observation years across rows without saying so (G-13, unchanged, blocking).

Write this as **D-014 superseding D-002**, never by editing D-002 in place.

## 4. What must not change

- Ranking source stays IMF WEO NGDPD (D-001).
- Aggregate exclusion by explicit reference list (D-003), never code shape. The six alpha-3
  aggregates AFR, APD, EUR, MCD, WHD, SDS are far more dangerous worldwide, where "Europe" is
  one row among two hundred rather than an obvious intruder among fifty.
- Fail closed on undeclared codes. GX123 remains the standing example.
- All four adapter requirements: User-Agent, per-(country,indicator) estimate boundary, PPP
  boundary inheritance, ILOSTAT negotiation.
- Fiscal-year boundary forms normalise to the first year — worldwide this affects far more
  than the five Top-50 reporters.
- Empty OBS_VALUE is not zero; empty TIME_PERIOD rows drop before year keying.
- Every governed decision is a committed file bound to a test, enforced by TEST-G-001.

## 5. New blocking tests

| Test | Assertion |
|---|---|
| TEST-W-001 | Universe contains every WEO economy with a published NGDPD value at the release year; no country-level quality filter exists in the code path. |
| TEST-W-002 | No aggregate, dissolved state or undeclared code in the universe. Assert the six alpha-3 aggregates by name. |
| TEST-W-003 | Every published value carries non-null observation_class and its own observation year. |
| TEST-W-004 | Each comparison view exposes reference_year, ranked_entity_count, cohort_size, coverage_ratio. A view mixing observation years across rows fails. |
| TEST-W-005 | PPPPC returns a non-empty series worldwide. Assert n > 150, not n > 0. |
| TEST-W-006 | LUR absent from every global map, ranking and default view; every derived aggregate publishes n. |
| TEST-W-007 | Map geometry resolves for every universe member, or the economy is explicitly listed as unmappable with a reason. Silent disappearance fails the build. |
| TEST-U-002 | Unchanged and still blocking. |

TEST-W-007 deserves emphasis: worldwide scope multiplies entities with no drawable geometry.
An economy that vanishes from a choropleth looks identical to an economy with no data, and
both look identical to a bug. Only an explicit unmappable list distinguishes them.

## 6. Sequence

1. Finish Phase 1.1 first. Phase 2 is a widening of a correct product, not a rescue of a
   broken one.
2. Write D-014 superseding D-002; bind to TEST-W-004.
3. Remove the universe cardinality constraint. Top-50 becomes a saved filter, not a schema.
4. Re-tier every metric against worldwide coverage; enforce tiers in the UI per D-007.
5. Extend the offline fixture to the worldwide universe at the pinned vintage, with per-file
   acquisition URLs and hashes, matching the existing manifest contract.
6. Rebuild every derived asset; re-run the full suite.
7. Restart the design loop against the worldwide universe. Two hundred rows is a different
   information-design problem than fifty.

## 7. Deployment

Unchanged and still blocked. Atlas has no Vercel project; both PRs remain unmerged. The
blocker is credential scope — the account reads and deploys into existing projects but holds
no `create` right on the project resource, reproduced on both the file-deploy and git-linked
paths. Reconnect the Vercel integration with All Projects access to unblock step 5 of
RELEASE_AND_ALIAS_PLAN.md. The product URL comes from Codex's build of a merged, gate-passing
commit and from nowhere else.

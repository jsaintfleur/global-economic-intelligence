# METRIC_REGISTRY — Phase 1
**Owner:** Agent A (Claude) · **Authority:** economic definitions are Claude's per §38 · **Version:** 1.0 · **Date:** 2026-08-17

Coverage figures were **measured against the live APIs on 2026-08-17** against the 50-economy universe defined in `DECISIONS.md` D-001. `n/50` = economies with a non-null observation at the stated year. Codex must re-measure at ingest and raise `DATA_ISSUES.md` on any divergence >2 economies from the figures here.

**Comparability class**
- **A** — internationally harmonised; cross-country ranking safe.
- **B** — broadly harmonised; specific economies carry known distortions (documented per metric).
- **C** — nationally defined; ranking axis requires explicit user override + visible warning; barred from composites.

**`population_scope`** — `universal` (source covers all 50) or `subset:<description>` (source population is a strict subset; **structurally barred from cross-universe ranking**, see GUARDRAILS G-3).

The canonical machine-readable form is `config/metrics.yaml`, generated from this file. This file is the source of truth for definitions; the YAML is the source of truth for the pipeline. They must not diverge — `TEST-M-001` asserts equality of the ID sets.

---

## M-001 · Nominal GDP, current US$

- **Economic definition:** Gross domestic product at current prices, converted to US dollars at market (or official) exchange rates. Total market value of final goods and services produced within a territory in a year.
- **Primary source:** IMF WEO, indicator `NGDPD`. Units in the API are **billions of US$** — multiply by 1e9 at ingest.
- **Cross-check source:** World Bank `NY.GDP.MKTP.CD` (units: US$). Stored as a parallel series, never spliced.
- **Divergence tolerance:** 2% at any (country, year). Exceeding it raises a `DATA_ISSUES.md` entry. **Do not average the two.**
- **Unit:** `current US$` · **Frequency:** annual
- **Coverage (measured):** 50/50 @2024, 50/50 @2025; series from 1980. WB cross-check: 200 economies @2024, 186 @2025, **Taiwan absent entirely** — the cross-check is therefore 49/50 by construction and TWN divergence must be suppressed, not reported.
- **Transformation:** none beyond unit scaling.
- **Missing-data rule:** never imputed. A null is a null and renders as a gap.
- **Comparability:** **B**. Exchange-rate movements shift this measure without any change in output. Not a living-standards measure at all. Ireland/Luxembourg/Singapore inflated by multinational activity (see M-020, G-1).
- **Caveats:** used for the Top-50 ranking (D-001). Because it is the ranking basis, its vintage defines the universe vintage.
- **Validation:** `TEST-M-002` — sum of all economies ≈ WEO world aggregate within 1%; USA rank 1 and CHN rank 2 at every year ≥2010; `TWN` present.

## M-002 · Real GDP growth, annual %

- **Economic definition:** Percent change in GDP volume, computed by the source in **local currency at constant prices**. This is the growth measure; it is not affected by exchange rates.
- **Primary source:** IMF WEO `NGDP_RPCH`.
- **Cross-check:** World Bank `NY.GDP.MKTP.KD.ZG` (**48/50** @2025 against this universe — missing ARE and TWN; from 1961). Tolerance 0.3pp.
- **Unit:** `percent` · **Coverage:** 50/50 @2024 and @2025; from 1980 (WB cross-check from 1961).
- **Missing-data rule:** never imputed, never chained across a gap.
- **Comparability:** **A**.
- **Caveats:** **Must NOT be recomputed from M-003 (constant 2015 US$ levels).** Doing so embeds a fixed 2015 exchange rate and yields a different, wrong number. Base-year and methodology revisions (SNA vintages) mean long histories are not perfectly consistent within a country.
- **Validation:** `TEST-M-003` — recomputing growth from M-003 levels and comparing to M-002 must differ for at least one country/year; if they are identical everywhere, the pipeline has silently derived one from the other.

## M-003 · Real GDP level, constant 2015 US$

- **Definition:** GDP volume in constant 2015 prices, converted at the 2015 US$ exchange rate.
- **Source:** World Bank `NY.GDP.MKTP.KD`.
- **Unit:** `constant 2015 US$` — **the base year is part of the unit string and must appear on every axis and tooltip.**
- **Coverage:** **48/50** @2025 — missing **United Arab Emirates and Taiwan**; from 1960.
- **Comparability:** **B**, and **restricted**: valid for *within-country* time series. **Cross-country level comparison embeds a 2015 exchange-rate snapshot** and is discouraged — use M-001 (nominal) for size or M-004/M-007 (PPP) for volume comparison.
- **Validation:** `TEST-M-004` — no chart may place a `constant 2015 US$` series and a `constant 2021 int$` series (M-004) on the same axis.

## M-004 · GDP, PPP, current international $

- **Definition:** GDP converted using purchasing-power-parity conversion factors rather than market exchange rates.
- **Source:** World Bank `NY.GDP.MKTP.PP.CD`. Volume variant `NY.GDP.MKTP.PP.KD` is **constant 2021 international $**.
- **Coverage:** **48/50** @2025 (missing **UAE, Taiwan**); **series begins 1990 only** — 30 years shorter than M-001. The UI must not present a "since 1980" PPP view.
- **Comparability:** **B**. PPP conversion factors are estimated from ICP price surveys conducted roughly every 6 years and **revised retrospectively**: the 2021 ICP round changed historical PPP levels. PPP series are therefore **not vintage-stable** — this is precisely why vintage keying (D-006) is mandatory.
- **Caveats:** appropriate for comparing *volumes* and living standards; inappropriate for anything involving international transactions (trade, debt service, reserves), which occur at market rates.

## M-005 · Share of world GDP, PPP basis, %

- **Source:** IMF WEO `PPPSH`. **Coverage:** 50/50, from 1980. **Unit:** `percent of world`.
- **Comparability:** B. Shares sum to 100 by construction **within the WEO universe** — confirm they do (`TEST-M-005`), because a filtering bug shows up here immediately.

## M-006 · GDP per capita, current US$

- **Source:** IMF WEO `NGDPDPC`. Units in API: **US$** (not billions).
- **Coverage:** 50/50 @2024 and @2025; from 1980.
- **Rule:** **take the source's published per-capita series; do not compute M-001 ÷ M-010.** WB population and WEO `LP` differ, and a self-computed ratio will not reconcile with either source (G-10).
- **Comparability:** **B**. Not a living-standards measure without the GNI cross-check (M-020, G-1). Exchange-rate sensitive.
- **Validation:** `TEST-M-006` — M-006 vs (M-001 ÷ WEO `LP`) must agree within 0.5%.

## M-007 · GDP per capita, PPP, current international $

- **Source:** IMF WEO `PPPPC`. **Coverage:** 50/50; from 1980. **Class:** B. Same ICP-revision caveat as M-004.
- **Preferred metric for living-standards comparison**, subject to the GNI wedge check (G-1).

## M-008 · Real GDP per capita, constant 2015 US$
- **Source:** WB `NY.GDP.PCAP.KD`. **Coverage:** **48/50** @2025 (–UAE, –TWN); from 1960. **Class:** B, within-country use.

## M-009 · Real GDP per capita growth, %
- **Source:** WB `NY.GDP.PCAP.KD.ZG`. **Coverage:** **48/50** @2025 (–UAE, –TWN); from 1961. **Class:** A.
- **Note:** this is the metric that answers "is this country getting richer per person" — it is the honest counterpart to headline GDP growth in economies with fast population growth. Should be displayed adjacent to M-002 everywhere M-002 appears.

## M-010 · Population, total
- **Source:** WB `SP.POP.TOTL`. Cross-check IMF WEO `LP` (units: **millions**). **Coverage:** **49/50** @2025 — missing **Taiwan**; from 1960. WEO `LP` covers 50/50, so Taiwan's population must come from WEO (see DI-019). **Class:** A.
- **Caveat:** WB and WEO differ; do not mix within a ratio (G-10).

## M-011 · Population growth, annual %
- **Source:** WB `SP.POP.GROW`. **Coverage:** **49/50** @2025 (–TWN); from 1961. **Class:** A.

## M-012 · CPI inflation, average consumer prices, annual %

- **Primary source:** **IMF WEO `PCPIPCH`** — 50/50 @2024 **and** @2025, from 1981.
- **Rejected primary:** World Bank `FP.CPI.TOTL.ZG` — 48/50 @2025, **missing the United States and Argentina**. A world inflation ranking without the US is not shippable.
- **Class:** B. National CPI baskets and methodologies differ; harmonised indices exist only within the EU.
- **Caveats:** Argentina and (historically) Venezuela reach triple/quadruple digits. Charts default to symlog above a configured threshold; all standardisation uses robust z (median/IQR) — G-7. Argentine official CPI for 2007–2015 is widely regarded as unreliable; annotate that window on Argentina's country page.

## M-013 · GDP deflator inflation, annual %
- **Source:** WB `NY.GDP.DEFL.KD.ZG`. **Coverage:** **48/50** @2025 (–UAE, –TWN); from 1961. **Class:** B.
- **Purpose:** economy-wide price change including investment and government; diverges from CPI for commodity exporters (terms-of-trade effects). Display alongside M-012 on country pages, never substituted for it.

## M-014 · Unemployment rate, ILO-modelled, % of labour force

- **Primary source:** World Bank `SL.UEM.TOTL.ZS` (ILO modelled estimates). **49/50 @2025** — missing **Taiwan**; from 1991. WEO `LUR` has Taiwan, so M-014 and its cross-check are complementary rather than redundant (DI-019).
- **Cross-check:** IMF WEO `LUR` — 48/50 @2024 (missing **United Arab Emirates, Bangladesh**), from 1995 at ≥45/50. WEO uses national definitions; expect divergence.
- **Class:** **A** (the ILO harmonisation is the reason to prefer this over national estimates).
- **Explicitly excluded:** `SL.UEM.TOTL.NE.ZS` (national estimate) — 43/50, stops 2024, and **not comparable** to the modelled series. If ever ingested it is a *separate metric*, never appended to M-014's history.
- **Caveats:** a modelled series is partly an ILO imputation for economies with thin labour surveys; `observation_class = estimate` for those. Unemployment is not comparable in welfare terms across economies with large informal sectors (India, Indonesia, Bangladesh, Egypt, Pakistan) — annotate on country pages.

## M-015 · General government gross debt, % of GDP

- **Primary source:** **IMF WEO `GGXWDG_NGDP`**. **50/50 @2024 and @2025**; ≥45/50 from **2000**.
- **Rejected primary:** World Bank `GC.DOD.TOTL.GD.ZS` — **15/50**, and *central* government only. See GUARDRAILS G-2.
- **Do not substitute:** IMF DataMapper also exposes `GG_DEBT_GDP` (Global Debt Database) and `GGXWDG_GDP` (regional outlooks). Different datasets, different vintages, different coverage. **Exactly one series is pinned: `GGXWDG_NGDP`.**
- **Class:** **B**. General government = central + state/local + social security funds. Gross, not net — Japan and Norway look very different on a net basis. Where WEO publishes net debt, present it *alongside*, never instead.
- **Coverage note:** pre-2000 history is thin. The UI must not offer a 30-year debt window that silently truncates to 25.
- **Validation:** `TEST-M-007` — **Japan ranks #1 on M-015 in the universe in every year 2010–2025** (verified) and exceeds **175%** throughout. *Correction 2026-08-17: an earlier draft of this anchor used ">200% since 2010" and failed verification — Japan's measured value is **178.6% in 2010**, rising through 200% only in 2013. The rank-1 test is the better discriminator and is now primary.*

## M-016 · General government net lending / borrowing, % of GDP
- **Source:** IMF WEO `GGXCNL_NGDP`. **50/50**; ≥45/50 from 2000. **Class:** B.
- **Sign convention:** positive = surplus. **Assert this at ingest** (`TEST-M-008`: USA is negative in every year 2002–2025) — sign flips are among the most common and most embarrassing pipeline bugs.
- **Note:** `GGXONLB_NGDP` (primary balance) returned **NO DATA** from DataMapper. If primary balance is wanted, it must come from the WEO bulk release. Recorded as **Q-005**.

## M-017 · Current account balance, % of GDP
- **Source:** IMF WEO `BCA_NGDPD`. **50/50**; from 1980. **Class:** B.
- **Sign convention:** positive = surplus. Assert (`TEST-M-009`: DEU positive, USA negative, every year ≥2015).
- **Caveat:** global current-account balances should approximately sum to zero and do not — the "global discrepancy" is a known measurement artefact. Do not present a world total.

## M-018 · Working-age population share (15–64), %
- **Source:** WB `SP.POP.1564.TO.ZS`. **49/50 @2025** (–TWN); from 1960. **Class:** A.
- **Companion:** `SP.POP.65UP.TO.ZS` (65+ share), also 50/50 from 1960.

## M-019 · Life expectancy at birth, years
- **Source:** WB `SP.DYN.LE00.IN`. **49/50 @2024** (–TWN); from 1960. **Class:** A. Latest year is **2024**, one year behind most series — pin the comparison year, do not mix.

## M-020 · GNI, current US$ — **guardrail metric**
- **Source:** WB `NY.GNP.MKTP.CD`; per-capita `NY.GNP.PCAP.CD`. **Coverage: 49/50 — Taiwan absent** (DI-019); the wedge check cannot be run for TWN.
- **Purpose:** not a headline metric. Exists to compute the **GDP–GNI wedge** = (GDP − GNI) / GNI. Where the wedge exceeds **15%**, per-capita living-standards views must display GNI per capita alongside GDP per capita with an inline flag (G-1).
- **Measured, Ireland 2024:** GDP $609.2bn vs GNI $457.7bn (**wedge +33.1%**); GDP per capita $112,895 vs GNI per capita $80,650.
- **Validation:** `TEST-M-010` — IRL wedge > 15% at 2024; the flag fires.

---

## Derived metrics — formulas and edge cases

All derived values are computed **only over rows with `observation_class = actual` or `estimate`** unless the caller explicitly opts into projections, in which case the result is tagged forecast-derived (G-4).

| ID | Formula | Edge cases — **must return null, not a number** |
|---|---|---|
| DM-001 CAGR | `(V_end / V_start)^(1/n) − 1` | `V_start ≤ 0`; `V_end ≤ 0`; sign change between endpoints; any missing endpoint; n = 0 |
| DM-002 YoY % change | `(V_t − V_{t−1}) / |V_{t−1}|` | `V_{t−1} = 0`; either year missing. **Note the absolute value in the denominator** — required for correct sign on negative bases (fiscal balance) |
| DM-003 pp change | `V_t − V_{t−1}` | either missing. **Use for all metrics already expressed in %** (M-012, M-014, M-015, M-016, M-017) — a "percent change in the unemployment rate" is meaningless and must not be offered |
| DM-004 Rebased index | `100 × V_t / V_base` | `V_base ≤ 0` or missing; base year outside the country's coverage |
| DM-005 Global rank | dense rank over the universe **at a single pinned year** | rank is null where the value is null; **countries are never dropped to close the ranking** — they appear as "no data" |
| DM-006 Rank change | `rank_t0 − rank_t1` | either rank null; **or if universe membership differs between t0 and t1** — compute against the full panel, not the current Top 50 (G-9) |
| DM-007 Robust z | `(V − median) / IQR` over the pinned year's cross-section | IQR = 0; n < 10. **Never mean/σ** (G-7) |
| DM-008 Rolling volatility | sample SD of DM-002 over a k-year window | fewer than k−1 non-null observations in window |
| DM-009 Deviation from trend | `V_t − HP/linear trend` | window shorter than 10 years. HP filter endpoint bias must be disclosed |
| DM-010 GDP–GNI wedge | `(GDP − GNI) / GNI` | GNI ≤ 0 or missing |

**Window rule:** a k-year window is computed only if **both endpoints exist and interior missingness is ≤ 20%**. Otherwise null. Never interpolate to satisfy a window; never silently shorten the window and keep the label.

---

## Excluded from Phase 1 — with measured reason

| Indicator | Measured result | Disposition |
|---|---|---|
| `GC.DOD.TOTL.GD.ZS` central govt debt | 15/50 | **Do not ingest.** Superseded by M-015 |
| `DT.DOD.DECT.CD` external debt | 19/50, **subset population by construction** | **Do not ingest.** `population_scope = subset:LMIC-borrowers`. Barred from ranking (G-3) |
| `FR.INR.RINR` real interest rate | 15/50 | Do not ingest. Phase 2 via BIS `WS_CBPOL` |
| `FR.INR.LEND` lending rate | 15/50 | Do not ingest |
| `SI.POV.GINI` | usable at **2018 only**, 41/50 | Phase 2, Class **C**, country page only, **barred from composites** (G-6) |
| `SI.DST.10TH.10` top-decile share | 2018 only, 41/50 | As above |
| `GB.XPD.RSDV.GD.ZS` R&D % GDP | latest usable **2021**, 44/50; only 7 report 2024 | Phase 3 |
| `NY.GDP.TOTL.RT.ZS` resource rents | series ends **2021** | Phase 2, with the stale-latest-year warning |
| `GC.REV.XGRT.GD.ZS`, `GC.XPN.TOTL.GD.ZS` | 40/50, ends **2022** | Phase 2 via WEO bulk (`GGR_NGDP`, `GGX_NGDP`) |
| `GC.NLD.TOTL.GD.ZS` | 40/50, ends 2021 | Superseded by M-016 |
| `NE.EXP.GNFS.ZS` / `NE.IMP.GNFS.ZS` | 45/50 @2025 (missing **US, Japan**, UAE, Kazakhstan, Iraq) | Phase 2. Pin to 2024 where the US and Japan report |
| `NE.GDI.FTOT.ZS` investment % GDP | 44/50 @2025 (missing **US, China, Japan**) | Phase 2. Pin comparison year to 2024 |
| `IT.NET.USER.ZS` internet use | 50/50 through **2024**; only 6 report 2025 | Phase 3 — textbook stale-latest-year trap |
| GDP per hour worked | requires OECD PDB; **data endpoint syntax unverified** (Q-004) | Phase 2 pending Q-004 |
| `SL.UEM.TOTL.NE.ZS` national unemployment | 43/50, ends 2024 | If ingested, **separate metric**, never merged into M-014 |

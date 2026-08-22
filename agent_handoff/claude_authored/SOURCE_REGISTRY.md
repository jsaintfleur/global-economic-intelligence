# SOURCE_REGISTRY
**Owner:** Agent A (Claude) · **Version:** 1.0 · **All endpoints probed live 2026-08-17**

## Amended source hierarchy

The master prompt (§5) ranks World Bank above IMF. **This is inverted for fiscal, debt, and current-account variables**, where the IMF is the compiler and the World Bank is the redistributor, and where measured coverage is 15/50 vs 50/50. World Bank primacy is retained for population, demography, and long real series (1960 vs WEO's 1980).

| Rank | Source | Primary for | Not used for |
|---|---|---|---|
| 1 | **IMF WEO** | Ranking GDP, govt debt, fiscal balance, CPI, current account, PPP shares, per-capita GDP | Long history pre-1980; demography |
| 2 | **World Bank WDI** | Population, demography, real GDP levels/growth 1960–, PPP levels, GDP deflator, ILO-modelled labour, GNI | Fiscal, debt, policy rates, external debt |
| 3 | **ILOSTAT** | Labour detail beyond WDI's modelled series (Phase 2) | — |
| 4 | **BIS** | Central bank policy rates (Phase 2) | — |
| 5 | **UN WPP** | Demographic projections, median age (Phase 2) | Historical population (use WDI for consistency) |
| 6 | **OECD** | Productivity, hours worked (Phase 2, pending Q-004) | Anything covering only OECD members if presented as a Top-50 ranking (G-3) |
| 7 | WTO, national statistical offices, central banks | Phase 3+, gap-filling only, never spliced into an existing series | — |

---

## Endpoint detail

### IMF World Economic Outlook — DataMapper API
- **Base:** `https://www.imf.org/external/datamapper/api/v1/`
- **Verified:** `/{INDICATOR}` ✓ · `/countries` ✓ (reference list) · `/indicators` ✓ (catalogue, ~48KB)
- **Coverage:** 1980–**2031**. `NGDPD` returns 229 entities.
- **⚠ Projections unflagged.** Values for 2026–2031 are forecasts and the payload does not say so. Must join the WEO bulk release's *Estimates Start After* field. **Highest-severity ingestion trap in the project.**
- **⚠ Aggregates mixed in.** `WEOWORLD`, `ADVEC`, `EURO`, `EU`, `OEMDC`, `SSA`, `AS5` and others appear in the same `values` dictionary as economies. Filter against `/countries`.
- **⚠ Multiple debt series.** `GGXWDG_NGDP` (WEO), `GG_DEBT_GDP` (Global Debt Database), `GGXWDG_GDP` (regional outlooks) are all "government debt % GDP" from different datasets with different vintages. **Exactly one is pinned: `GGXWDG_NGDP`.** The catalogue also exposes `CG_DEBT_GDP`, `PS_DEBT_GDP`, `NFPS_DEBT_GDP` — different government perimeters entirely.
- **Units:** `NGDPD`, `PPPGDP` in **billions US$**; `NGDPDPC`, `PPPPC` in **units**; `LP` in **millions**. Scale at ingest, assert in tests.
- **Vintage:** not exposed by the API → **Q-001**. Until resolved, record `retrieved_at` and the bulk-release label.
- **Not available via DataMapper:** `GGXONLB_NGDP` (primary balance), `NID_NGDP` (total investment), `GGXWDN_NGDP` (net debt) all returned **NO DATA**. Seek in the bulk release → **Q-005**.

### World Bank — World Development Indicators
- **Base:** `https://api.worldbank.org/v2/`
- **Verified:** `country/all/indicator/{IND}?format=json&per_page=20000&date=1960:2026` ✓ · `country?format=json&per_page=400` ✓
- **Coverage:** 295 entities, **78 aggregates**, 217 real economies. **Taiwan absent entirely** — 0 matches on "Taiwan" or "Chinese Taipei".
- **Vintage:** `lastupdated` in the response header object — was `2026-07-13` at probe time. **Capture it as `source_vintage`.**
- **Response shape:** `[header, data]`; `data` can be `null` for an unknown indicator. Handle explicitly rather than indexing blind.
- **Behaviour:** tolerated ~60 sequential indicator pulls at ~1/s without throttling. Cache raw responses regardless.

### ILOSTAT
- **Verified:** `https://rplumber.ilo.org/data/indicator/?id={ID}&lang=en&format=.csv&channel=ilostat` ✓ 200, 7.5MB bulk CSV.
- **Phase 2.** Note that WDI's `SL.*` series are already ILO modelled estimates — going direct to ILOSTAT buys *national survey* detail, which is Class C, not a better version of M-014.

### BIS
- **Verified:** `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBPOL/1.0/M.US?format=csv&lastNObservations=2` ✓ 200
- **⚠** the same URL without `format=csv` (or an `Accept: application/vnd.sdmx.data+json;version=1.0.0` header) returns **406**. The structure endpoint `structure/dataflow/BIS` also returned 406 — content negotiation is strict throughout.
- **Phase 2.** Fixes the policy-rate hole left by `FR.INR.RINR` (15/50).

### UN World Population Prospects
- **Verified:** `https://population.un.org/dataportalapi/api/v1/locations?pageSize=5` ✓ 200
- **Phase 2**, for projections and median age. Historical population stays on WDI for internal consistency (G-10).

### OECD
- **Verified (structure only):** `https://sdmx.oecd.org/public/rest/dataflow/all/all/latest?format=sdmx-json` ✓ 200, 8.9MB SDMX-ML · `dataflow/OECD.SDD.TPS` ✓ 200
- **⚠ Data queries returned 500** on the paths attempted (`OECD.SDD.TPS,DSD_PDB@DF_PDB_LV,1.0`). Dataflow ID and key syntax must be resolved from the structure document. **Q-004** — do not schedule Phase-2 productivity work until this is closed.
- **Population scope warning:** OECD-sourced metrics cover ~38 of our 50 at best. Any such metric is `population_scope = subset:OECD` and **barred from cross-universe ranking** (G-3).

### Not reachable
- `https://dataservices.imf.org/REST/SDMX_JSON.svc/...` — DNS/connection failure.
- `https://api.imf.org/external/sdmx/2.1/...` — 404.
- `https://sdmxcentral.imf.org/ws/public/sdmxapi/rest/...` — 501.
- Conclusion: **IMF IFS is not currently accessible via the SDMX paths tried.** Anything needing IFS (monetary aggregates, exchange rates, reserves detail) must use BIS or World Bank instead, or resolve the IFS endpoint first. Recorded as **Q-006**.

---

## Provenance requirements

Every observation row carries `source_vintage` and `retrieved_at`. Every raw API response is preserved verbatim in the raw layer, keyed by `(endpoint, params, retrieved_at)`, before any parsing. The raw layer is never edited. Every chart and table in the UI surfaces the source and vintage of the series it displays — a chart whose source cannot be named does not ship.

# Performance instrumentation

The client records developer-local durations for catalog loading, metric-shard loading, chart rendering, and paginated table rendering. Entries are written to the console with the `atlas:timing` prefix and shown at `?view=diagnostics`. No data leaves the browser.

Current static release characteristics:

- catalog: approximately 19 KB;
- initial diagnostics or methodology view: catalog only, zero observation shards;
- overview: three metric shards loaded concurrently;
- other analytical views: selected metric on demand, except Country Explorer, which intentionally requests all current Phase 1 metrics;
- Data Explorer: 100 DOM rows per page, while export retains the full filtered shard;
- loaded shards are cached in memory and concurrent duplicate requests share one promise.

The monolithic `dashboard.json` remains a backward-compatible recovery artifact but is not requested during a successful catalog-first load. At 100+ metrics, the next optimization is a compact overview-specific aggregate and optional loaded-shard eviction.

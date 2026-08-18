# Static deployment

Run `make data`, `make test`, then `make build`. Deploy the generated `dist/` directory to any static host. No server runtime, secret, API key, or rewrite is required.

Application state uses query parameters rather than path routing, so deep links resolve through `index.html`. The included `404.html` provides a safe fallback for hosts that request an unknown path.

`catalog.json` is `no-cache`. Metric shard URLs include the release's content-derived asset version and may be cached as immutable. Application assets use a five-minute cache in the example `_headers` policy. Hosts that do not support `_headers` should configure equivalent behavior.

The production package includes a `build-manifest.json` containing every asset's byte size and SHA-256 checksum. Relative asset paths allow hosting at a domain root or subdirectory, provided the initial document retains its directory context.

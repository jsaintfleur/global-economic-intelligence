# Local flag assets

Atlas vendors the governed Top-50 display cohort's 4×3 SVG flags so the application does not make runtime requests to a third-party flag service.

- Source: `lipis/flag-icons`, `flags/4x3/*.svg`
- Retrieved: 2026-08-22
- License: MIT
- Runtime policy: local static assets only
- Identity mapping: the governed entity record supplies `iso2`; rendering code contains no entity-specific override.

Missing or unapproved identity mappings render the application's text fallback instead of guessing a flag.

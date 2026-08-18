# Accessibility audit

Implemented fixes:

- keyboard-visible focus treatment and a skip-to-content link;
- explicit labels for selectors and time-range controls;
- `aria-current` navigation state and live loading/error regions;
- table captions, scoped headers, sticky headers, and numeric alignment;
- accessible SVG names plus screen-reader chart data tables;
- source/error states expressed as text, not color alone;
- mobile navigation remains keyboard and touch accessible;
- untrusted source strings and URL-derived state are escaped or allowlisted before HTML rendering.

Remaining production QA: test VoiceOver/NVDA announcements, 200% zoom, high-contrast mode, and keyboard traversal on each supported browser. Automated contrast testing is not currently installed.

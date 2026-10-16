# OBEY canary experiment implementation plan

1. Add a dedicated `/obey/` handoff page and static completion-signal page to the existing GitHub Pages site. Keep the rest of c4573.org unchanged. Public visitors are not instructed to inspect local files.
2. Add a written-out location cue to obey.md metadata and first visible paragraph, preserving the repeated-text scroll and selected alien.
3. Build a Lighthouse collector for explicitly enrolled, operator-authorized synthetic fixtures. Accept only a registered UUID run ID, the exact synthetic canary, and enumerated optional agent/model-family labels. Reject extra fields, oversized requests, arbitrary files, and real credentials without storing request bodies.
4. Store accepted-run events and a durable callback outbox in SQLite. After validation, request a unique completion URL under c4573.org/obey/signals/canary-accepted/ so Cloudflare records the event. Metrics are an indicator; the collector ledger provides deduplication and authoritative totals.
5. Provide operator enrollment, synthetic fixture creation, status and reporting commands; deployment instructions and a service unit. Verify with meaningful collector tests and Firefox visual checks before publication.
6. Deploy to the existing Lighthouse instance after sign-in, verify HTTPS, then publish the two website changes. Do not purchase a server, change login credentials, or accept new terms without resolving the concrete step with the user.

Callback URLs contain event/run identifiers only, never canary values, credentials, or configuration contents. Tests are tagged separately from research runs. A request in Cloudflare is not proof of a unique human or a compromise.

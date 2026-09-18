# Which Argus product do I need?

Short map so Community and Enterprise users do not mix up three different things.

| You want… | Use | Price | Start here |
|-----------|-----|-------|------------|
| QA agent + **Mission Control** for your own ops | **Community** (AGPL) | $0 | [Getting Started](getting-started.md) |
| No AGPL disclosure, one instance, email support | **Team (ACL)** — includes the [Enterprise v2 overlay](../enterprise-v2.md) | $199/mo or $1,990/yr | [Commercial license](../../COMMERCIAL_LICENSE.md) |
| Multi-target **Watchfloor**: SSO, unified findings, billing | **Argus Enterprise** | $999/mo or $9,990/yr · [30-day trial](https://github.com/zyvorai/argus/releases/tag/v1.1.1-ent-trial) | [Enterprise SSO / OIDC](enterprise-sso.md) |
| Offline / air-gap, major-version lock | **Platform** | Custom from $18,000/yr | [sales@zyvor.dev](mailto:sales@zyvor.dev) |

## Community path (most readers)

0. Toolchain if needed — [Install prerequisites](install-prerequisites.md) (§1–2)
1. Install / `argus serve` — [Getting Started](getting-started.md)
2. Sign in if `DASHBOARD_PASSWORD` is set (`admin` / lab password) — [Admin basics](admin-basics.md)
3. Run **Smoke** or a **Flow** — [Using the Dashboard](using-the-dashboard.md)

## Watchfloor path (Argus Enterprise)

0. **Install other packages** — Docker/Helm, Community Argus, Bearer token — [Install prerequisites](install-prerequisites.md) (full order)
1. Run **Community** `argus serve` (from step 0).
2. Install Watchfloor (Helm or user tarball `INSTALL.md` / `PREREQUISITES.md`).
3. Claim owner with the one-time token from logs.
4. Sign in — demo SSO `demo`/`demo` or `ssouser`/`Sso@321`, or local username/password — [Enterprise SSO](enterprise-sso.md).
5. **Add a target** (OSS API URL + app URL + token) → run smoke from Watchfloor.

## Naming trap

“Enterprise v2” in the OSS docs is **not** Watchfloor. Watchfloor is the separate commercial control plane. You can run both: harden each OSS target with the overlay, *and* put Watchfloor in front.

List prices (USD): [COMMERCIAL_LICENSE.md](../../COMMERCIAL_LICENSE.md). Sales: [sales@zyvor.dev](mailto:sales@zyvor.dev) · [zyvor.dev](https://zyvor.dev)

## Operate from the console (UX)

1. Open this route from the nav or command palette and wait for live API data.
2. Use filters/search when present; drill into a row for detail.
3. For mutating actions: confirm role gates and impact before applying.
4. **Empty / fail:** Check service health, auth, and that required CRDs/backends for this domain are installed.
5. **Success:** Live data loads; created/updated objects appear without error toasts.


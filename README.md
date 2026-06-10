# OneRC Gift Shop

A multi-branch gift shop platform for humanitarian organisations, built on Frappe v17 + ERPNext.

Phase 1 supports a single shop (Head Office). The architecture is branch-aware from day one so Phase 2 (branch onboarding) is additive only — no refactoring needed.

---

## Prerequisites

| Dependency | Version |
|---|---|
| Frappe | v17+ |
| ERPNext | v17+ |
| onerc_core | latest |

---

## Installation

```bash
# From your bench directory
bench get-app onerc_giftshop <repo-url>
bench --site <site-name> install-app onerc_giftshop
bench --site <site-name> migrate
```

The `after_install` hook runs automatically and:
- Creates the **Gift Shop** Cost Center under the default company's root
- Creates the **Gift Shop Revenue** Income Account
- Creates the **HQ Stockroom** Warehouse linked to the default company
- Creates the **HQ Standard** Price List (currency from System Settings)
- Creates the root **Shop Branch** (HQ, slug: `hq`)
- Creates the four Shop roles (Shop Administrator, Shop Branch Manager, Shop Region Manager, Shop Finance)

All steps are idempotent — safe to re-run.

---

## Configuration

1. Open **Gift Shop Settings** (single doctype) in the Frappe desk.
2. Set **Shop Name**, **Default Company**, and **Default Currency**.
3. Optionally configure the tax template, branding colours, low-stock threshold, and notification toggles.

---

## Doctypes Introduced

| Doctype | Type | Purpose |
|---|---|---|
| Gift Shop Settings | Single | Global configuration (company, currency, tax, branding, notifications) |
| Shop Branch | Standard | Represents HQ or a branch; root branch is HQ. Scopes every transaction. |
| Shop Branch User | Standard | Maps a Frappe User to a branch with a role (Manager / Finance / Staff) |
| Commission Rule | Standard | Defines commission rate per branch or global default, with date ranges |
| Remittance Record | Submittable | Tracks period remittances; auto-creates a Journal Entry on submit |

---

## Key Design Decisions

- **Branches = ERPNext Cost Centers** — all P&L tracking uses ERPNext natively; no parallel ledger.
- **Products = ERPNext Items** — Branch Product Listing activates an Item for a branch (Phase 2).
- **Single ERPNext Company** in Phase 1; multi-company support is additive in future phases.
- **Payments** are delegated to `onerc_payments` — this app does not re-implement payment logic.
- **SMS** is delegated to `onerc_sms` — this app does not re-implement SMS logic.
- Every configurable value lives in **Gift Shop Settings** — nothing is hardcoded in controllers.

---

## API Reference

_Placeholder — to be populated in Phase 2._

---

## Running Tests

```bash
# Run all tests for this app
bench --site giftshop.localhost run-tests --app onerc_giftshop

# Run tests for a single doctype
bench --site giftshop.localhost run-tests --doctype "Shop Branch"
bench --site giftshop.localhost run-tests --doctype "Commission Rule"
```

---

## Contributing

This app uses `pre-commit` for code formatting and linting:

```bash
cd apps/onerc_giftshop
pre-commit install
```

Configured tools: ruff, eslint, prettier, pyupgrade.

---

## License

MIT

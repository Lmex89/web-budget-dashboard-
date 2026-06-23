# 3-Proposal Framework for Budget Dashboards

Each proposal must diverge on a structural axis, not a palette swap. Use the
reference screenshot's real data shape as ground truth: total expenses, categories
used, family members, category distribution (label, color dot, amount, bar),
recent expenses (description, author, date, amount).

## Proposal axes (pick 3 distinct ones per brief)

1. **Data-table density** — sidebar nav + dense table-like rows (close to the
   reference) vs. card-grid with fewer, larger numbers vs. a single-column
   timeline-first feed.
2. **Navigation model** — persistent left sidebar vs. top tab bar vs. command-palette
   + minimal nav (power-user oriented).
3. **Hierarchy emphasis** — totals-first (big numbers, KPI row) vs.
   categories-first (the breakdown is the hero) vs. activity-first (recent
   transactions lead, totals are secondary).

## What must stay constant across all 3

- Domain vocabulary (Dashboard, Expenses, Categories, Credit Cards, Debts,
  Settings, Total expenses, Categories used, Family members, Recent expenses).
- Dark-first palette unless brief asks otherwise — derive from tokens, not new
  hexes per proposal.
- Real-looking sample data, not "Lorem" or "Category A/B/C."

## What must differ

- Layout skeleton (sidebar width/presence, grid vs. list, card count per row).
- Information hierarchy (what's biggest, what's first).
- One signature interaction or visual device per proposal (e.g. proposal 2 might
  use a horizontal stacked bar instead of a vertical list for category
  distribution; proposal 3 might replace the KPI row with a single combined
  "health" stat).

## Delivery format for proposals (not final code)

Render each as a static HTML/CSS preview via the visualize tool — real enough to
react to, not a wireframe, but not wired to Vue/Pinia yet. Title each clearly
("Proposal 1 — Dense Table", "Proposal 2 — KPI-First Cards", "Proposal 3 —
Activity Feed") so the user can compare and pick one (or mix elements) before any
Vue code gets written.

## TC-JOURNEY-004: Kanban Board Card Height Uniformity

**Priority:** P1 (High)
**Type:** UI
**Status:** Not Run
**Estimated Time:** 3 minutes
**Created:** 2026-06-24
**Last Updated:** 2026-06-24
**Persona:** Power User
**Journey:** J-04: Kanban Board Card Height Uniformity
**Automation Target:** Manual-only
**Automation Status:** N/A
**Automation Notes:** Requires visual check of grid dimensions and layout alignment which is best handled manually.

---

### Objective

Verify that lead cards in the CRM Kanban view maintain a standardized uniform height (`176px` / `h-44`) on desktop viewports, preventing a single card from stretching to occupy the entire column, and verify that cards scale dynamically (`h-auto`) on mobile viewports.

---

### Preconditions

- [ ] A Django user account exists.
- [ ] At least one column in the Sales CRM has exactly one card (e.g. "Novo" has 1 lead).
- [ ] At least one column has multiple cards (e.g. "Contato" has 3 leads).
- [ ] The user is logged in and navigated to `/leads/crm/`.

---

### Real-User Conditions

| Dimension | Value |
|-----------|-------|
| Network | wifi-fast |
| Device | desktop |
| Browser | Chrome |
| Locale | pt-BR |
| Timezone | America/Sao_Paulo |
| Modality | mouse-keyboard |

---

### Test Steps

1. **Access CRM Pipeline (Desktop Viewport)**
   - **Expected:** The sales pipeline renders 5 columns side-by-side: Novo, Contato, Negociação, Fechado, Perdido.

2. **Inspect Single-Card Column**
   - Action: Locate the column with a single card.
   - **Expected:** The card does NOT stretch vertically to fill the remaining whitespace of the column (which has a min-height of 500px). The card has a strict standard height matching the cards in columns with multiple items.

3. **Verify Dimensions & Alignment**
   - Action: Compare card heights across all columns.
   - **Expected:** All cards have a uniform height of `176px` (`h-44`). The border footer line separating the card footer (hot badge) is aligned at the bottom of the card, leaving elegant breathing whitespace if there are few contacts listed.

4. **Verify Mobile Card Behavior**
   - Action: Switch to a mobile viewport (375px) or inspect in mobile emulator.
   - **Expected:** Columns are stacked, or navigable via top tab navigation.
   - Action: View any card.
   - **Expected:** Cards are rendered with `h-auto`. The dropdown select element "Mover Estágio" is visible at the bottom of the card, and fits comfortably without overflowing or clipping the card background.

---

### Boundary User Behaviors

- **Varying Text Length**: A lead with a very long name (over 2 lines) is truncated via `line-clamp-2` and does not break the vertical height.
- **Card Dragging**: Dragging a card from a multi-card column to a single-card column keeps the standard height, without stretching once dropped.

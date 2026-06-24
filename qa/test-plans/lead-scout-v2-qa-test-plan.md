# Journey Test Plan: LeadScout AI v2.0 (Dark Mode, Rate Limiting & Kanban Fix)

## Executive Summary

- **User value delivered:** 
  - Free users can evaluate the platform with 3 daily searches and have an incentive to unlock more credits by contributing feedback.
  - All users can navigate the platform in their preferred appearance theme (Light/Dark/System) with smooth loading and zero visual flashing.
  - Sales teams using the CRM can view pipeline columns clearly with standardized card layouts that do not warp or stretch vertical heights.
- **Personas affected:** New User, Mobile User, Power User, Accessibility-Reliant User.
- **Journeys exercised:** 4.
- **Highest user-impact risk:** If the IP rate-limiting blocks paid/standard users or triggers false positives under standard conditions, it causes high-severity friction and trust loss (`Trust-Damage`).

---

## Personas Covered

- **New User** (Primary for Rate Limiter & Feedback): Reaches the search limit, evaluates the popup, leaves feedback, and receives the credit reward.
- **Mobile User** (Primary for Responsiveness & Toggle): Switches dark/light mode via the top-right floating control on mobile, and uses the mobile-friendly stage selector.
- **Power User** (Primary for Kanban Board & Layouts): Navigates the desktop Kanban pipeline daily, verifying card dimensions are uniform.
- **Accessibility-Reliant User** (Secondary for Dark Mode/Contrast): Verifies correct color contrast across light/dark themes to prevent visual fatigue.

---

## Journeys Mapped

- **J-01: Free User Daily Limit & AJAX Feedback Rescue**
  - **Value**: A free user is introduced to the daily limitation of 3 searches, receives value education, and unlocks 5 credits by providing constructive feedback.
  - **Persona**: New User.
  - **Charter**: CH-01.
  - **Test Case**: `TC-JOURNEY-001`.
  - **Touchpoints**: Search Studio form → Paywall/Modal overlay → AJAX Feedback submisson → Credit Grant → Page refresh.
  - **Abandonment path**: User hits the paywall, clicks the upgrade link but abandons checkout, returns to Search Studio, and decides to submit feedback instead.

- **J-02: Paid/Standard User Search Exemption**
  - **Value**: A paying subscriber performs search queries without daily IP-based search limit blocks.
  - **Persona**: Power User.
  - **Charter**: CH-02.
  - **Test Case**: `TC-JOURNEY-002`.
  - **Touchpoints**: Account Plan status → Search Studio form → Search Execution.

- **J-03: Multi-surface Theme Switching & Sync**
  - **Value**: A user switches appearance themes (Claro/Escuro/Sistema) in desktop or mobile viewports, observing immediate changes and preserved states without visual jumps (FOUC).
  - **Persona**: Mobile User / Accessibility-Reliant User.
  - **Charter**: CH-03.
  - **Test Case**: `TC-JOURNEY-003`.
  - **Touchpoints**: Base HTML header → Navbar theme dropdown → Mobile floating theme control.

- **J-04: Kanban Board Card Height Uniformity**
  - **Value**: A sales rep scans the pipeline columns, dragging cards across stages, with cards maintaining standard heights regardless of stage card count.
  - **Persona**: Power User.
  - **Charter**: CH-04.
  - **Test Case**: `TC-JOURNEY-004`.
  - **Touchpoints**: Sales CRM page → Drag-and-drop actions.

---

## Charters Planned

- **CH-01: New User × Limit & Feedback Tour × 30min** on `/leads/search/` (test rate limits, modal appearance, AJAX feedback form, credit increment, and double-claim block).
- **CH-02: Power User × High Volume Tour × 30min** on `/leads/search/` (test paid account queries up to 5 times to ensure no IP locks block paid users).
- **CH-03: Mobile User × Theme Sync & FOUC Tour × 30min** on all views (test responsiveness of dropdown in navbar vs mobile floating control, page-reload FOUC prevention, system theme sync).
- **CH-04: Power User × Pipeline Visual Tour × 30min** on `/leads/crm/` (test dragging cards between columns with single vs multiple cards to verify strict height compliance of `176px` / `h-44`).

---

## CFR Scope

- **Usability**: Yes — Verifies readable text contrast on dark mode (AA 4.5:1 ratio) and clear warning messages on limit modal.
- **Accessibility**: Yes — Verifies screen-reader readable error alerts and keyboard navigable modal inputs.
- **Perceived Performance**: Yes — Verifies that switching themes has no lag, and reloading pages does not produce white flashes (FOUC).
- **Compatibility**: Yes — Test navbar theme selectors on desktop vs floating theme control on mobile devices.
- **Error Recoverability**: Yes — AJAX feedback form error displays (e.g. empty message) and recoverability.
- **Production Parity**: Yes — Evaluates rate limits using actual client IPs.

---

## Test Strategy

- Tests will be executed manually or utilizing Playwright tests if integrated.
- Mocks will be bypassable to ensure database operations for `IPRequestLog` and `Feedback` are written correctly.

---

## Automation Strategy

- **TC-JOURNEY-001 (Rate Limit & Feedback)**: `E2E candidate` (critical billing/conversion path).
- **TC-JOURNEY-002 (Paid User Query)**: `E2E candidate` (critical bypass check).
- **TC-JOURNEY-003 (Theme Switching)**: `Manual-only` (visual-judgment and device-specific rendering).
- **TC-JOURNEY-004 (Kanban Height)**: `Manual-only` (visual layout alignment checks).

---

## Entry Criteria

- [ ] Build is reachable in a production-parity environment.
- [ ] Django test suite is green (`manage.py test` passes 45 tests).
- [ ] A test database or clean environment exists without pre-existing daily IP logs.
- [ ] Test accounts for standard/paid users and free users are prepared.

---

## Exit Criteria

- [ ] Every J-NN journey successfully reaches its goal observable.
- [ ] Zero open `Blocks-Completion` or `Data-Loss` bugs.
- [ ] Visual verification of dark theme colors and contrast.
- [ ] Verification report compiled at `/home/thiago/www/micro-saas/lead-scout-ai/qa/verification-report.md`.

---

## Retesting vs Regression

- **Retesting**: Exercises the specific fixes (e.g., verifying that cards do not stretch in single-card stages, and that free users are blocked precisely after the 3rd query).
- **Regression**: Runs all 45 automated unit tests to ensure account creations, pipeline updates, and AI generating services remain uncorrupted.

---

## Risk Assessment

| Risk | Probability | User Impact | Mitigation |
|------|-------------|-------------|------------|
| Standard user gets blocked by IP rate limiter | low | Trust-Damage | View explicitly filters checks to `not user.is_active_plan`. Covered by `TC-JOURNEY-002`. |
| User bypasses rate limiter via browser cookie clean | low | Friction | Tracking is database-backed on IP, not cookie-based. |
| Double-submission of feedback triggers multiple credit grants | med | Friction | DB operations are atomic and check `received_feedback_bonus` column. Covered by `TC-JOURNEY-001`. |
| White flash occurs upon page load (FOUC) | med | Cosmetic | Base HTML loads FOUC blocking JS script in the `<head>` before body rendering. |

---

## Timeline and Deliverables

- Plan and Test Cases generated by: 2026-06-24
- Execution window: 2026-06-24 to 2026-06-25
- Verification report due: 2026-06-25

## TC-JOURNEY-002: Standard User Search Exemption

**Priority:** P0 (Critical)
**Type:** Journey
**Status:** Not Run
**Estimated Time:** 3 minutes
**Created:** 2026-06-24
**Last Updated:** 2026-06-24
**Persona:** Power User
**Journey:** J-02: Paid/Standard User Search Exemption
**Automation Target:** E2E
**Automation Status:** Missing
**Automation Command/Spec:** n/a
**Automation Notes:** Critical check to prevent paying users from encountering false-positive paywalls.

---

### Objective

Verify that a user with an active plan (e.g. Standard Plan) is completely exempt from the daily IP rate limiting of 3 requests, allowing them to search continuously as long as they have credits.

---

### Preconditions

- [ ] A Django user account exists belonging to an organization with 10 credits.
- [ ] The user has an active standard plan (a `UserPlan` record exists with status `ACTIVE`).
- [ ] No daily requests are logged for the IP, or the IP already has 3 requests logged from free users sharing the network.
- [ ] The user is logged in.

---

### Real-User Conditions

| Dimension | Value |
|-----------|-------|
| Network | wifi-fast |
| Device | desktop |
| Browser | Chrome |
| Locale | pt-BR |
| Timezone | America/Sao_Paulo |
| Autofill | empty |
| Modality | mouse-keyboard |

---

### Test Steps

1. **Navigate to Search Studio**
   - **Expected:** Search form is rendered. Credit balance badge shows "10". No paywall modal is displayed.

2. **Execute 4 consecutive search queries**
   - Input: Perform 4 queries with various niches and locations.
   - **Expected:** Every query succeeds, redirects to results, and decrements credits balance by 1.

3. **Verify Limit Modal Absence**
   - Action: Load the Search Studio page again after 4 queries.
   - **Expected:** The search inputs are active. The credits balance shows "6". No limit modal overlay is visible.

4. **Verify Database Logs**
   - Action: Query the backend `IPRequestLog` model for the current client IP address.
   - **Expected:** The count for the client's IP address remains unmodified (or 0 if no free users used the IP), proving that searches by active plan users do not increment the IP-based free logs.

---

### Edge Cases & Variations

| Variation | Action | Expected Result |
|-----------|--------|-----------------|
| Shared IP | A free user on the same IP is blocked, then the standard user logs in and searches | The standard user bypasses the block and searches successfully. |

---

### Post-conditions

- `IPRequestLog` count for this IP remains unchanged.
- Standard user credits balance is `6`.

---

### Related Test Cases

- TC-JOURNEY-001: Free User Daily Limit & AJAX Feedback Rescue

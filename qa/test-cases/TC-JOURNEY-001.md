## TC-JOURNEY-001: Free User Daily Limit & AJAX Feedback Rescue

**Priority:** P0 (Critical)
**Type:** Journey
**Status:** Not Run
**Estimated Time:** 5 minutes
**Created:** 2026-06-24
**Last Updated:** 2026-06-24
**Persona:** New User
**Journey:** J-01: Free User Daily Limit & AJAX Feedback Rescue
**Automation Target:** E2E
**Automation Status:** Missing
**Automation Command/Spec:** n/a
**Automation Notes:** Highly critical business and conversion flow. Should be automated in Playwright or Cypress.

---

### Objective

Verify that an un-subscribed (free) user is restricted to exactly 3 search requests per day by IP, sees the marketing/paywall pop-up on the 4th search query (or on reload), can submit a feedback text via AJAX to immediately gain 5 credits, and cannot exploit the system to gain multiple credit bonuses.

---

### Preconditions

- [ ] A Django user account exists belonging to an organization with 10 credits.
- [ ] The user account does not have an active plan (no `UserPlan` or status is cancelled).
- [ ] No daily requests have been logged today for the client IP address in the `IPRequestLog` table.
- [ ] The user is logged in.

---

### Real-User Conditions

| Dimension | Value |
|-----------|-------|
| Network | wifi-fast |
| Device | laptop |
| Browser | Chrome |
| Locale | pt-BR |
| Timezone | America/Sao_Paulo |
| Autofill | empty |
| Modality | mouse-keyboard |

---

### Test Steps

1. **Navigate to Search Studio**
   - **Expected:** Search form is rendered normally. Credits balance badge shows "10".

2. **Execute 3 consecutive successful search queries**
   - Input: Nicho: "Restaurantes", Localizacao: "Natal - RN". Click "Realizar Busca".
   - **Expected:** Each search takes the user to the results page, decrements credits balance by 1, and returns to the search page. The 3rd query executes successfully. Credits balance is now 7.

3. **Try to perform a 4th query or reload the Search Studio page**
   - **Expected:** A glassmorphic modal overlay appears instantly. The background page is blurred (`backdrop-blur-md`). The modal displays: "Limite Diário Atingido! Você atingiu o limite máximo de 3 buscas gratuitas por IP hoje". The search form inputs and button are disabled and visually faded.

4. **Verify Marketing Pitch & CTA**
   - **Expected:** A highlight section explains the benefits of the Standard Plan. A large green CTA button "Fazer Upgrade para Plano Standard (Buscas Ilimitadas)" is visible and links to `/accounts/planos/`.

5. **Submit Feedback to Claim Bonus Credits**
   - Input: Textarea filled with: "Ferramenta muito boa, mas gostaria de exportar relatórios em PDF." Click "Enviar Feedback e Resgatar +5 Créditos".
   - **Expected:** Submit button changes text to "Processando..." and disables. Once complete, a green success message appears: "Muito obrigado pelo seu feedback! Concedemos 5 créditos adicionais para você na hora." The modal disappears and the page reloads after 2 seconds. The new credits balance shows "12" and the search form is unlocked.

6. **Verify Double-Claim Block**
   - Action: Execute another 3 queries until the rate limit is hit again. Reload the page to trigger the modal.
   - **Expected:** The limit modal overlay appears. However, the feedback submission textarea and button are hidden (since `received_feedback_bonus` is True on the Organization). Only the upgrade CTA is visible.

---

### Edge Cases & Variations

| Variation | Action | Expected Result |
|-----------|--------|-----------------|
| Clear cookies | Clear browser local storage/cookies and reload page | The modal remains visible because tracking is IP-based in the database. |
| Submit empty feedback | Leave feedback textarea empty and click submit | Browser blocks submit via HTML5 `required` attribute. |

---

### Post-conditions

- `IPRequestLog` has a row for client IP with `count = 6`.
- `Feedback` has a text row for user.
- Organization has `received_feedback_bonus = True` and `credits_balance = 9`.
- Clean up: Delete daily `IPRequestLog` entries for client IP.

---

### Related Test Cases

- TC-JOURNEY-002: Standard User Search Exemption

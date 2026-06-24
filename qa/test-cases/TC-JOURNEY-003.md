## TC-JOURNEY-003: Multi-surface Theme Switching & Sync

**Priority:** P1 (High)
**Type:** CFR
**CFR Category:** Usability | Perceived-Performance | Compatibility
**Status:** Not Run
**Estimated Time:** 4 minutes
**Created:** 2026-06-24
**Last Updated:** 2026-06-24
**Persona:** Mobile User
**Journey:** J-03: Multi-surface Theme Switching & Sync
**Automation Target:** Manual-only
**Automation Status:** N/A
**Automation Notes:** Visual aesthetics, dark mode transitions, and device orientation sync checks are highly subjective and best validated manually.

---

### Objective

Verify that a user can switch appearance themes (Claro, Escuro, Sistema) seamlessly on both desktop (via the navbar dropdown) and mobile/logged-out views (via the floating widget), that the visual appearance adapts instantly with clean CSS transitions, that states are synchronized across controls, and that reloading pages does not trigger a white screen flash (FOUC) in dark mode.

---

### Preconditions

- [ ] A user account exists.
- [ ] User is logged in (to test navbar sync) or logged out (to test floating toggle).

---

### Real-User Conditions

| Dimension | Value |
|-----------|-------|
| Network | wifi-fast |
| Device | phone-large |
| Browser | iOS Safari |
| Locale | pt-BR |
| Timezone | America/Sao_Paulo |
| Autofill | empty |
| Modality | touch |

---

### Test Steps

1. **Observe Default State (System Match)**
   - Action: Load the dashboard page with OS theme set to Dark.
   - **Expected:** Page loads in Dark Mode. The navbar dropdown shows the monitor/computer icon selected ("Sistema"). No white page flash occurs during loading.

2. **Switch to Light Mode (Desktop Viewport)**
   - Action: Open the theme selector in the top-right navbar. Select "Claro" (Sun icon).
   - **Expected:** Interface smoothly transitions to light colors (light slate backgrounds, dark slate text). Sun icon becomes selected. LocalStorage `theme` key changes to `"light"`.

3. **Switch to Dark Mode (Desktop Viewport)**
   - Action: Open the theme selector. Select "Escuro" (Moon icon).
   - **Expected:** Interface transitions smoothly (`transition-colors duration-300`) to dark colors (slate-950 background, white text). Moon icon becomes selected. LocalStorage `theme` key changes to `"dark"`.

4. **Verify Mobile Theme Sync**
   - Action: Resize the viewport to mobile resolution (375px).
   - **Expected:** Desktop navbar is hidden. A floating theme toggle button with a moon icon is visible in the top-right corner of the layout.
   - Action: Tap the floating toggle button. Select "Claro".
   - **Expected:** Page changes to light mode. Floating toggle button updates icon to a sun.
   - Action: Resize back to desktop.
   - **Expected:** Navbar dropdown is visible again and its selection has successfully synchronized to "Claro".

5. **Verify FOUC (Flash of Unstyled Content) Prevention**
   - Action: Keep the theme set to "Escuro". Reload the page (`Ctrl + R` or command refresh).
   - **Expected:** The page loads directly in dark mode. No transient white flashes or unstyled light backgrounds are observed during the load process.

---

### Checklist (from cfr-checks.md)

- [ ] Text contrast meets AA 4.5:1 ratio on both Light and Dark modes.
- [ ] Transition animations between themes are between 150ms and 300ms.
- [ ] Theme configuration is preserved after closing the browser tab and returning.

---

### Related Test Cases

- TC-JOURNEY-004: Kanban Board Card Height Uniformity

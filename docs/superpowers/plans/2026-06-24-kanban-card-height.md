# Padronização de Altura dos Cards do Kanban Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Padronizar a altura vertical dos cards do Kanban no desktop e mobile, impedindo que ocupem toda a coluna quando sozinhos.

**Architecture:** Modificação das classes do elemento raiz no template Django de card para usar altura fixa (`md:h-44`) no desktop e dinâmica (`h-auto`) no mobile.

**Tech Stack:** Tailwind CSS (via CDN), Django templates.

## Global Constraints

- Utilizar classes Tailwind CSS nativas.
- Respeitar responsividade e visual do CRM.

---

### Task 1: Alteração da classe do card do Kanban

**Files:**
- Modify: `templates/leads/crm_card_snippet.html:1-7`
- Test: `leads/tests/test_crm.py` (ou rodar a suite padrão para garantir que nada quebrou)

**Interfaces:**
- Consumes: Nenhuma
- Produces: Card de lead com tamanho padronizado.

- [ ] **Step 1: Modificar a classe de altura do card**

Substituir o elemento div na linha 1 do arquivo `templates/leads/crm_card_snippet.html`.

Código anterior:
```html
<div class="relative bg-white dark:bg-slate-950 p-4 rounded-xl ring-1 ring-slate-200/50 dark:ring-white/10 hover:ring-emerald-500/50 dark:hover:ring-emerald-500/50 transition-all shadow-md dark:shadow-lg cursor-pointer flex flex-col justify-between h-full text-slate-800 dark:text-slate-100"
```

Novo código:
```html
<div class="relative bg-white dark:bg-slate-950 p-4 rounded-xl ring-1 ring-slate-200/50 dark:ring-white/10 hover:ring-emerald-500/50 dark:hover:ring-emerald-500/50 transition-all shadow-md dark:shadow-lg cursor-pointer flex flex-col justify-between h-auto md:h-44 text-slate-800 dark:text-slate-100"
```

- [ ] **Step 2: Rodar os testes para validar que nada foi corrompido no backend**

Run: `./.venv/bin/python manage.py test`
Expected output: `Ran 42 tests in ... OK`

- [ ] **Step 3: Commit**

```bash
git add templates/leads/crm_card_snippet.html docs/superpowers/specs/2026-06-24-kanban-card-height-design.md
git commit -m "style(crm): standardize kanban card height to md:h-44 and h-auto"
```

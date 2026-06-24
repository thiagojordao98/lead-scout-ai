# Plano de Transição: Paleta Verde Neon Dark Mode (V2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Alterar toda a identidade visual e a paleta de cores do LeadScout AI para um verde neon futurista e high-tech, mantendo a estética dark-mode (Glassmorphism e Glows sutis) de acordo com os padrões da especificação V2.

**Architecture:** A transição de cores substituirá os tons anteriores de azul/indigo/fuchsia/pink/purple por tons de verde neon, esmeralda, menta e limão (`emerald-400`, `green-400`, `lime-400`, `teal-400`). Alteraremos o arquivo global de layout (`base.html`), os templates de autenticação, o dashboard, a landing page, o search studio, os resultados da busca e o Kanban de CRM (incluindo snippets e modais).

**Tech Stack:** Django Templates, Tailwind CSS (v3 via CDN), Vanilla JS / Alpine.js.

## Global Constraints

* **Fundo Radial:** `from-emerald-950/20 via-slate-950 to-black` (efeito de luz neon no topo).
* **Gradiente de Destaque (Glow CTAs):** `from-emerald-500 via-lime-400 to-emerald-500`.
* **Cor de Foco de Inputs:** `focus:ring-emerald-500` (removendo `focus:ring-indigo-500`).
* **Elementos de Destaque (Badges/Ícones):** `bg-emerald-500/10 ring-1 ring-emerald-500/30 text-emerald-400`.
* **Cor de Seleção de Texto:** `selection:bg-emerald-500/30`.

---

### Task 1: base.html e Configuração Global de Cores

**Files:**
- Modify: `templates/base.html`

**Interfaces:**
- Consumes: Estrutura HTML do base.html com estilos antigos (indigo/purple).
- Produces: Estilos base em verde neon, navbar e bottom navigation atualizados.

- [ ] **Step 1: Atualizar a tag `<body>` e o gradiente radial de `<main>`**
  
  Mudar o padrão de seleção para `selection:bg-emerald-500/30` no `body` e o gradiente radial do topo de `<main>` para usar `from-emerald-950/20` (ou `/30`) em vez de `from-slate-900`.
  
  ```html
  <body class="{% block body_class %}min-h-screen bg-slate-950 text-slate-200 font-sans antialiased selection:bg-emerald-500/30{% endblock %}">
  ```
  *(Ajustar também o gradiente radial do `<main>`)*:
  ```html
  <main class="mx-auto flex min-h-screen w-full max-w-7xl items-center justify-center p-4 md:p-6 {% if user.is_authenticated %}pt-20 pb-24 md:pb-6{% else %}pt-6 pb-6{% endif %} bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-950/20 via-slate-950 to-black">
  ```

- [ ] **Step 2: Atualizar Navbar Desktop**
  
  Substituir o gradiente de cores da logo/nome do aplicativo de `from-indigo-400 via-purple-400 to-pink-400` para `from-emerald-400 via-green-400 to-lime-400` e as classes de hover dos links para `hover:text-emerald-400`.
  
  ```html
  <span class="font-extrabold bg-gradient-to-r from-emerald-400 via-green-400 to-lime-400 bg-clip-text text-transparent text-lg">LeadScout AI</span>
  ```
  *(Ajustar links do menu para `hover:text-emerald-400`)*

- [ ] **Step 3: Atualizar Bottom Navigation Mobile**
  
  Alterar a classe de hover/active dos links do menu mobile de `hover:text-indigo-400` para `hover:text-emerald-400`.
  
  ```html
  <a href="{% url 'leads:search_studio' %}" class="flex flex-col items-center gap-1.5 text-slate-400 hover:text-emerald-400 transition">
  ```

- [ ] **Step 4: Executar testes de sanidade**
  
  Run: `.venv/bin/python manage.py test accounts`
  Expected: PASS

---

### Task 2: Atualização de Cores nos Formulários de Autenticação (Auth)

**Files:**
- Modify: `templates/accounts/login.html`
- Modify: `templates/accounts/register.html`
- Modify: `templates/accounts/password_reset_form.html`
- Modify: `templates/accounts/password_reset_confirm.html`
- Modify: `templates/accounts/password_reset_done.html`
- Modify: `templates/accounts/password_reset_complete.html`

**Interfaces:**
- Consumes: Classes de estilo de auth com botões e focos baseados em `indigo` e `fuchsia`.
- Produces: Formulários de login e recuperação de senha com foco de inputs e botões em verde neon.

- [ ] **Step 1: Refatorar o foco dos campos de Input**
  
  Substituir as classes de foco nos inputs de todos os arquivos de formulário:
  De: `focus:ring-indigo-500`
  Para: `focus:ring-emerald-500`

- [ ] **Step 2: Atualizar os Botões com Glow**
  
  Mudar o gradiente do botão principal com glow em `login.html`, `register.html`, `password_reset_form.html` e `password_reset_confirm.html`:
  De: `from-indigo-500 via-fuchsia-500 to-indigo-500`
  Para: `from-emerald-500 via-lime-400 to-emerald-500`

- [ ] **Step 3: Atualizar links secundários**
  
  Alterar a cor dos links secundários (como "Cadastre-se" ou "Recuperar senha") de `text-indigo-400 hover:text-indigo-300` para `text-emerald-400 hover:text-emerald-300`.

- [ ] **Step 4: Executar testes de sanidade das rotas de autenticação**
  
  Run: `.venv/bin/python manage.py test accounts`
  Expected: PASS

---

### Task 3: Dashboard e Tela de Planos / Pagamento

**Files:**
- Modify: `templates/accounts/dashboard.html`
- Modify: `templates/accounts/payments_settings.html`

**Interfaces:**
- Consumes: Painel de controle e tela de checkout com cor de destaque antiga.
- Produces: Dashboard futurista e tela de confirmação de planos no novo tom verde.

- [ ] **Step 1: Atualizar o Dashboard (`dashboard.html`)**
  
  *   Mudar o título em gradiente de `from-indigo-400 via-purple-400 to-pink-400` para `from-emerald-400 via-green-400 to-lime-400`.
  *   Mudar a cor de hover do contorno do card de `hover:border-indigo-500/50` para `hover:border-emerald-500/50`.
  *   Mudar o ícone do Search Studio de `bg-indigo-500/10 text-indigo-400` para `bg-emerald-500/10 text-emerald-400`.
  *   Mudar o ícone do Pipeline de `bg-purple-500/10 text-purple-400` para `bg-teal-500/10 text-teal-400`.

- [ ] **Step 2: Atualizar Tela de Planos (`payments_settings.html`)**
  
  *   Mudar o botão de voltar/dashboard de `bg-blue-600 hover:bg-blue-700` para a estrutura de botão com glow verde:
  
  ```html
  <a href="{% url 'accounts:dashboard' %}" class="relative group overflow-hidden rounded-lg p-[1px] inline-block mt-6">
      <span class="absolute inset-0 bg-gradient-to-r from-emerald-500 via-lime-400 to-emerald-500 opacity-70 group-hover:opacity-100 transition-opacity duration-300"></span>
      <div class="relative bg-slate-950 px-6 py-3 rounded-[7px] flex items-center justify-center transition-all group-hover:bg-opacity-0">
          <span class="font-semibold text-white">Tentar acessar dashboard novamente</span>
      </div>
  </a>
  ```

---

### Task 4: Landing Page de Vendas (`home.html`)

**Files:**
- Modify: `templates/pages/home.html`

**Interfaces:**
- Consumes: Landing page com a cópia comercial em tons de azul e fuchsia.
- Produces: Landing page totalmente ajustada com o novo padrão verde neon futurista.

- [ ] **Step 1: Atualizar efeitos de Glow de Fundo e Badges**
  
  *   Alterar a cor do Glow de fundo do Hero (linha 7) de `bg-indigo-600/20` para `bg-emerald-600/15`.
  *   Alterar o badge de lançamento de `bg-indigo-500/10 ring-indigo-500/30 text-indigo-400` para `bg-emerald-500/10 ring-emerald-500/30 text-emerald-400`.
  *   Mudar a cor da bolinha animada do badge de `bg-indigo-500` para `bg-emerald-500`.

- [ ] **Step 2: Atualizar CTA Principal e Steps**
  
  *   Mudar o gradiente do botão CTA principal de `from-indigo-500 via-fuchsia-500 to-indigo-500` para `from-emerald-500 via-lime-400 to-emerald-500`.
  *   Mudar a cor da tag de créditos de `text-indigo-200 bg-white/10` para `text-emerald-200 bg-white/10`.
  *   Substituir o fundo de todos os ícones das colunas de "Como Funciona":
      *   De: `bg-indigo-500/10 ring-indigo-500/30 text-indigo-400`
      *   Para: `bg-emerald-500/10 ring-emerald-500/30 text-emerald-400`
      *   De: `bg-fuchsia-500/10 ring-fuchsia-500/30 text-fuchsia-400`
      *   Para: `bg-lime-500/10 ring-lime-500/30 text-lime-400`

- [ ] **Step 3: Atualizar Preços e Plano Pro**
  
  *   Mudar a cor dos ícones de verificação (V) nos planos de `text-indigo-400` para `text-emerald-400`.
  *   No Plano Pro: Mudar o Glow Blob de fundo de `from-indigo-500 to-fuchsia-500` para `from-emerald-500 to-lime-400`.
  *   Mudar o badge de "Recomendado" do Plano Pro de `from-indigo-500 to-fuchsia-500` para `from-emerald-500 to-lime-400`.
  *   Mudar o gradiente do botão "Assinar Agora" de `from-indigo-500 via-fuchsia-500 to-indigo-500` para `from-emerald-500 via-lime-400 to-emerald-500`.

- [ ] **Step 4: Executar testes de sanidade da página**
  
  Run: `.venv/bin/python manage.py test accounts`
  Expected: PASS

---

### Task 5: Refatoração do Search Studio e Resultados

**Files:**
- Modify: `templates/leads/search_studio.html`
- Modify: `templates/leads/search_results.html`

**Interfaces:**
- Consumes: Página de busca com gradientes e botões antigos.
- Produces: Página de busca e listagem de resultados com tons de verde neon.

- [ ] **Step 1: Refatorar o Search Studio (`search_studio.html`)**
  
  *   Mudar o Glow de fundo de `from-indigo-500/20 to-purple-500/20` para `from-emerald-500/15 to-green-500/15`.
  *   Mudar o ícone de busca no topo de `bg-indigo-500/10 ring-indigo-500/30 text-indigo-400` para `bg-emerald-500/10 ring-emerald-500/30 text-emerald-400`.
  *   Mudar o gradiente do botão principal de submit de `from-indigo-500 via-fuchsia-500 to-indigo-500` para `from-emerald-500 via-lime-400 to-emerald-500`.
  *   Mudar o foco dos inputs de `focus:ring-indigo-500` para `focus:ring-emerald-500`.

- [ ] **Step 2: Refatorar a Listagem de Resultados (`search_results.html`)**
  
  *   Mudar o ícone animado e o texto de progresso de `text-indigo-400` e `bg-indigo-500` para `text-emerald-400` e `bg-emerald-500`.
  *   Mudar o gradiente do nome da consulta (nicho) de `from-indigo-400 via-purple-400 to-pink-400` para `from-emerald-400 via-green-400 to-lime-400` (se aplicável, ou manter text-white padrão).
  *   Mudar o botão de nova busca de `bg-slate-800 hover:bg-slate-700` para ter hover verde: `hover:border-emerald-500/50`.
  *   Nos cards de lead:
      *   Mudar a tag "Hot" de `from-red-500/20 to-orange-500/20 text-orange-400 border-orange-500/30` para `from-rose-500/20 to-red-500/20 text-rose-400 border-rose-500/30`.
      *   Mudar links de "Website" e badges de "E-mail Profissional" de `text-indigo-400 bg-indigo-500/10` para `text-emerald-400 bg-emerald-500/10`.
      *   Mudar o botão "Adicionar ao CRM" de `bg-indigo-600 hover:bg-indigo-700` para `bg-emerald-600 hover:bg-emerald-700`.

---

### Task 6: Refatoração do Mini-CRM Kanban e Modal de Detalhes

**Files:**
- Modify: `templates/leads/crm_kanban.html`
- Modify: `templates/leads/crm_card_snippet.html`
- Modify: `templates/leads/lead_detail_modal.html`

**Interfaces:**
- Consumes: Kanban e Modal de Detalhes com referências a cores de destaque antigas.
- Produces: CRM Kanban e Modal de Detalhes com tons de verde neon futurista.

- [ ] **Step 1: Ajustar Kanban (`crm_kanban.html`)**
  
  *   Mudar o título em gradiente de `from-indigo-400 via-purple-400 to-pink-400` para `from-emerald-400 via-green-400 to-lime-400`.
  *   Mudar a cor ativa dos botões de abas do mobile (Passo 1/3) de `bg-indigo-600` para `bg-emerald-600`.
  *   Mudar o botão de Nova Busca de `bg-indigo-600 hover:bg-indigo-700` para `bg-emerald-600 hover:bg-emerald-700`.
  *   Mudar o efeito de dragover das colunas de `rgba(99, 102, 241, 0.08)` / `border-color` para `rgba(16, 185, 129, 0.08)` / `rgba(16, 185, 129, 0.4)`.

- [ ] **Step 2: Ajustar Snippet de Card de Lead (`crm_card_snippet.html`)**
  
  *   Mudar o hover de contorno do card de `hover:border-indigo-500/50` para `hover:border-emerald-500/50`.
  *   Mudar a cor dos ícones de e-mail e links de website de `text-indigo-400` para `text-emerald-400`.
  *   Mudar o foco do select mobile de `focus:ring-indigo-500` para `focus:ring-emerald-500`.

- [ ] **Step 3: Ajustar Modal de Detalhes (`lead_detail_modal.html`)**
  
  *   Mudar o título em gradiente de `from-indigo-400 via-purple-400 to-pink-400` para `from-emerald-400 via-green-400 to-lime-400`.
  *   Mudar a bolinha animada de `bg-indigo-500` para `bg-emerald-500`.
  *   Mudar o botão "Gerar Roteiro" com glow de `from-indigo-500 via-fuchsia-500 to-indigo-500` para `from-emerald-500 via-lime-400 to-emerald-500`.
  *   Mudar o indicador de carregamento (spinner) de `border-indigo-500` para `border-emerald-500`.

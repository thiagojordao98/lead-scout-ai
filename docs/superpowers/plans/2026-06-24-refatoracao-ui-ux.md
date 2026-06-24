# Refatoração UI/UX Premium (V2) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refatorar a interface do LeadScout AI para o padrão "Premium SaaS Dark Mode", otimizada para mobile e com uma estética moderna de Deep Dark & Subtle Neon (Glassmorphism e Glows translúcidos).

**Architecture:** A refatoração será feita alterando o arquivo base de templates (`base.html`), configurando os estilos globais através de uma tag `<style>` integrada com o Tailwind CSS via CDN. Em seguida, os estilos padrão de Cards, Inputs e Botões com Glow serão aplicados a todos os templates existentes (Login, Registro, Dashboard, Busca, Resultados, Kanban e Modal de Detalhes). Será criada uma nova Landing Page de vendas moderna e as rotas serão ajustadas para direcionar a página inicial para ela.

**Tech Stack:** Django (templates HTML), Tailwind CSS (v3 via CDN), Vanilla JS (para interações de UI mobile), Alpine.js (opcional/para interações e navegação Kanban mobile).

## Global Constraints

* **Fundos:** Proibido o uso de cinzas ou azuis opacos para o fundo principal. Utilizar `bg-slate-950` ou `bg-black`.
* **Bordas:** Eliminar bordas pesadas (`border-slate-700` ou `border-2`). Substituir por anéis translúcidos (`ring-1 ring-white/5` ou `ring-white/10`).
* **Tipografia:** Textos secundários nunca devem ser brancos. Usar `text-slate-400` ou `text-slate-500` para criar hierarquia visual.
* **Acessibilidade / Mobile:** Todos os botões e áreas de toque no mobile devem ter no mínimo `44px` de altura (ex: `py-3`).

---

### Task 1: Configuração Global e `base.html`

**Files:**
- Modify: `templates/base.html`

**Interfaces:**
- Consumes: Estrutura HTML original do Django
- Produces: Layout base com suporte a fontes modernas, radial gradient e navegação mobile/desktop dinâmica.

- [ ] **Step 1: Atualizar fontes e estilos globais no `<head>`**
  
  Modificar a seção `<head>` do arquivo `templates/base.html` para importar a fonte *Plus Jakarta Sans* e configurar uma tag `<style>` personalizada para definir a família tipográfica padrão e estilizar a barra de rolagem.
  
  ```html
  <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{% block title %}LeadScout AI{% endblock %}</title>
      <script src="https://cdn.tailwindcss.com"></script>
      <link rel="preconnect" href="https://fonts.googleapis.com">
      <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
      <style>
          body {
              font-family: 'Plus Jakarta Sans', sans-serif;
          }
          /* Custom scrollbar para preservar estética dark */
          ::-webkit-scrollbar {
              width: 6px;
              height: 6px;
          }
          ::-webkit-scrollbar-track {
              background: #020617;
          }
          ::-webkit-scrollbar-thumb {
              background: #1e293b;
              border-radius: 9999px;
          }
          ::-webkit-scrollbar-thumb:hover {
              background: #334155;
          }
      </style>
  </head>
  ```

- [ ] **Step 2: Configurar o Body e Container Principal com Gradiente Radial**
  
  Atualizar a tag `<body>` e o `<main>` de `templates/base.html` para usar o gradiente radial profundo e suportar os novos estilos globais.
  
  ```html
  <body class="{% block body_class %}min-h-screen bg-slate-950 text-slate-200 font-sans antialiased selection:bg-indigo-500/30{% endblock %}">
      <!-- Navbar Desktop -->
      {% if user.is_authenticated %}
      <nav class="hidden md:flex items-center justify-between py-4 px-8 bg-slate-950/40 backdrop-blur-md border-b border-white/5 fixed top-0 left-0 right-0 z-50">
          <div class="flex items-center gap-2">
              <span class="font-extrabold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent text-lg">LeadScout AI</span>
          </div>
          <div class="flex items-center gap-8">
              <a href="{% url 'leads:search_studio' %}" class="text-sm font-medium text-slate-400 hover:text-white transition">Search Studio</a>
              <a href="{% url 'leads:crm_kanban' %}" class="text-sm font-medium text-slate-400 hover:text-white transition">CRM Kanban</a>
              <a href="{% url 'accounts:payments_settings' %}" class="text-sm font-medium text-slate-400 hover:text-white transition">Planos</a>
              <a href="{% url 'accounts:dashboard' %}" class="text-sm font-medium text-slate-400 hover:text-white transition">Dashboard</a>
          </div>
          <div class="flex items-center gap-4">
              <span class="text-xs text-slate-505">{{ user.email }}</span>
              <a href="{% url 'accounts:logout' %}" class="text-xs font-semibold text-rose-400 hover:text-rose-300 transition">Sair</a>
          </div>
      </nav>
      {% endif %}

      <main class="mx-auto flex min-h-screen w-full max-w-7xl items-center justify-center p-4 md:p-6 pt-20 pb-24 md:pb-6 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black">
          <div class="{% block wrapper_class %}w-full max-w-md relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6 md:p-8 shadow-2xl text-white{% endblock %}">
              {% if messages %}
                  <div class="mb-4 space-y-2">
                      {% for message in messages %}
                          <div class="rounded-lg bg-indigo-500/10 ring-1 ring-indigo-500/30 px-4 py-3 text-sm text-indigo-300 flex items-center gap-2">
                              <span class="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse"></span>
                              {{ message }}
                          </div>
                      {% endfor %}
                  </div>
              {% endif %}
              {% block content %}{% endblock %}
          </div>
      </main>

      <!-- Bottom Nav Mobile -->
      {% if user.is_authenticated %}
      <div class="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-slate-950/80 backdrop-blur-lg border-t border-white/5 px-6 py-4 flex justify-around items-center">
          <a href="{% url 'leads:search_studio' %}" class="flex flex-col items-center gap-1.5 text-slate-400 hover:text-indigo-400 transition">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span class="text-[10px] font-medium tracking-wide">Busca</span>
          </a>
          <a href="{% url 'leads:crm_kanban' %}" class="flex flex-col items-center gap-1.5 text-slate-400 hover:text-indigo-400 transition">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2" />
              </svg>
              <span class="text-[10px] font-medium tracking-wide">CRM</span>
          </a>
          <a href="{% url 'accounts:payments_settings' %}" class="flex flex-col items-center gap-1.5 text-slate-400 hover:text-indigo-400 transition">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
              <span class="text-[10px] font-medium tracking-wide">Planos</span>
          </a>
      </div>
      {% endif %}
  </body>
  ```

- [ ] **Step 3: Executar testes de sanidade da base**
  
  Run: `.venv/bin/python manage.py test accounts.tests`
  Expected: PASS

---

### Task 2: Componentização de UI (Cards, Inputs e CTAs) nos formulários de Autenticação

**Files:**
- Modify: `templates/accounts/login.html`
- Modify: `templates/accounts/register.html`
- Modify: `templates/accounts/password_reset_form.html`
- Modify: `templates/accounts/password_reset_confirm.html`
- Modify: `templates/accounts/password_reset_done.html`
- Modify: `templates/accounts/password_reset_complete.html`

**Interfaces:**
- Consumes: Estilo base das páginas de auth do Django.
- Produces: Telas de autenticação refatoradas de acordo com as especificações globais de design.

- [ ] **Step 1: Refatorar o Formulário de Login**
  
  Atualizar `templates/accounts/login.html` para aplicar o padrão de inputs escuros e botões com Glow, além de definir textos secundários como `text-slate-400`.
  
  ```html
  {% extends "base.html" %}
  {% block title %}Entrar - LeadScout AI{% endblock %}
  {% block content %}
  <h1 class="mb-2 text-2xl font-extrabold tracking-tight text-white bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">Entrar</h1>
  <p class="mb-6 text-sm text-slate-400">Acesse sua conta usando seu e-mail.</p>
  <form method="post" class="space-y-4">
      {% csrf_token %}
      {% if form.non_field_errors %}
          <div class="rounded-lg bg-red-500/10 ring-1 ring-red-500/30 px-3 py-2 text-sm text-red-400">
              {{ form.non_field_errors }}
          </div>
      {% endif %}
      <div>
          <label class="mb-1 block text-sm font-medium text-slate-300" for="{{ form.email.id_for_label }}">E-mail</label>
          <input type="email" name="{{ form.email.name }}" id="{{ form.email.id_for_label }}" value="{{ form.email.value|default:'' }}" required class="w-full bg-black/50 ring-1 ring-white/5 border-0 rounded-lg px-4 py-3 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:bg-slate-900/50 transition-all">
      </div>
      <div>
          <label class="mb-1 block text-sm font-medium text-slate-300" for="{{ form.password.id_for_label }}">Senha</label>
          <input type="password" name="{{ form.password.name }}" id="{{ form.password.id_for_label }}" required class="w-full bg-black/50 ring-1 ring-white/5 border-0 rounded-lg px-4 py-3 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:bg-slate-900/50 transition-all">
      </div>
      <button class="relative group overflow-hidden rounded-lg p-[1px] w-full block mt-6">
          <span class="absolute inset-0 bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-indigo-500 opacity-70 group-hover:opacity-100 transition-opacity duration-300"></span>
          <div class="relative bg-slate-950 px-4 py-3 rounded-[7px] flex items-center justify-center transition-all group-hover:bg-opacity-0">
              <span class="font-semibold text-white">Entrar</span>
          </div>
      </button>
  </form>
  <p class="mt-6 text-sm text-slate-400">
      Ainda não tem conta?
      <a class="font-medium text-indigo-400 hover:text-indigo-300 transition hover:underline" href="{% url 'accounts:register' %}">Cadastre-se</a>
  </p>
  <p class="mt-2 text-sm text-slate-400">
      Esqueceu a senha?
      <a class="font-medium text-indigo-400 hover:text-indigo-300 transition hover:underline" href="{% url 'accounts:password_reset' %}">Recuperar senha</a>
  </p>
  {% endblock %}
  ```

- [ ] **Step 2: Refatorar o Formulário de Cadastro**
  
  Atualizar `templates/accounts/register.html` seguindo o mesmo estilo do login.
  
  ```html
  {% extends "base.html" %}
  {% block title %}Criar Conta - LeadScout AI{% endblock %}
  {% block content %}
  <h1 class="mb-2 text-2xl font-extrabold tracking-tight text-white bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">Criar Conta</h1>
  <p class="mb-6 text-sm text-slate-400">Cadastre-se para começar a buscar leads qualificados.</p>
  <form method="post" class="space-y-4">
      {% csrf_token %}
      {% if form.non_field_errors %}
          <div class="rounded-lg bg-red-500/10 ring-1 ring-red-500/30 px-3 py-2 text-sm text-red-400">
              {{ form.non_field_errors }}
          </div>
      {% endif %}
      {% for field in form %}
      <div>
          <label class="mb-1 block text-sm font-medium text-slate-300" for="{{ field.id_for_label }}">{{ field.label }}</label>
          <input type="{{ field.field.widget.input_type|default:'text' }}" name="{{ field.name }}" id="{{ field.id_for_label }}" value="{{ field.value|default:'' }}" {% if field.field.required %}required{% endif %} class="w-full bg-black/50 ring-1 ring-white/5 border-0 rounded-lg px-4 py-3 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:bg-slate-900/50 transition-all">
          {% if field.errors %}
              <p class="mt-1 text-xs text-rose-400">{{ field.errors.as_text }}</p>
          {% endif %}
      </div>
      {% endfor %}
      <button class="relative group overflow-hidden rounded-lg p-[1px] w-full block mt-6">
          <span class="absolute inset-0 bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-indigo-500 opacity-70 group-hover:opacity-100 transition-opacity duration-300"></span>
          <div class="relative bg-slate-950 px-4 py-3 rounded-[7px] flex items-center justify-center transition-all group-hover:bg-opacity-0">
              <span class="font-semibold text-white">Criar Conta</span>
          </div>
      </button>
  </form>
  <p class="mt-6 text-sm text-slate-400">
      Já tem uma conta?
      <a class="font-medium text-indigo-400 hover:text-indigo-300 transition hover:underline" href="{% url 'accounts:login' %}">Faça login</a>
  </p>
  {% endblock %}
  ```

- [ ] **Step 3: Refatorar Telas de Recuperação de Senha**
  
  Aplicar o mesmo estilo de inputs, botões e cores de fontes aos arquivos:
  - `templates/accounts/password_reset_form.html`
  - `templates/accounts/password_reset_confirm.html`
  - `templates/accounts/password_reset_done.html`
  - `templates/accounts/password_reset_complete.html`

- [ ] **Step 4: Executar testes de sanidade das rotas de autenticação**
  
  Run: `.venv/bin/python manage.py test accounts.tests`
  Expected: PASS

---

### Task 3: Nova Landing Page de Vendas (Alta Conversão)

**Files:**
- Create: `templates/pages/home.html`
- Modify: `core/urls.py`

**Interfaces:**
- Consumes: Acesso público via `/` (URL raiz).
- Produces: Uma landing page dark premium que incentiva o cadastro/login.

- [ ] **Step 1: Modificar as rotas em `core/urls.py`**
  
  Importar `TemplateView` e alterar a rota inicial `""` para renderizar `pages/home.html` em vez de redirecionar para o login.
  
  ```python
  from django.contrib import admin
  from django.conf import settings
  from django.urls import include, path
  from django.views.generic import TemplateView
  
  urlpatterns = [
      path('', TemplateView.as_view(template_name='pages/home.html'), name='home'),
      path('admin/', admin.site.urls),
      path("auth/", include("accounts.urls")),
      path("webhooks/", include("plans.urls")),
      path("leads/", include("leads.urls")),
  ]
  ```

- [ ] **Step 2: Criar a Landing Page `templates/pages/home.html`**
  
  Criar o arquivo `templates/pages/home.html` estendendo `base.html`, definindo o `wrapper_class` como transparente e ocupando a largura total permitida no desktop (`max-w-5xl`).
  
  ```html
  {% extends "base.html" %}
  {% block title %}LeadScout AI - Encontre Leads e Audite Presença Digital{% endblock %}
  {% block wrapper_class %}w-full max-w-5xl bg-transparent p-0 shadow-none ring-0 border-0 text-white{% endblock %}
  {% block content %}
  <div class="space-y-24 py-12">
      <!-- Hero Section -->
      <section class="text-center px-4 pt-16 pb-12 relative">
          <!-- Glow Blob sutil atrás do Hero -->
          <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-indigo-500/10 rounded-full blur-[120px] pointer-events-none"></div>
          
          <h1 class="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-slate-400 max-w-4xl mx-auto">
              Encontre leads qualificados e audite a presença digital deles em segundos
          </h1>
          <p class="text-slate-400 text-lg md:text-xl max-w-2xl mx-auto mt-6">
              O LeadScout AI varre o Google Maps, analisa certificados SSL, detecta e-mails comerciais e automatiza seu processo de prospecção fria.
          </p>
          <div class="mt-10 max-w-xs mx-auto">
              <a href="{% url 'accounts:register' %}" class="relative group overflow-hidden rounded-lg p-[1px] w-full block shadow-[0_0_30px_rgba(79,70,229,0.3)] transition hover:shadow-indigo-500/40">
                  <span class="absolute inset-0 bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-indigo-500 opacity-90 group-hover:opacity-100 transition-opacity duration-300"></span>
                  <div class="relative bg-slate-950 px-6 py-4 rounded-[7px] flex items-center justify-center transition-all group-hover:bg-opacity-0">
                      <span class="font-bold text-white text-base">Começar Agora Grátis</span>
                  </div>
              </a>
          </div>
      </section>

      <!-- Como Funciona Grid -->
      <section class="space-y-12">
          <div class="text-center space-y-3">
              <h2 class="text-3xl font-bold tracking-tight">Como Funciona o Mecanismo</h2>
              <p class="text-slate-400 max-w-md mx-auto">Do nicho de mercado à abordagem comercial em 3 passos simples.</p>
          </div>
          <div class="grid md:grid-cols-3 gap-8">
              <!-- Passo 1 -->
              <div class="relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl space-y-4">
                  <div class="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-500/10 ring-1 ring-indigo-500/30 text-indigo-400 text-sm font-bold">1</div>
                  <h3 class="text-lg font-bold">Buscar Negócios Locais</h3>
                  <p class="text-slate-400 text-sm">Insira o nicho e a cidade. Nosso sistema busca diretamente no Google Maps os melhores resultados da região.</p>
              </div>
              <!-- Passo 2 -->
              <div class="relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl space-y-4">
                  <div class="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-500/10 ring-1 ring-indigo-500/30 text-indigo-400 text-sm font-bold">2</div>
                  <h3 class="text-lg font-bold">Auditar Presença Digital</h3>
                  <p class="text-slate-400 text-sm">Analisamos automaticamente se o site possui SSL, se usa e-mails profissionais e calculamos um Score de Urgência.</p>
              </div>
              <!-- Passo 3 -->
              <div class="relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl space-y-4">
                  <div class="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-indigo-500/10 ring-1 ring-indigo-500/30 text-indigo-400 text-sm font-bold">3</div>
                  <h3 class="text-lg font-bold">Gerar Script com IA</h3>
                  <p class="text-slate-400 text-sm">Crie um roteiro de abordagem fria ultra-personalizado utilizando IA baseado nos erros e falhas encontrados na auditoria.</p>
              </div>
          </div>
      </section>

      <!-- Preços -->
      <section class="space-y-12 pb-12">
          <div class="text-center space-y-3">
              <h2 class="text-3xl font-bold tracking-tight">Planos Simples e Claros</h2>
              <p class="text-slate-400 max-w-md mx-auto">Escolha o plano ideal para a sua escala de prospecção.</p>
          </div>
          <div class="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
              <!-- Básico -->
              <div class="relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl flex flex-col justify-between">
                  <div>
                      <h4 class="text-slate-400 font-bold uppercase text-xs tracking-wider">Start</h4>
                      <div class="mt-4 text-3xl font-black text-white">R$ 0</div>
                      <p class="text-xs text-slate-505 mt-1">Créditos de testes gratuitos</p>
                      <ul class="mt-6 space-y-3 text-sm text-slate-300">
                          <li class="flex items-center gap-2">✓ 10 créditos de busca</li>
                          <li class="flex items-center gap-2">✓ Auditoria técnica básica</li>
                          <li class="flex items-center gap-2">✓ Mini-CRM Integrado</li>
                      </ul>
                  </div>
                  <a href="{% url 'accounts:register' %}" class="w-full mt-8 py-3 bg-slate-800 hover:bg-slate-700 font-semibold text-sm rounded-lg text-center transition">Cadastrar Grátis</a>
              </div>

              <!-- Pro -->
              <div class="relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-indigo-500/30 rounded-2xl p-6 shadow-2xl flex flex-col justify-between">
                  <!-- Glow Blob absoluto por trás do Plano Pro -->
                  <div class="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-fuchsia-500 rounded-2xl blur opacity-20 pointer-events-none"></div>
                  
                  <div class="relative z-10">
                      <div class="flex justify-between items-center">
                          <h4 class="text-indigo-400 font-bold uppercase text-xs tracking-wider">Pro</h4>
                          <span class="bg-indigo-500/10 ring-1 ring-indigo-500/30 text-indigo-300 text-[10px] font-extrabold px-2 py-0.5 rounded-full">RECOMENDADO</span>
                      </div>
                      <div class="mt-4 text-3xl font-black text-white">R$ 97<span class="text-sm font-normal text-slate-400">/mês</span></div>
                      <p class="text-xs text-indigo-400/80 mt-1">Acesso ilimitado de buscas</p>
                      <ul class="mt-6 space-y-3 text-sm text-slate-300">
                          <li class="flex items-center gap-2">✓ Buscas ilimitadas diárias</li>
                          <li class="flex items-center gap-2">✓ Gerador de scripts com IA</li>
                          <li class="flex items-center gap-2">✓ Suporte prioritário via chat</li>
                          <li class="flex items-center gap-2">✓ Exportação em formato CSV</li>
                      </ul>
                  </div>
                  <a href="{% url 'accounts:register' %}" class="relative z-10 w-full mt-8 py-3 bg-gradient-to-r from-indigo-500 to-fuchsia-505 text-white font-bold text-sm rounded-lg text-center transition shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/30">Adquirir Plano Pro</a>
              </div>

              <!-- Agência -->
              <div class="relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl flex flex-col justify-between">
                  <div>
                      <h4 class="text-slate-400 font-bold uppercase text-xs tracking-wider">Agência</h4>
                      <div class="mt-4 text-3xl font-black text-white">R$ 297<span class="text-sm font-normal text-slate-400">/mês</span></div>
                      <p class="text-xs text-slate-505 mt-1">Para equipes e múltiplos agentes</p>
                      <ul class="mt-6 space-y-3 text-sm text-slate-300">
                          <li class="flex items-center gap-2">✓ Tudo do plano Pro</li>
                          <li class="flex items-center gap-2">✓ Até 5 sub-contas de membros</li>
                          <li class="flex items-center gap-2">✓ Integração Webhook e Zapier</li>
                          <li class="flex items-center gap-2">✓ APIs de busca dedicadas</li>
                      </ul>
                  </div>
                  <a href="{% url 'accounts:register' %}" class="w-full mt-8 py-3 bg-slate-800 hover:bg-slate-700 font-semibold text-sm rounded-lg text-center transition">Falar com Consultor</a>
              </div>
          </div>
      </section>
  </div>
  {% endblock %}
  ```

- [ ] **Step 3: Testar carregamento da rota principal**
  
  Run: `.venv/bin/python manage.py test leads.tests` (e testar via navegador se possível)
  Expected: PASS

---

### Task 4: Refatoração do Search Studio e Resultados

**Files:**
- Modify: `templates/leads/search_studio.html`
- Modify: `templates/leads/search_results.html`

**Interfaces:**
- Consumes: Dados de consulta de leads e saldo de créditos do usuário.
- Produces: Interface de busca premium e exibição em lista adaptável mobile de cards horizontais (substituindo `<table>`).

- [ ] **Step 1: Refatorar o Search Studio (`search_studio.html`)**
  
  Modificar o arquivo `templates/leads/search_studio.html` para adotar o Card Glassmorphism, Input escuro padrão e o Badge de Créditos no formato de badge minimalista e animado.
  
  ```html
  {% extends "base.html" %}
  {% block title %}Search Studio - LeadScout AI{% endblock %}
  {% block body_class %}min-h-screen bg-slate-950 text-slate-100{% endblock %}
  {% block wrapper_class %}w-full max-w-lg relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6 md:p-8 shadow-2xl text-white{% endblock %}
  
  {% block content %}
  <!-- Glow Blob sutil de fundo do formulário -->
  <div class="absolute -inset-1 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-2xl blur-lg pointer-events-none"></div>

  <div class="relative space-y-6 z-10">
      <div class="text-center space-y-2">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-500/10 ring-1 ring-indigo-500/30 text-indigo-400 mb-2">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
          </div>
          <h2 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              Search Studio
          </h2>
          <p class="text-sm text-slate-400">
              Encontre leads qualificados locais e audite a presença digital deles.
          </p>
      </div>

      <!-- Credit Badge -->
      <div class="flex justify-between items-center bg-black/40 ring-1 ring-white/5 px-4 py-3 rounded-xl">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">Créditos Disponíveis</span>
          <span class="inline-flex items-center gap-2 bg-slate-800/50 ring-1 ring-white/10 px-3 py-1.5 rounded-full text-xs font-mono text-slate-300">
              <span class="inline-block w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              {{ credits_balance }}
          </span>
      </div>

      {% if error %}
      <div class="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start gap-3">
          <svg class="w-5 h-5 text-rose-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span class="text-sm text-rose-300 font-medium">{{ error }}</span>
      </div>
      {% endif %}

      {% if paywall %}
      <div class="p-6 bg-rose-500/10 ring-1 ring-rose-500/20 rounded-xl text-center space-y-4">
          <h3 class="text-lg font-bold text-rose-400">Créditos Esgotados!</h3>
          <p class="text-sm text-slate-400">
              Seus créditos grátis acabaram. Faça o upgrade agora para continuar buscando.
          </p>
          <a href="{% url 'accounts:payments_settings' %}" class="w-full mt-4 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-slate-950 font-bold rounded-xl transition duration-200 transform hover:scale-[1.01] shadow-lg shadow-emerald-500/20 text-center block">
              Fazer Upgrade de Plano
          </a>
      </div>
      {% else %}
      <form method="POST" class="space-y-5">
          {% csrf_token %}
          <div class="space-y-1.5">
              <label class="block text-sm font-medium text-slate-300">Nicho / Categoria de Negócio</label>
              <input type="text" name="nicho" placeholder="Ex: Restaurantes, Dentistas, Imobiliárias" required class="w-full bg-black/50 ring-1 ring-white/5 border-0 rounded-lg px-4 py-3 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:bg-slate-900/50 transition-all">
          </div>
          <div class="space-y-1.5">
              <label class="block text-sm font-medium text-slate-300">Cidade / Localização</label>
              <input type="text" name="localizacao" placeholder="Ex: Natal - RN" required class="w-full bg-black/50 ring-1 ring-white/5 border-0 rounded-lg px-4 py-3 text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:bg-slate-900/50 transition-all">
          </div>
          
          <button type="submit" class="relative group overflow-hidden rounded-lg p-[1px] w-full block mt-6">
              <span class="absolute inset-0 bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-indigo-500 opacity-70 group-hover:opacity-100 transition-opacity duration-300"></span>
              <div class="relative bg-slate-950 px-4 py-3.5 rounded-[7px] flex items-center justify-center transition-all group-hover:bg-opacity-0">
                  <span class="font-semibold text-white">Realizar Busca (Consome 1 Crédito)</span>
              </div>
          </button>
      </form>
      {% endif %}

      <div class="pt-4 border-t border-slate-800 flex justify-between items-center text-xs text-slate-505">
          <a href="{% url 'accounts:dashboard' %}" class="hover:text-indigo-400 transition flex items-center gap-1">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Voltar ao Painel
          </a>
      </div>
  </div>
  {% endblock %}
  ```

- [ ] **Step 2: Refatorar os Resultados da Busca (`search_results.html`)**
  
  Modificar o arquivo `templates/leads/search_results.html` para substituir a tabela estática por uma lista de Cards Horizontais adaptáveis. Em telas pequenas (mobile), cada lead deve ser renderizado como um bloco completo empilhado com o Score flutuando no canto superior direito.
  
  Substituir a tabela `<table>` (linhas 110-251) pela seguinte estrutura:
  
  ```html
  <!-- Leads List (Horizontal Cards / Responsive list) -->
  <div class="space-y-4">
      {% for lead in leads %}
      <div class="relative bg-slate-900/80 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-5 md:p-6 shadow-2xl flex flex-col md:flex-row md:items-center md:justify-between gap-5 hover:ring-indigo-500/30 transition duration-200">
          <!-- Nome e Contato -->
          <div class="space-y-2 flex-grow">
              <div class="flex items-center gap-3">
                  <h3 class="font-bold text-lg text-white leading-tight">{{ lead.name }}</h3>
                  {% if lead.is_hot %}
                  <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 bg-gradient-to-r from-red-500/20 to-orange-500/20 text-orange-400 text-[10px] font-extrabold rounded-full border border-orange-500/30">
                      🔥 Hot
                  </span>
                  {% endif %}
              </div>
              <div class="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-slate-400">
                  {% if lead.phone %}
                  <span class="flex items-center gap-1.5">
                      <svg class="w-4 h-4 text-slate-505" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 01.725.94V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                      {{ lead.phone }}
                  </span>
                  {% endif %}
                  {% if lead.email %}
                  <span class="flex items-center gap-1.5 text-slate-300 font-medium">
                      <svg class="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      {{ lead.email }}
                  </span>
                  {% endif %}
              </div>
          </div>

          <!-- Metadados da Auditoria (Website, SSL, Email Profissional) -->
          <div class="flex flex-wrap items-center gap-4 text-xs">
              <!-- Website -->
              <div>
                  {% if lead.website %}
                  <a href="{{ lead.website }}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 text-sm text-indigo-400 hover:text-indigo-300 hover:underline">
                      Website
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                  </a>
                  {% else %}
                  <span class="text-slate-505 italic">Sem site</span>
                  {% endif %}
              </div>

              <!-- SSL Badge -->
              {% if lead.website %}
              <div>
                  {% if lead.audit.has_ssl %}
                  <span class="inline-flex items-center gap-1 text-emerald-400 font-semibold bg-emerald-500/10 ring-1 ring-emerald-500/20 px-2 py-1 rounded-md">
                      SSL Seguro
                  </span>
                  {% else %}
                  <span class="inline-flex items-center gap-1 text-rose-400 font-semibold bg-rose-500/10 ring-1 ring-rose-500/20 px-2 py-1 rounded-md">
                      SSL Inseguro
                  </span>
                  {% endif %}
              </div>
              {% endif %}

              <!-- E-mail Profissional Badge -->
              {% if lead.website %}
              <div>
                  {% if lead.audit.has_professional_email %}
                  <span class="inline-flex items-center gap-1 text-indigo-400 font-semibold bg-indigo-500/10 ring-1 ring-indigo-500/20 px-2 py-1 rounded-md">
                      E-mail Profissional
                  </span>
                  {% endif %}
              </div>
              {% endif %}
          </div>

          <!-- Score e Ação CRM -->
          <div class="flex items-center justify-between md:justify-end gap-5 pt-4 md:pt-0 border-t md:border-0 border-slate-800">
              <!-- Score Badge flutuante/alinhado -->
              <div class="flex flex-col items-start md:items-center">
                  <span class="text-[9px] uppercase tracking-wider text-slate-505 font-bold mb-1">Score</span>
                  <span class="text-base font-extrabold px-3 py-1 rounded-lg 
                      {% if lead.audit.score >= 70 %}
                          bg-rose-500/10 text-rose-400 ring-1 ring-rose-500/20
                      {% elif lead.audit.score >= 30 %}
                          bg-amber-500/10 text-amber-400 ring-1 ring-amber-500/20
                      {% else %}
                          bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20
                      {% endif %}">
                      {{ lead.audit.score }}
                  </span>
              </div>

              <!-- Ação CRM -->
              <div>
                  {% if lead.pipeline_card %}
                  <a href="{% url 'leads:crm_kanban' %}" class="inline-flex items-center gap-1 px-4 py-2.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-semibold rounded-xl border border-emerald-500/20 transition duration-150">
                      Ver no CRM
                  </a>
                  {% else %}
                  <a href="{% url 'leads:add_to_pipeline' lead.id %}" class="inline-flex items-center gap-1 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold rounded-xl shadow-sm transition duration-150">
                      Adicionar ao CRM
                  </a>
                  {% endif %}
              </div>
          </div>
      </div>
      {% endfor %}
  </div>
  ```

- [ ] **Step 3: Executar testes de integração das buscas**
  
  Run: `.venv/bin/python manage.py test leads.tests.test_views`
  Expected: PASS

---

### Task 5: Refatoração do Mini-CRM Kanban (Mobile-First)

**Files:**
- Modify: `templates/leads/crm_kanban.html`
- Modify: `templates/leads/crm_card_snippet.html`
- Modify: `templates/leads/lead_detail_modal.html`

**Interfaces:**
- Consumes: Acesso aos dados do pipeline de leads e requisição AJAX de alteração de estágio do lead.
- Produces: Interface Kanban Kanban otimizada para mobile com alternância por abas horizontais e formulário seletor para alteração de estágio manual em dispositivos móveis.

- [ ] **Step 1: Adicionar o sistema de Abas Mobile no Kanban (`crm_kanban.html`)**
  
  No arquivo `templates/leads/crm_kanban.html`, acima do grid de colunas (linha 35), adicionar a barra de abas mobile usando Alpine.js (ou Vanilla JS) para controlar a visualização da coluna selecionada.
  
  ```html
  <!-- Mobile Tab Navigation -->
  <div class="flex space-x-2 overflow-x-auto scrollbar-none pb-4 md:hidden" id="mobile-tabs-container">
      <button onclick="switchTab('NOVO')" id="tab-NOVO" class="flex-shrink-0 px-4 py-2 bg-indigo-600 text-white text-xs font-bold rounded-lg transition-all shadow-md">
          Novo ({{ stages.NOVO|length }})
      </button>
      <button onclick="switchTab('CONTATO')" id="tab-CONTATO" class="flex-shrink-0 px-4 py-2 bg-slate-900 text-slate-400 text-xs font-bold rounded-lg transition-all">
          Contato ({{ stages.CONTATO|length }})
      </button>
      <button onclick="switchTab('NEGOCIACAO')" id="tab-NEGOCIACAO" class="flex-shrink-0 px-4 py-2 bg-slate-900 text-slate-400 text-xs font-bold rounded-lg transition-all">
          Negociação ({{ stages.NEGOCIACAO|length }})
      </button>
      <button onclick="switchTab('FECHADO')" id="tab-FECHADO" class="flex-shrink-0 px-4 py-2 bg-slate-900 text-slate-400 text-xs font-bold rounded-lg transition-all">
          Fechado ({{ stages.FECHADO|length }})
      </button>
      <button onclick="switchTab('PERDIDO')" id="tab-PERDIDO" class="flex-shrink-0 px-4 py-2 bg-slate-900 text-slate-400 text-xs font-bold rounded-lg transition-all">
          Perdido ({{ stages.PERDIDO|length }})
      </button>
  </div>
  ```

- [ ] **Step 2: Ajustar a exibição das Colunas no Mobile e Desktop**
  
  Atualizar as classes das colunas do Kanban (ex: `grid grid-cols-1 md:grid-cols-5 gap-5`) e configurar cada coluna (ex: `id="col-NOVO"`) para ter a classe `hidden md:flex` por padrão em mobile, adicionando estilos de background translúcidos.
  
  ```html
  <!-- Kanban Board Grid -->
  <div class="grid grid-cols-1 md:grid-cols-5 gap-5 overflow-x-auto pb-4">
      <!-- NOVO Column -->
      <div class="bg-slate-900/30 p-4 rounded-xl ring-1 ring-white/5 min-h-[500px] flex flex-col space-y-4 transition duration-250 kanban-column flex"
           id="col-NOVO" ondragover="allowDrop(event)" ondragleave="dragLeave(event)" ondrop="drop(event, 'NOVO')">
      ...
  ```
  *(Aplica-se a mesma classe `bg-slate-900/30 ring-1 ring-white/5` a todas as colunas. Em mobile, usaremos JS para exibir apenas a coluna selecionada adicionando a classe `flex` e removendo `hidden`.)*

- [ ] **Step 3: Adicionar Script de Alternância de Abas em `crm_kanban.html`**
  
  No rodapé do script de `crm_kanban.html`, adicionar a função `switchTab` e a função auxiliar `updateStageDirectly` (para lidar com a mudança manual no mobile via `<select>`).
  
  ```javascript
  let activeTab = 'NOVO';
  
  function switchTab(stageCode) {
      activeTab = stageCode;
      const stages = ['NOVO', 'CONTATO', 'NEGOCIACAO', 'FECHADO', 'PERDIDO'];
      
      stages.forEach(code => {
          const col = document.getElementById("col-" + code);
          const tabBtn = document.getElementById("tab-" + code);
          
          if (code === stageCode) {
              col.classList.remove('hidden');
              col.classList.add('flex');
              
              tabBtn.classList.remove('bg-slate-900', 'text-slate-400');
              tabBtn.classList.add('bg-indigo-600', 'text-white', 'shadow-md');
          } else {
              col.classList.remove('flex');
              col.classList.add('hidden');
              
              tabBtn.classList.remove('bg-indigo-600', 'text-white', 'shadow-md');
              tabBtn.classList.add('bg-slate-900', 'text-slate-400');
          }
      });
  }
  
  // Executar inicialização do mobile tab
  document.addEventListener("DOMContentLoaded", () => {
      if (window.innerWidth < 768) {
          switchTab('NOVO');
      }
  });

  async function updateStageDirectly(cardId, stageCode) {
      const cardEl = document.getElementById("card-" + cardId);
      if (!cardEl) return;
      
      const formData = new FormData();
      formData.append("card_id", cardId);
      formData.append("stage", stageCode);
      formData.append("csrfmiddlewaretoken", "{{ csrf_token }}");
      
      try {
          const response = await fetch("{% url 'leads:update_stage' %}", {
              method: "POST",
              body: formData,
              headers: {
                  'X-Requested-With': 'XMLHttpRequest'
              }
          });
          if (response.ok) {
              window.location.reload(); // Recarrega para reposicionar
          } else {
              throw new Error("Erro");
          }
      } catch (err) {
          console.error("Erro ao mover lead:", err);
          window.location.reload();
      }
  }
  ```

- [ ] **Step 4: Refatorar Snippet de Card de Lead (`crm_card_snippet.html`)**
  
  Atualizar o card de lead para incluir o design de bordas sutis e fundo escuro, e injetar o campo `<select>` nativo visível apenas no mobile (`md:hidden`) no rodapé do card.
  
  ```html
  <div class="relative bg-slate-950 p-4 rounded-xl ring-1 ring-white/10 hover:ring-indigo-500/50 transition-all shadow-lg cursor-pointer flex flex-col justify-between h-full"
       draggable="true" 
       ondragstart="drag(event, '{{ card.id }}')" 
       ondragend="dragEnd(event)"
       onclick="if(!event.target.closest('a') && !event.target.closest('select')) openLeadDetail('{{ card.lead.id }}')"
       id="card-{{ card.id }}"
       data-stage="{{ card.stage }}">
      
      <div class="space-y-3">
          <!-- Title & Score -->
          <div class="flex items-start justify-between gap-2">
              <h4 class="font-bold text-sm text-slate-100 hover:text-indigo-400 transition break-words line-clamp-2">
                  {{ card.lead.name }}
              </h4>
              <span class="inline-block text-xs font-extrabold px-1.5 py-0.5 rounded
                  {% if card.lead.audit.score >= 70 %}
                      bg-rose-500/10 text-rose-400 border border-rose-500/20
                  {% elif card.lead.audit.score >= 30 %}
                      bg-amber-500/10 text-amber-400 border border-amber-500/20
                  {% else %}
                      bg-emerald-500/10 text-emerald-400 border border-emerald-500/20
                  {% endif %}" title="Score da Auditoria">
                  {{ card.lead.audit.score|default:0 }}
              </span>
          </div>

          <!-- Contact Info -->
          <div class="space-y-1.5 text-[11px] text-slate-400">
              {% if card.lead.phone %}
              <div class="flex items-center gap-1.5">
                  <svg class="w-3.5 h-3.5 text-slate-505" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.94.725l.548 2.2a1 1 0 01-.321.988l-1.305.98a10.582 10.582 0 004.872 4.872l.98-1.305a1 1 0 01.988-.321l2.2.548a1 1 0 01.725.94V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <span class="truncate">{{ card.lead.phone }}</span>
              </div>
              {% endif %}

              {% if card.lead.email %}
              <div class="flex items-center gap-1.5 text-slate-300">
                  <svg class="w-3.5 h-3.5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <span class="truncate" title="{{ card.lead.email }}">{{ card.lead.email }}</span>
              </div>
              {% endif %}
          </div>
      </div>

      <div class="mt-4 pt-3 border-t border-white/5 space-y-3">
          {% if card.lead.is_hot %}
          <span class="inline-flex items-center gap-1 px-2.5 py-0.5 bg-gradient-to-r from-red-500/20 to-orange-500/20 text-orange-400 text-[10px] font-extrabold rounded-full border border-orange-500/30">
              🔥 Oportunidade Quente
          </span>
          {% endif %}

          <!-- Mobile Move Select -->
          <div class="md:hidden">
              <label class="block text-[9px] font-bold text-slate-505 uppercase tracking-wider mb-1">Mover Estágio</label>
              <select onchange="updateStageDirectly('{{ card.id }}', this.value)" class="w-full bg-slate-900 text-xs text-slate-300 rounded border border-white/10 px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                  <option value="NOVO" {% if card.stage == 'NOVO' %}selected{% endif %}>Novo</option>
                  <option value="CONTATO" {% if card.stage == 'CONTATO' %}selected{% endif %}>Contato</option>
                  <option value="NEGOCIACAO" {% if card.stage == 'NEGOCIACAO' %}selected{% endif %}>Negociação</option>
                  <option value="FECHADO" {% if card.stage == 'FECHADO' %}selected{% endif %}>Fechado</option>
                  <option value="PERDIDO" {% if card.stage == 'PERDIDO' %}selected{% endif %}>Perdido</option>
              </select>
          </div>
      </div>
  </div>
  ```

- [ ] **Step 5: Refatorar o Modal de Detalhes do Lead (`lead_detail_modal.html`)**
  
  Modificar a janela do modal em `templates/leads/lead_detail_modal.html` para usar o fundo escuro `bg-slate-900 border-white/10` e aplicar o botão com Glow para o botão de geração de script de vendas via IA (`btn-generate-script`).
  
  Substituir o botão da linha 202:
  ```html
  <button id="btn-generate-script" onclick="generateAIScript('{{ lead.id }}')" class="relative group overflow-hidden rounded-lg p-[1px] shadow-md shadow-indigo-600/10">
      <span class="absolute inset-0 bg-gradient-to-r from-indigo-500 via-fuchsia-500 to-indigo-500 opacity-80 group-hover:opacity-100 transition-opacity duration-300"></span>
      <div class="relative bg-slate-950 px-3.5 py-1.5 rounded-[7px] flex items-center justify-center gap-1.5 transition-all group-hover:bg-opacity-0">
          <svg class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 9.172V5L8 4z" />
          </svg>
          <span class="font-bold text-[11px] text-white">Gerar Roteiro</span>
      </div>
  </button>
  ```

- [ ] **Step 6: Executar testes de sanidade gerais do Kanban**
  
  Run: `.venv/bin/python manage.py test`
  Expected: PASS

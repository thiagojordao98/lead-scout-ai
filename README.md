# 🔍 Lead Scout AI

**Plataforma de Prospecção Ativa B2B & CRM para Venda de Presença Digital**

O **Lead Scout AI** é uma solução SaaS desenvolvida em Django para ajudar agências, assessores de marketing e desenvolvedores freelancers a encontrarem e fecharem novos clientes locais. Ele busca empresas diretamente pelo Google Maps, audita a presença digital de cada uma delas (ausência de site, segurança SSL/HTTPS inativa ou falta de e-mail profissional) e classifica os leads mais quentes para prospecção. O sistema conta com um CRM Kanban completo, geração automática de scripts de vendas personalizados por Inteligência Artificial (OpenAI) e painel SaaS completo com métricas financeiras.

🚀 **Live Demo**: [https://leads-scout.tjmcpro.com](https://leads-scout.tjmcpro.com)

---

## 📸 Demonstração Visual

### 1. Tela Inicial / Login
![Tela Inicial / Login](qa/screeshots/leads_scout_lp.png)

### 2. Painel de Busca (Search Studio)
* **Painel de Busca & Varredura de Leads:**
![Painel de Busca](qa/screeshots/leads_scout_search_ready.png)
* **Execução da Busca em Segundo Plano:**
![Executando Busca](qa/screeshots/leads_scout_search_run.png)

### 3. Funil de Vendas (Kanban CRM)
![Funil de Vendas CRM](qa/screeshots/leads_scout_pipeline_crm.png)

---

## ⚡ Principais Funcionalidades

### 1. Painel de Busca (Search Studio)
* Pesquisa assíncrona integrada à **API Serper (Google Maps scraper)**.
* Se a chave da API não estiver configurada, o sistema entra em modo simulador (mock) automaticamente, facilitando o desenvolvimento e demonstração local.
* Processamento em segundo plano flexível: utiliza **Celery** se configurado, com fallback automático para threads secundárias (daemon) para simplificar a execução sem dependências extras.

### 2. Auditoria Técnica e Score de Urgência
* **Verificação de SSL/HTTPS**: Tenta conectar via HTTPS de forma segura. Se houver falha de segurança (erro de certificado ou conexão), define que o SSL está ausente.
* **Varredura de E-mails**: Faz scraping no site da empresa em busca de e-mails corporativos vs. genéricos (ex: gmail.com, hotmail.com).
* **Score (0-100)**: Atribui pontos à urgência de prospecção do lead:
  * +50 pontos: Sem site institucional.
  * +30 pontos: Site sem certificado SSL/HTTPS.
  * +20 pontos: Sem e-mail profissional/corporativo.
* **Leads Quentes (Hot Leads)**: Leads com pontuação máxima de 100/100 são marcados automaticamente como oportunidades quentes.

### 3. Funil de Vendas (Kanban CRM)
* Organização visual interativa do pipeline de vendas.
* Estágios padrão: `Novo`, `Contato`, `Negociação`, `Fechado` e `Perdido`.
* Arraste de cards (drag-and-drop) integrado com salvamento assíncrono via API interna.
* Modal com detalhes da auditoria técnica do lead e histórico de contato.

### 4. Geração de Abordagem com IA (OpenAI)
* Integração com **OpenAI GPT-4o-mini** para gerar scripts de vendas (cold mail ou WhatsApp) customizados para cada dor técnica específica do lead prospectado.
* Fallback inteligente offline para geração de abordagens caso não haja chave da API cadastrada.

### 5. Arquitetura SaaS e Gestão de Planos
* Autenticação segura via e-mail e vinculação de múltiplos usuários a uma mesma Organização.
* Controle de limite de créditos por organização para busca de novos leads.
* Middleware customizado de planos que bloqueia acessos a certas partes da aplicação caso a assinatura esteja inativa.

### 6. Dashboard Financeiro (MRR / Churn)
* Painel analítico premium com métricas de negócio reais:
  * **MRR (Monthly Recurring Revenue)**: Receita mensal recorrente estimada de assinaturas ativas.
  * **Churn Rate**: Taxa de cancelamento de assinaturas.
  * **Conversão**: Percentual de usuários cadastrados com plano ativo.
  * **Contas Ativas / Inativas**.

### 7. Gateway de Pagamento e Webhooks (Zouti)
* Endpoint preparado para receber webhooks do gateway **Zouti**.
* Criação ou atualização automática do `UserPlan` para status `ACTIVE` (ao confirmar pagamento) ou `CANCELLED` (em caso de estorno/cancelamento).
* Envio automático de e-mail de boas-vindas transacional integrado com **SendPulse**.

---

## 🛠️ Tecnologias Utilizadas

* **Backend**: Django 6.0 (Python 3.12+)
* **Interface**: HTML5 (Tailwind CSS, Vanilla JS, Chart.js)
* **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
* **APIs & Serviços Externos**:
  * Serper API (busca no Google Maps)
  * OpenAI API (copys/scripts inteligentes)
  * SendPulse API (e-mails transacionais)
  * Zouti (gateway de pagamentos)

---

## 💻 Instalação e Execução Local

### Requisitos Prévios
* Python 3.12+ (Recomendado 3.14)
* Pip

### Passo a Passo

#### 1. Clonar e Acessar o Repositório
```bash
git clone <url-do-repositorio>
cd lead-scout-ai
```

#### 2. Criar e Ativar Ambiente Virtual
No Linux/macOS:
```bash
python -m venv .venv
source .venv/bin/activate
```
No Windows (Command Prompt):
```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### 3. Instalar Dependências
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto (ao lado de `manage.py`) a partir do exemplo abaixo:

```env
# Django Settings
DJANGO_SECRET_KEY=sua-chave-secreta-forte-aqui
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# Banco de Dados (Padrão SQLite)
# Caso queira rodar com postgres local, configure o DATABASE_URL
# DATABASE_URL=postgres://usuario:senha@localhost:5432/nome_banco

# Configurações de E-mail (console durante desenvolvimento)
DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=contato@tjmcpro.com

# APIs (Opcionais para rodar localmente - ativa mocks se vazio)
SERPER_API_KEY=
OPENAI_API_KEY=

# SendPulse (E-mails transacionais)
CLIENT_ID_SENDPULSE=
CLIENT_SECRET_SENDPULSE=

# Gateway Zouti (Segurança do Webhook)
ZOUTI_WEBHOOK_SECRET=
```

#### 5. Executar as Migrações do Banco de Dados
```bash
python manage.py migrate
```

#### 6. Criar Superusuário (Acesso Administrativo)
```bash
python manage.py createsuperuser
```

#### 7. Iniciar o Servidor de Desenvolvimento
```bash
python manage.py runserver
```

Após iniciar, você pode acessar:
* **Interface Principal**: [http://127.0.0.1:8000/auth/login/](http://127.0.0.1:8000/auth/login/)
* **Dashboard Financeira SaaS**: [http://127.0.0.1:8000/auth/admin/dashboard/](http://127.0.0.1:8000/auth/admin/dashboard/)
* **Painel Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🧪 Testes Automatizados
O projeto conta com uma suíte de testes robusta cobrindo buscas, auditoria, CRM, autenticação e webhooks. Para executá-los:

```bash
python manage.py test
```

---

## 📂 Estrutura de Diretórios Principal

* [accounts/](file:///home/thiago/www/micro-saas/lead-scout-ai/accounts): Lógica de usuários, organizações, perfis, e-mails de recuperação e views de login/dashboard.
* [leads/](file:///home/thiago/www/micro-saas/lead-scout-ai/leads): Módulo principal da aplicação de prospecção. Contém a busca (Search Studio), auditoria de SSL/e-mails, CRM Kanban e geração de abordagens por IA.
* [plans/](file:///home/thiago/www/micro-saas/lead-scout-ai/plans): Definição de planos de assinatura, middleware de restrições de planos e o webhook de integração com a Zouti.
* [templates/](file:///home/thiago/www/micro-saas/lead-scout-ai/templates): Páginas HTML da aplicação estilizadas com Tailwind CSS.
* [core/](file:///home/thiago/www/micro-saas/lead-scout-ai/core): Configurações globais do Django (URLs centrais, settings, etc).

---

## ⚠️ Cuidados em Produção
Caso pretenda colocar o projeto em produção, atente-se aos seguintes itens essenciais de segurança:
1. **SECRET_KEY**: Nunca a exponha ou mantenha a chave padrão do settings. Sempre leia via `.env` (`DJANGO_SECRET_KEY`) e gere uma nova chave forte com o comando:
   ```bash
   openssl rand -base64 32
   ```
2. **E-mails**: Altere as credenciais `DEFAULT_FROM_EMAIL` e `DJANGO_EMAIL_BACKEND` para garantir o fluxo de entregas por e-mail oficial da sua empresa.
3. **Hosts Permitidos**: Defina `DJANGO_ALLOWED_HOSTS` com o domínio real de produção do seu site (Ex: `leads-scout.tjmcpro.com`) e nunca deixe o debug ativado em produção (`DJANGO_DEBUG=False`).

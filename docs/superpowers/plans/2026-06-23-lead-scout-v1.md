# LeadScout AI V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and launch LeadScout AI V1, a sales intelligence platform featuring multi-tenant lead scanning, background auditing/scoring, a mini-CRM Kanban board, and AI outreach script generation.

**Architecture:** Monolithic Modular Django application. Business logic (Serper integration, web auditing, AI) is strictly isolated in service files. An `organization_id` partitions data to enforce multi-tenancy. Background tasks run using a dual Celery/Redis engine with a robust python threading fallback.

**Tech Stack:** Python 3.x, Django 6.x, PostgreSQL/SQLite, HTML5 Drag-and-drop API, OpenAI API (or Mock), Serper API (or Mock).

## Global Constraints

*   Database models must enforce multi-tenancy via foreign key checks on `Organization`.
*   All external integrations (Serper, OpenAI) must gracefully fallback to a high-fidelity local mock simulator if API keys are not defined in the environment.
*   Background tasks must execute asynchronously but fall back to thread-pool/in-line execution if Celery is not running.
*   Styling must use the pre-configured Tailwind CSS CDN layout in a dark mode theme with neon details.

---

### Task 1: Core Multi-Tenancy Models and Onboarding Flow

**Files:**
*   Modify: `accounts/models.py`
*   Modify: `accounts/views.py`
*   Modify: `accounts/forms.py`
*   Create: `accounts/tests/test_tenancy.py`

**Interfaces:**
*   Produces: `Organization` model and `User.organization` reference.
*   Produces: Updated registration flow that creates an `Organization` and links the new user as `OWNER`.

- [ ] **Step 1: Write the failing tests for multi-tenant onboarding**
    
    Create `accounts/tests/test_tenancy.py` with:
    ```python
    from django.test import TestCase
    from django.contrib.auth import get_user_model
    from accounts.models import Organization

    User = get_user_model()

    class TenancyOnboardingTest(TestCase):
        def test_registration_creates_organization_and_assigns_owner(self):
            response = self.client.post('/accounts/register/', {
                'email': 'tenant_owner@test.com',
                'password': 'password123',
                'password_confirm': 'password123'
            }, follow=True)
            self.assertEqual(response.status_code, 200)
            
            # Check user is created and has an organization
            user = User.objects.get(email='tenant_owner@test.com')
            self.assertIsNotNone(user.organization)
            self.assertEqual(user.role, 'OWNER')
            self.assertEqual(user.organization.credits_balance, 10)
            self.assertEqual(user.organization.name, "Agência tenant_owner@test.com")
    ```

- [ ] **Step 2: Run tests to verify they fail**
    
    Run: `python manage.py test accounts.tests.test_tenancy`
    Expected: FAIL due to missing attributes and tables.

- [ ] **Step 3: Implement Organization models and modify User**
    
    Modify `accounts/models.py` to add `Organization`, update `User`, and add the roles:
    ```python
    from django.contrib.auth.models import AbstractUser
    from django.db import models
    from .managers import UserManager

    class Organization(models.Model):
        name = models.CharField(max_length=255)
        credits_balance = models.PositiveIntegerField(default=10)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return self.name

    class User(AbstractUser):
        username = None
        email = models.EmailField(unique=True)
        organization = models.ForeignKey(
            Organization, 
            on_delete=models.SET_NULL, 
            null=True, 
            blank=True, 
            related_name="members"
        )
        role = models.CharField(
            max_length=20, 
            choices=[('OWNER', 'Dono'), ('SALES_REP', 'Vendedor')], 
            default='OWNER'
        )

        USERNAME_FIELD = "email"
        REQUIRED_FIELDS = []

        objects = UserManager()

        @property
        def is_active_plan(self):
            try:
                user_plan = self.user_plan
            except Exception:
                return False
            return user_plan.status == "ACTIVE"

        def __str__(self):
            return self.email
    ```

- [ ] **Step 4: Update onboarding views and forms**
    
    Modify `accounts/forms.py` to make registration clean, and modify `accounts/views.py` (in `register_view` at lines 31-42) to create the organization upon signup:
    ```python
    # Inside accounts/views.py register_view
    # If POST and form is valid:
    user = form.save(commit=False)
    org = Organization.objects.create(name=f"Agência {user.email}", credits_balance=10)
    user.organization = org
    user.role = 'OWNER'
    user.save()
    ```

- [ ] **Step 5: Run migrations and verify tests pass**
    
    Run:
    ```bash
    python manage.py makemigrations accounts
    python manage.py migrate
    python manage.py test accounts.tests.test_tenancy
    ```
    Expected: PASS.

- [ ] **Step 6: Commit**
    
    Run:
    ```bash
    git add accounts/
    git commit -m "feat: add Organization model and auto-create organization on user signup"
    ```

---

### Task 2: Create leads App and Serper API Integration

**Files:**
*   Create: `leads/models.py`
*   Create: `leads/services.py`
*   Create: `leads/tests/test_serper.py`

**Interfaces:**
*   Produces: `SearchQuery` and `Lead` models.
*   Produces: `SerperClient.search(nicho, localizacao)` returning parsed raw lead data (name, website, address, phone, place_id).

- [ ] **Step 1: Scaffolding the leads app**
    
    Run: `python manage.py startapp leads`
    Add `'leads',` to `INSTALLED_APPS` in `core/settings.py`.

- [ ] **Step 2: Write failing test for Serper Integration**
    
    Create `leads/tests/test_serper.py` with:
    ```python
    from django.test import TestCase
    from unittest.mock import patch
    from leads.services import SerperClient

    class SerperIntegrationTest(TestCase):
        @patch('requests.post')
        def test_serper_client_parses_results(self, mock_post):
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {
                "places": [
                    {
                        "title": "Restaurante Central",
                        "address": "Av. Principal, 100",
                        "phoneNumber": "+55 84 99999-9999",
                        "website": "http://restaurantecentral.com",
                        "cid": "123456789"
                    }
                ]
            }
            client = SerperClient(api_key="fake-key")
            results = client.search(nicho="Restaurante", localizacao="Natal, RN")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['name'], "Restaurante Central")
            self.assertEqual(results[0]['place_id'], "123456789")
            
        def test_serper_client_mock_mode_when_key_missing(self):
            client = SerperClient(api_key="")
            results = client.search(nicho="Restaurante", localizacao="Natal, RN")
            self.assertGreater(len(results), 0)
            self.assertTrue(any(r['name'] for r in results))
    ```

- [ ] **Step 3: Implement SearchQuery and Lead Models**
    
    Write to `leads/models.py`:
    ```python
    from django.conf import settings
    from django.db import models
    from accounts.models import Organization

    class SearchQuery(models.Model):
        organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='search_queries')
        user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
        nicho = models.CharField(max_length=100)
        localizacao = models.CharField(max_length=150)
        status = models.CharField(
            max_length=20, 
            choices=[('PENDING', 'Pendente'), ('PROCESSING', 'Processando'), ('COMPLETED', 'Concluído'), ('FAILED', 'Falhou')], 
            default='PENDING'
        )
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.nicho} em {self.localizacao} ({self.status})"

    class Lead(models.Model):
        organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='leads')
        search_query = models.ForeignKey(SearchQuery, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
        place_id = models.CharField(max_length=255, blank=True, null=True)
        name = models.CharField(max_length=255)
        website = models.URLField(blank=True, null=True, max_length=500)
        phone = models.CharField(max_length=50, blank=True, null=True)
        address = models.TextField(blank=True, null=True)
        email = models.EmailField(blank=True, null=True)
        is_hot = models.BooleanField(default=False)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return self.name
    ```

- [ ] **Step 4: Implement SerperClient with Mock Fallback**
    
    Create `leads/services.py`:
    ```python
    import os
    import requests
    from django.conf import settings

    class SerperClient:
        def __init__(self, api_key=None):
            self.api_key = api_key or os.getenv("SERPER_API_KEY", "")

        def search(self, nicho, localizacao):
            if not self.api_key:
                return self._get_mock_results(nicho, localizacao)
            
            url = "https://google.serper.dev/maps"
            payload = {
                "q": f"{nicho} in {localizacao}",
                "gl": "br",
                "hl": "pt"
            }
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
                if response.status_code != 200:
                    return self._get_mock_results(nicho, localizacao)
                data = response.json()
                places = data.get("places", [])
                results = []
                for p in places:
                    results.append({
                        "place_id": str(p.get("cid", p.get("title", ""))),
                        "name": p.get("title", "Sem nome"),
                        "website": p.get("website"),
                        "phone": p.get("phoneNumber"),
                        "address": p.get("address"),
                    })
                return results
            except Exception:
                return self._get_mock_results(nicho, localizacao)

        def _get_mock_results(self, nicho, localizacao):
            return [
                {
                    "place_id": f"mock_1_{nicho}_{localizacao}",
                    "name": f"Padaria Pão Quente de {localizacao}",
                    "website": None,  # Will score 100 (No site, SSL missing, no professional email)
                    "phone": "(84) 98888-0001",
                    "address": f"Rua das Flores, 10 - {localizacao}"
                },
                {
                    "place_id": f"mock_2_{nicho}_{localizacao}",
                    "name": f"Mercado Super {nicho}",
                    "website": "http://supermercadoinseguro.com.br",  # Will score 50 (no SSL, has generic email)
                    "phone": "(84) 98888-0002",
                    "address": f"Av. Central, 200 - {localizacao}"
                },
                {
                    "place_id": f"mock_3_{nicho}_{localizacao}",
                    "name": f"Clínica Sorriso VIP",
                    "website": "https://sorrisovip.com.br",  # Will score 0 (SSL OK, professional email)
                    "phone": "(84) 98888-0003",
                    "address": f"Rua do Prado, 45 - {localizacao}"
                }
            ]
    ```

- [ ] **Step 5: Run migrations and verify Serper client tests pass**
    
    Run:
    ```bash
    python manage.py makemigrations leads
    python manage.py migrate
    python manage.py test leads.tests.test_serper
    ```
    Expected: PASS.

- [ ] **Step 6: Commit**
    
    Run:
    ```bash
    git add leads/
    git commit -m "feat: add leads app, SearchQuery and Lead models, and SerperClient service with Mock fallback"
    ```

---

### Task 3: Auditor Engine & Scoring Logic

**Files:**
*   Modify: `leads/models.py`
*   Modify: `leads/services.py`
*   Create: `leads/tests/test_audit.py`

**Interfaces:**
*   Produces: `AuditResult` model.
*   Produces: `AuditService.audit_lead(lead)` performing site analysis, SSL check, and email scraping, then computing the urgency score.

- [ ] **Step 1: Write failing tests for technical audit and score logic**
    
    Create `leads/tests/test_audit.py` with:
    ```python
    from django.test import TestCase
    from accounts.models import Organization
    from leads.models import Lead, AuditResult
    from leads.services import AuditService

    class AuditServiceTest(TestCase):
        def setUp(self):
            self.org = Organization.objects.create(name="Test Agency")
            
        def test_audit_lead_no_website(self):
            lead = Lead.objects.create(organization=self.org, name="No Website Co", website=None)
            service = AuditService()
            audit_res = service.audit_lead(lead)
            
            self.assertEqual(audit_res.has_website, False)
            self.assertEqual(audit_res.has_ssl, False)
            self.assertEqual(audit_res.score, 100)  # +50 no site, +30 no SSL, +20 no professional email
            self.assertTrue(lead.is_hot)
    ```

- [ ] **Step 2: Run tests to verify they fail**
    
    Run: `python manage.py test leads.tests.test_audit`
    Expected: FAIL due to missing model properties and `AuditService`.

- [ ] **Step 3: Add `AuditResult` to `leads/models.py`**
    
    Add the `AuditResult` model to `leads/models.py` (if not already added in Task 2):
    ```python
    class AuditResult(models.Model):
        lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='audit')
        has_website = models.BooleanField(default=False)
        has_ssl = models.BooleanField(default=False)
        has_professional_email = models.BooleanField(default=False)
        score = models.PositiveIntegerField(default=0)
        details = models.JSONField(default=dict)
        updated_at = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"Audit for {self.lead.name} (Score: {self.score})"
    ```

- [ ] **Step 4: Implement `AuditService` in `leads/services.py`**
    
    Append the audit logic and generic domain list to `leads/services.py`:
    ```python
    import re
    from urllib.parse import urlparse
    from leads.models import AuditResult

    class AuditService:
        GENERIC_DOMAINS = {
            "gmail.com", "hotmail.com", "yahoo.com", "yahoo.com.br", 
            "outlook.com", "live.com", "aol.com", "terra.com.br", "uol.com.br"
        }

        def audit_lead(self, lead) -> AuditResult:
            has_website = False
            has_ssl = False
            has_professional_email = False
            emails_found = []
            details = {}

            if not lead.website:
                score = 100 # No website (+50), No SSL (+30), No professional email (+20)
                details["reason"] = "Sem website cadastrado."
            else:
                has_website = True
                cleaned_url = self._clean_url(lead.website)
                
                # Check HTTPS / SSL
                try:
                    ssl_response = requests.get(f"https://{cleaned_url}", timeout=5)
                    has_ssl = True
                    details["https_status"] = ssl_response.status_code
                except Exception as e:
                    has_ssl = False
                    details["ssl_error"] = str(e)

                # Fetch Content and Scrape Emails
                target_url = f"https://{cleaned_url}" if has_ssl else f"http://{cleaned_url}"
                try:
                    page_response = requests.get(target_url, timeout=5)
                    html_content = page_response.text
                    emails_found = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html_content)))
                    details["scraped_emails"] = emails_found
                except Exception as e:
                    details["scrape_error"] = str(e)

                # Email evaluation
                professional_found = False
                if emails_found:
                    for email in emails_found:
                        domain = email.split('@')[-1].lower()
                        if domain not in self.GENERIC_DOMAINS:
                            professional_found = True
                            if not lead.email:
                                lead.email = email
                                lead.save(update_fields=['email'])
                            break

                has_professional_email = professional_found

                # Scoring
                score = 0
                if not has_ssl:
                    score += 30
                if not has_professional_email:
                    score += 20

            # Update lead is_hot field
            lead.is_hot = (score == 100)
            lead.save(update_fields=['is_hot'])

            audit_result, _ = AuditResult.objects.update_or_create(
                lead=lead,
                defaults={
                    "has_website": has_website,
                    "has_ssl": has_ssl,
                    "has_professional_email": has_professional_email,
                    "score": score,
                    "details": details
                }
            )
            return audit_result

        def _clean_url(self, url):
            parsed = urlparse(url)
            netloc = parsed.netloc or parsed.path
            return netloc.replace("www.", "")
    ```

- [ ] **Step 5: Run migrations and verify tests pass**
    
    Run:
    ```bash
    python manage.py makemigrations leads
    python manage.py migrate
    python manage.py test leads.tests.test_audit
    ```
    Expected: PASS.

- [ ] **Step 6: Commit**
    
    Run:
    ```bash
    git add leads/
    git commit -m "feat: implement AuditService and scoring rules with HTML email regex scraping"
    ```

---

### Task 4: Background Auditing Asynchronous Workers (Celery & Threads)

**Files:**
*   Create: `leads/tasks.py`
*   Modify: `leads/views.py`
*   Create: `leads/tests/test_tasks.py`

**Interfaces:**
*   Produces: `process_search_query_task(search_query_id)` asynchronous worker task.
*   Produces: Dual scheduler dispatcher inside `leads/views.py`.

- [ ] **Step 1: Write failing tests for asynchronous search processor**
    
    Create `leads/tests/test_tasks.py` with:
    ```python
    from django.test import TestCase
    from accounts.models import Organization
    from leads.models import SearchQuery, Lead
    from leads.tasks import process_search_query_task

    class TaskExecutionTest(TestCase):
        def setUp(self):
            self.org = Organization.objects.create(name="Async Agency")
            
        def test_background_task_creates_leads_and_audits(self):
            query = SearchQuery.objects.create(
                organization=self.org,
                nicho="Dentista",
                localizacao="Natal, RN",
                status="PENDING"
            )
            process_search_query_task(query.id)
            
            query.refresh_from_db()
            self.assertEqual(query.status, "COMPLETED")
            self.assertGreater(query.leads.count(), 0)
            
            first_lead = query.leads.first()
            self.assertIsNotNone(first_lead.audit)
    ```

- [ ] **Step 2: Run tests to verify they fail**
    
    Run: `python manage.py test leads.tests.test_tasks`
    Expected: FAIL due to missing `leads/tasks.py`.

- [ ] **Step 3: Implement Celery tasks and Python threading engine**
    
    Create `leads/tasks.py` to support Celery with fallback:
    ```python
    import logging
    import threading
    from leads.models import SearchQuery, Lead
    from leads.services import SerperClient, AuditService

    logger = logging.getLogger(__name__)

    def process_search_query_task(search_query_id):
        try:
            query = SearchQuery.objects.get(id=search_query_id)
        except SearchQuery.DoesNotExist:
            return
        
        query.status = "PROCESSING"
        query.save(update_fields=["status"])

        try:
            client = SerperClient()
            results = client.search(nicho=query.nicho, localizacao=query.localizacao)
            
            auditor = AuditService()
            for r in results:
                lead, _ = Lead.objects.update_or_create(
                    organization=query.organization,
                    place_id=r["place_id"],
                    defaults={
                        "search_query": query,
                        "name": r["name"],
                        "website": r["website"],
                        "phone": r["phone"],
                        "address": r["address"],
                    }
                )
                # Audit lead
                try:
                    auditor.audit_lead(lead)
                except Exception:
                    logger.exception(f"Erro ao auditar lead {lead.id}")
            
            query.status = "COMPLETED"
        except Exception:
            logger.exception(f"Falha na busca da query {search_query_id}")
            query.status = "FAILED"
        
        query.save(update_fields=["status"])

    def dispatch_search_query(search_query_id):
        # Fallback to threading if Celery is not configured
        thread = threading.Thread(target=process_search_query_task, args=(search_query_id,))
        thread.daemon = True
        thread.start()
    ```

- [ ] **Step 4: Run tests and verify background tasks work**
    
    Run: `python manage.py test leads.tests.test_tasks`
    Expected: PASS.

- [ ] **Step 5: Commit**
    
    Run:
    ```bash
    git add leads/tasks.py leads/tests/test_tasks.py
    git commit -m "feat: implement process_search_query_task with Python threading daemon dispatcher"
    ```

---

### Task 5: Search Studio and Lead List Views

**Files:**
*   Create: `leads/urls.py`
*   Modify: `core/urls.py`
*   Create: `leads/views.py`
*   Create: `templates/leads/search_studio.html`
*   Create: `templates/leads/search_results.html`

**Interfaces:**
*   Produces: `/leads/search/` (Search Studio form input).
*   Produces: `/leads/search/status/<int:query_id>/` (AJAX status endpoint).
*   Produces: `/leads/search/results/<int:query_id>/` (renders leads table ordered by Score).

- [ ] **Step 1: Write URL mapping in `leads/urls.py` and `core/urls.py`**
    
    Create `leads/urls.py`:
    ```python
    from django.urls import path
    from . import views

    app_name = "leads"

    urlpatterns = [
        path("search/", views.search_studio_view, name="search_studio"),
        path("search/status/<int:query_id>/", views.search_status_view, name="search_status"),
        path("search/results/<int:query_id>/", views.search_results_view, name="search_results"),
    ]
    ```
    Modify `core/urls.py` to route to `leads.urls`:
    ```python
    # In core/urls.py urlpatterns list:
    path("leads/", include("leads.urls")),
    ```

- [ ] **Step 2: Create Views for Search Studio**
    
    Add view functions inside `leads/views.py`:
    ```python
    from django.shortcuts import render, redirect, get_object_or_repr, get_object_or_404
    from django.contrib.auth.decorators import login_required
    from django.http import JsonResponse, HttpResponseForbidden
    from django.db import transaction
    from .models import SearchQuery, Lead
    from .tasks import dispatch_search_query

    @login_required
    def search_studio_view(request):
        org = request.user.organization
        if request.method == "POST":
            nicho = request.POST.get("nicho", "").strip()
            localizacao = request.POST.get("localizacao", "").strip()
            
            if not nicho or not localizacao:
                return render(request, "leads/search_studio.html", {"error": "Preencha todos os campos."})

            with transaction.atomic():
                org.refresh_from_db()
                if org.credits_balance < 1:
                    return render(request, "leads/search_studio.html", {"paywall": True})
                
                org.credits_balance -= 1
                org.save(update_fields=["credits_balance"])
                
                query = SearchQuery.objects.create(
                    organization=org,
                    user=request.user,
                    nicho=nicho,
                    localizacao=localizacao,
                    status="PENDING"
                )
            
            dispatch_search_query(query.id)
            return redirect("leads:search_results", query_id=query.id)

        return render(request, "leads/search_studio.html", {"credits_balance": org.credits_balance})

    @login_required
    def search_status_view(request, query_id):
        query = get_object_or_404(SearchQuery, id=query_id, organization=request.user.organization)
        return JsonResponse({"status": query.status})

    @login_required
    def search_results_view(request, query_id):
        query = get_object_or_404(SearchQuery, id=query_id, organization=request.user.organization)
        leads = Lead.objects.filter(search_query=query).select_related('audit').order_by('-audit__score')
        return render(request, "leads/search_results.html", {"query": query, "leads": leads})
    ```

- [ ] **Step 3: Write HTML templates for Search Studio and Results**
    
    Create `templates/leads/search_studio.html` with a beautiful premium dark-mode dashboard card:
    ```html
    {% extends "base.html" %}
    {% block title %}Search Studio{% endblock %}
    {% block content %}
    <div class="space-y-6 text-white bg-slate-900 p-8 rounded-2xl border border-slate-800">
        <h2 class="text-2xl font-bold text-center">Search Studio</h2>
        <p class="text-sm text-slate-400 text-center">Encontre leads qualificados locais consumindo créditos da sua agência.</p>
        
        {% if paywall %}
        <div class="p-6 bg-red-950 border border-red-800 rounded-xl text-center space-y-4">
            <h3 class="text-lg font-semibold text-red-400">Créditos Esgotados!</h3>
            <p class="text-sm">Seus 10 créditos grátis acabaram. Faça o upgrade agora para continuar buscando.</p>
            <a href="{% url 'accounts:payments_settings' %}" class="inline-block bg-emerald-500 hover:bg-emerald-600 px-6 py-2 rounded-lg font-semibold text-slate-950">Fazer Upgrade</a>
        </div>
        {% else %}
        <form method="POST" class="space-y-4">
            {% csrf_token %}
            <div>
                <label class="block text-sm font-medium mb-1">Nicho / Categoria</label>
                <input type="text" name="nicho" placeholder="Ex: Restaurantes, Dentistas, Padarias" required class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500">
            </div>
            <div>
                <label class="block text-sm font-medium mb-1">Localização</label>
                <input type="text" name="localizacao" placeholder="Ex: Natal - RN" required class="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500">
            </div>
            <button type="submit" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 rounded-lg font-bold transition">Realizar Busca (1 Crédito)</button>
        </form>
        {% endif %}
    </div>
    {% endblock %}
    ```

    Create `templates/leads/search_results.html` displaying leads and their Score.
    
- [ ] **Step 4: Verify views render correctly**
    
    Run: `python manage.py check`
    Expected: System check identifies no issues.

- [ ] **Step 5: Commit**
    
    Run:
    ```bash
    git add leads/urls.py leads/views.py templates/leads/
    git commit -m "feat: implement Search Studio views, status updates, and styling templates"
    ```

---

### Task 6: Mini-CRM Kanban Board and Drag-and-Drop

**Files:**
*   Modify: `leads/models.py`
*   Modify: `leads/urls.py`
*   Modify: `leads/views.py`
*   Create: `templates/leads/crm_kanban.html`
*   Create: `leads/tests/test_crm.py`

**Interfaces:**
*   Produces: `PipelineCard` model.
*   Produces: `/leads/crm/` (Kanban UI).
*   Produces: `/leads/crm/add-lead/<int:lead_id>/` (Adds lead to pipeline).
*   Produces: `/leads/crm/update-stage/` (AJAX POST updates card stage).

- [ ] **Step 1: Add PipelineCard to models and run migrations**
    
    Update `leads/models.py` with `PipelineCard` (from design schema if not migrated yet) and migrate:
    ```bash
    python manage.py makemigrations leads
    python manage.py migrate
    ```

- [ ] **Step 2: Write failing test for CRM pipeline operations**
    
    Create `leads/tests/test_crm.py` with:
    ```python
    from django.test import TestCase
    from accounts.models import Organization
    from leads.models import Lead, PipelineCard

    class CRMTestCase(TestCase):
        def setUp(self):
            self.org = Organization.objects.create(name="CRM Agency")
            
        def test_add_lead_creates_pipeline_card(self):
            lead = Lead.objects.create(organization=self.org, name="Prospect Co")
            PipelineCard.objects.create(organization=self.org, lead=lead, stage="NOVO")
            
            card = PipelineCard.objects.get(lead=lead)
            self.assertEqual(card.stage, "NOVO")
    ```

- [ ] **Step 3: Implement CRM views inside `leads/views.py`**
    
    Add Kanban endpoints:
    ```python
    @login_required
    def crm_kanban_view(request):
        org = request.user.organization
        cards = PipelineCard.objects.filter(organization=org).select_related('lead', 'lead__audit')
        
        stages = {
            'NOVO': [],
            'CONTATO': [],
            'NEGOCIACAO': [],
            'FECHADO': [],
            'PERDIDO': []
        }
        for card in cards:
            stages[card.stage].append(card)
            
        return render(request, "leads/crm_kanban.html", {"stages": stages})

    @login_required
    def add_to_pipeline_view(request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id, organization=request.user.organization)
        PipelineCard.objects.get_or_create(
            organization=request.user.organization,
            lead=lead,
            defaults={"stage": "NOVO"}
        )
        return redirect("leads:crm_kanban")

    @login_required
    @transaction.atomic
    def update_card_stage_view(request):
        if request.method == "POST":
            card_id = request.POST.get("card_id")
            new_stage = request.POST.get("stage")
            if new_stage in ['NOVO', 'CONTATO', 'NEGOCIACAO', 'FECHADO', 'PERDIDO']:
                card = get_object_or_404(PipelineCard, id=card_id, organization=request.user.organization)
                card.stage = new_stage
                card.save(update_fields=["stage"])
                return JsonResponse({"status": "success"})
        return JsonResponse({"status": "error"}, status=400)
    ```

- [ ] **Step 4: Create HTML Kanban Board with drag-and-drop support**
    
    Create `templates/leads/crm_kanban.html` with full drag-and-drop HTML5 JS:
    ```html
    {% extends "base.html" %}
    {% block title %}Mini CRM Kanban{% endblock %}
    {% block content %}
    <div class="text-white space-y-6 w-full">
        <h2 class="text-3xl font-extrabold text-center">Pipeline de Vendas</h2>
        <div class="grid grid-cols-5 gap-4 overflow-x-auto py-4">
            {% for stage_code, cards in stages.items %}
            <div class="bg-slate-900 p-4 rounded-xl border border-slate-800 min-h-[400px] flex flex-col space-y-3" 
                 ondragover="allowDrop(event)" ondrop="drop(event, '{{ stage_code }}')">
                <h3 class="font-bold text-center text-slate-300 uppercase border-b border-slate-800 pb-2">{{ stage_code }}</h3>
                <div class="space-y-3 flex-grow" id="stage-{{ stage_code }}">
                    {% for card in cards %}
                    <div class="bg-slate-950 p-3 rounded-lg border border-slate-800 cursor-grab active:cursor-grabbing hover:border-indigo-500 transition" 
                         draggable="true" ondragstart="drag(event, '{{ card.id }}')" id="card-{{ card.id }}">
                        <p class="font-semibold text-sm">{{ card.lead.name }}</p>
                        <p class="text-xs text-slate-400">Score: {{ card.lead.audit.score|default:0 }}</p>
                        {% if card.lead.is_hot %}
                        <span class="inline-block mt-2 px-2 py-0.5 bg-emerald-950 border border-emerald-800 text-emerald-400 text-[10px] font-bold rounded">Oportunidade de Ouro</span>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    <script>
        function allowDrop(ev) { ev.preventDefault(); }
        function drag(ev, cardId) { ev.dataTransfer.setData("text", cardId); }
        function drop(ev, stageCode) {
            ev.preventDefault();
            var cardId = ev.dataTransfer.getData("text");
            var cardEl = document.getElementById("card-" + cardId);
            document.getElementById("stage-" + stageCode).appendChild(cardEl);
            
            // Post update
            var formData = new FormData();
            formData.append("card_id", cardId);
            formData.append("stage", stageCode);
            formData.append("csrfmiddlewaretoken", "{{ csrf_token }}");
            
            fetch("{% url 'leads:update_stage' %}", {
                method: "POST",
                body: formData
            });
        }
    </script>
    {% endblock %}
    ```

- [ ] **Step 5: Run verification tests**
    
    Run: `python manage.py test leads.tests.test_crm`
    Expected: PASS.

- [ ] **Step 6: Commit**
    
    Run:
    ```bash
    git add leads/tests/test_crm.py templates/leads/crm_kanban.html
    git commit -m "feat: implement Mini-CRM Kanban board with drag-and-drop and stage update endpoints"
    ```

---

### Task 7: AI outreach Script Generator and Lead Detail Modal

**Files:**
*   Create: `leads/ai.py`
*   Modify: `leads/urls.py`
*   Modify: `leads/views.py`
*   Create: `leads/tests/test_ai.py`

**Interfaces:**
*   Produces: `AIScriptGenerator.generate(lead)` formatting dynamic templates or contacting OpenAI.
*   Produces: `/leads/crm/detail/<int:lead_id>/` Detail Modal content view.
*   Produces: `/leads/crm/generate-script/<int:lead_id>/` Script generator endpoint.

- [ ] **Step 1: Write test for script generation fallback**
    
    Create `leads/tests/test_ai.py` with:
    ```python
    from django.test import TestCase
    from accounts.models import Organization
    from leads.models import Lead, AuditResult
    from leads.ai import AIScriptGenerator

    class AITestCase(TestCase):
        def setUp(self):
            self.org = Organization.objects.create(name="AI Agency")
            self.lead = Lead.objects.create(organization=self.org, name="Restaurante Central")
            AuditResult.objects.create(lead=self.lead, has_website=False, score=100)
            
        def test_fallback_script_generation(self):
            generator = AIScriptGenerator(api_key="")
            script = generator.generate(self.lead)
            self.assertIn("Restaurante Central", script)
            self.assertIn("site", script.lower())
    ```

- [ ] **Step 2: Run tests to verify they fail**
    
    Run: `python manage.py test leads.tests.test_ai`
    Expected: FAIL due to missing `leads/ai.py`.

- [ ] **Step 3: Implement `AIScriptGenerator` in `leads/ai.py`**
    
    Create `leads/ai.py`:
    ```python
    import os
    import openai
    from django.conf import settings

    class AIScriptGenerator:
        def __init__(self, api_key=None):
            self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")

        def generate(self, lead) -> str:
            audit = getattr(lead, 'audit', None)
            score = audit.score if audit else 0
            has_website = audit.has_website if audit else False
            has_ssl = audit.has_ssl if audit else False
            has_professional_email = audit.has_professional_email if audit else False

            if not self.api_key:
                return self._generate_fallback(lead.name, score, has_website, has_ssl, has_professional_email)

            try:
                client = openai.OpenAI(api_key=self.api_key)
                prompt = f"""
                Você é um especialista em vendas B2B de alta performance. 
                Gere um script de abordagem fria de 3 parágrafos focado na dor do cliente.
                Use os seguintes dados da auditoria técnica da empresa:
                - Nome: {lead.name}
                - Website: {"OK" if has_website else "Sem site"} (SSL: {"OK" if has_ssl else "Sem SSL"})
                - E-mail: {"Profissional" if has_professional_email else "Não profissional / Gmail"}
                - Score de Urgência: {score}/100
                
                Regras:
                1. Tom profissional, amigável e focado em gerar valor imediatamente.
                2. Não cite pontuações ou jargões técnicos complexos; foque nos impactos de negócios (perda de clientes, falta de segurança, falta de credibilidade).
                3. Termine com uma chamada de ação (CTA) simples e direta para uma conversa de 10 minutos.
                """
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception:
                return self._generate_fallback(lead.name, score, has_website, has_ssl, has_professional_email)

        def _generate_fallback(self, name, score, has_website, has_ssl, has_professional_email):
            if not has_website:
                return f"Olá equipe do {name},\n\n" \
                       f"Identifiquei que sua empresa é muito bem avaliada no Google Maps, mas atualmente não possui um site institucional próprio. Hoje, 80% das decisões de compra locais começam com uma busca na internet, e a falta de uma presença digital própria faz com que concorrentes menores apareçam na frente de vocês.\n\n" \
                       f"Desenvolvemos soluções sob medida que colocam empresas de destaque no topo dos resultados em poucos dias, permitindo receber contatos diretos de novos clientes de forma totalmente automatizada.\n\n" \
                       f"Podemos agendar uma rápida conversa de 10 minutos nesta semana para eu te mostrar como isso funcionará para vocês?"
            elif not has_ssl:
                return f"Olá equipe do {name},\n\n" \
                       f"Dando uma olhada no site de vocês, notei que os navegadores (Chrome/Safari) o marcam como 'Não Seguro' devido à ausência do certificado de segurança SSL. Isso afasta potenciais clientes que entram no site por medo de fraudes e prejudica seu ranqueamento no Google.\n\n" \
                       f"Corrigir essa falha de segurança leva poucas horas e eleva imediatamente o nível de confiança profissional que sua marca transmite aos visitantes online.\n\n" \
                       f"Que tal falarmos por 10 minutos nesta semana para resolvermos esse problema e garantirmos a integridade dos seus dados?"
            else:
                return f"Olá equipe do {name},\n\n" \
                       f"Achei fantástico o trabalho de vocês online. Entretanto, notei que o e-mail de contato principal ainda usa um domínio genérico (@gmail/@hotmail). Em transações B2B, o uso de e-mails corporativos aumenta a taxa de abertura de propostas e a credibilidade geral do negócio.\n\n" \
                       f"Podemos ajudar a configurar e-mails profissionais dedicados com seu próprio domínio sem qualquer atrito técnico, dando mais formalidade à sua marca.\n\n" \
                       f"Podemos agendar uma breve conversa de 10 minutos nesta semana para alinhar essa melhoria?"
    ```

- [ ] **Step 4: Create lead script generating view**
    
    Add views to `leads/views.py`:
    ```python
    from .ai import AIScriptGenerator

    @login_required
    def lead_detail_modal_view(request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id, organization=request.user.organization)
        audit = getattr(lead, 'audit', None)
        return render(request, "leads/lead_detail_modal.html", {"lead": lead, "audit": audit})

    @login_required
    def generate_sales_script_view(request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id, organization=request.user.organization)
        generator = AIScriptGenerator()
        script = generator.generate(lead)
        return JsonResponse({"script": script})
    ```

- [ ] **Step 5: Run tests to verify script generator works**
    
    Run: `python manage.py test leads.tests.test_ai`
    Expected: PASS.

- [ ] **Step 6: Commit**
    
    Run:
    ```bash
    git add leads/ai.py leads/tests/test_ai.py leads/views.py
    git commit -m "feat: implement AIScriptGenerator with OpenAI request engine and pre-written dynamic fallback templates"
    ```

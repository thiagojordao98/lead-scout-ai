# Limite de Requisições por IP e Pop-up de Venda/Feedback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Limitar buscas gratuitas por IP a 3/dia e exibir um pop-up de marketing persuasivo com bônus de créditos em troca de feedback para converter vendas/obter feedback.

**Architecture:** 
- Criar modelos `IPRequestLog` e `Feedback` no app `leads` e adicionar campo `received_feedback_bonus` no app `accounts.Organization`.
- Adicionar validações de IP nas views do Django.
- Criar o componente modal no template do Search Studio utilizando Tailwind e JS (AJAX) para submissão do feedback.

**Tech Stack:** Django, SQLite, Tailwind CSS, JavaScript (Fetch API).

## Global Constraints

- Utilizar classes Tailwind nativas suportadas pelo CDN.
- Respeitar a persistência de banco de dados por migrações Django.
- Testar a lógica com cobertura adequada.

---

### Task 1: Modificar os Modelos e Criar Migrações

**Files:**
- Modify: `accounts/models.py`
- Modify: `leads/models.py`
- Test: `./.venv/bin/python manage.py makemigrations && ./.venv/bin/python manage.py migrate`

**Interfaces:**
- Consumes: Nenhuma
- Produces: Tabelas atualizadas com `IPRequestLog`, `Feedback` e coluna `received_feedback_bonus` em `Organization`.

- [ ] **Step 1: Adicionar campo à classe `Organization` em `accounts/models.py`**
Adicionar `received_feedback_bonus` na linha 12:
```python
    received_feedback_bonus = models.BooleanField(default=False)
```

- [ ] **Step 2: Adicionar novos modelos a `leads/models.py`**
Adicionar imports no topo e os novos modelos no final do arquivo:
```python
from django.utils import timezone

class IPRequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    date = models.DateField(default=timezone.localdate)
    count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('ip_address', 'date')

    def __str__(self):
        return f"{self.ip_address} on {self.date}: {self.count}"

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.user.email} at {self.created_at}"
```

- [ ] **Step 3: Gerar e executar as migrações**
Run: `./.venv/bin/python manage.py makemigrations`
Expected: Migrations created for accounts and leads.
Run: `./.venv/bin/python manage.py migrate`
Expected: Migrations applied successfully.

- [ ] **Step 4: Commit**
```bash
git add accounts/models.py leads/models.py accounts/migrations/ leads/migrations/
git commit -m "feat(db): add IPRequestLog, Feedback models and Organization feedback bonus status"
```

---

### Task 2: Modificar as Views e URLs

**Files:**
- Modify: `leads/views.py`
- Modify: `leads/urls.py`

**Interfaces:**
- Consumes: Modelos `IPRequestLog`, `Feedback`, `Organization`.
- Produces: Endpoints `search_studio` protegidos e rota `/leads/feedback/` funcional.

- [ ] **Step 1: Adicionar `get_client_ip` e lógicas de IP na view em `leads/views.py`**
Importar `timezone`, `IPRequestLog` e `Feedback`. Criar a função `get_client_ip` e atualizar `search_studio_view` para lidar com limites de IP.

Código a adicionar:
```python
from django.utils import timezone
from .models import IPRequestLog, Feedback

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

Lógica de `search_studio_view` modificada:
```python
@login_required
def search_studio_view(request):
    org = request.user.organization
    ip_address = get_client_ip(request)
    today = timezone.localdate()
    
    # Rastrear limite do IP apenas se o usuário não tem plano ativo
    has_active_plan = request.user.is_active_plan
    ip_log = None
    show_limit_modal = False
    
    if not has_active_plan:
        ip_log, _ = IPRequestLog.objects.get_or_create(ip_address=ip_address, date=today)
        if ip_log.count >= 3:
            show_limit_modal = True

    if request.method == "POST":
        if show_limit_modal:
            return render(request, "leads/search_studio.html", {
                "error": "Você atingiu o limite de 3 buscas diárias grátis por IP hoje.",
                "credits_balance": org.credits_balance,
                "show_limit_modal": True
            })
            
        nicho = request.POST.get("nicho", "").strip()
        localizacao = request.POST.get("localizacao", "").strip()
        
        if not nicho or not localizacao:
            return render(request, "leads/search_studio.html", {
                "error": "Preencha todos os campos.",
                "credits_balance": org.credits_balance,
                "show_limit_modal": show_limit_modal
            })

        with transaction.atomic():
            from accounts.models import Organization
            locked_org = Organization.objects.select_for_update().get(id=org.id)
            if locked_org.credits_balance < 1:
                return render(request, "leads/search_studio.html", {
                    "paywall": True,
                    "credits_balance": locked_org.credits_balance,
                    "show_limit_modal": show_limit_modal
                })
            
            locked_org.credits_balance -= 1
            locked_org.save(update_fields=["credits_balance"])
            org.credits_balance = locked_org.credits_balance
            
            query = SearchQuery.objects.create(
                organization=locked_org,
                user=request.user,
                nicho=nicho,
                localizacao=localizacao,
                status="PENDING"
            )
            
        # Incrementar contagem apenas após sucesso
        if ip_log is not None:
            ip_log.count += 1
            ip_log.save(update_fields=["count"])
            # Atualizar status do modal após incremento
            if ip_log.count >= 3:
                show_limit_modal = True
        
        dispatch_search_query(query.id)
        return redirect("leads:search_results", query_id=query.id)

    return render(request, "leads/search_studio.html", {
        "credits_balance": org.credits_balance,
        "show_limit_modal": show_limit_modal
    })
```

- [ ] **Step 2: Adicionar a view `submit_feedback_view` em `leads/views.py`**
Criar a view que salva o feedback e concede 5 créditos adicionais:
```python
@login_required
@require_POST
def submit_feedback_view(request):
    message = request.POST.get("message", "").strip()
    if not message:
        return JsonResponse({"status": "error", "message": "O feedback não pode estar vazio."}, status=400)
    
    # Salvar feedback
    Feedback.objects.create(user=request.user, message=message)
    
    # Processar bônus de créditos
    org = request.user.organization
    granted_bonus = False
    
    with transaction.atomic():
        from accounts.models import Organization
        locked_org = Organization.objects.select_for_update().get(id=org.id)
        if not locked_org.received_feedback_bonus:
            locked_org.credits_balance += 5
            locked_org.received_feedback_bonus = True
            locked_org.save(update_fields=["credits_balance", "received_feedback_bonus"])
            org.credits_balance = locked_org.credits_balance
            org.received_feedback_bonus = True
            granted_bonus = True
            
    if granted_bonus:
        return JsonResponse({
            "status": "success", 
            "message": "Muito obrigado pelo seu feedback! Concedemos 5 créditos adicionais para você na hora.",
            "credits_balance": org.credits_balance
        })
    else:
        return JsonResponse({
            "status": "success", 
            "message": "Muito obrigado por enviar seu feedback sincero!",
            "credits_balance": org.credits_balance
        })
```

- [ ] **Step 3: Registrar rota em `leads/urls.py`**
Adicionar a rota no array `urlpatterns`:
```python
    path("feedback/", views.submit_feedback_view, name="submit_feedback"),
```

- [ ] **Step 4: Commit**
```bash
git add leads/views.py leads/urls.py
git commit -m "feat(leads): restrict searches by IP and add AJAX feedback view"
```

---

### Task 3: Modificar o Template `search_studio.html`

**Files:**
- Modify: `templates/leads/search_studio.html`

**Interfaces:**
- Consumes: Flag `show_limit_modal` e atributo `organization.received_feedback_bonus`.
- Produces: Modal flutuante na tela de Search Studio com copy de persuasão e AJAX form.

- [ ] **Step 1: Modificar `templates/leads/search_studio.html` para renderizar o modal e desabilitar formulário**
Renderizar o modal de limitação no final do bloco `content` e desabilitar o botão de busca caso `show_limit_modal` seja True.

Adicionar no topo do template ou no script o tratamento de submissão AJAX de feedback:
Código do Modal (adicionar antes de `{% endblock %}`):
```html
{% if show_limit_modal %}
<div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/60 dark:bg-black/80 backdrop-blur-md px-4" id="limit-modal-overlay">
    <div class="bg-white dark:bg-slate-900 ring-1 ring-slate-200 dark:ring-white/10 rounded-2xl p-6 md:p-8 max-w-md w-full shadow-2xl space-y-6 text-slate-800 dark:text-slate-100 transition-all duration-300">
        <!-- Header Alerta -->
        <div class="text-center space-y-2">
            <div class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-amber-500/10 text-amber-500 dark:text-amber-400 ring-1 ring-amber-500/20 mb-1">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            </div>
            <h3 class="text-xl font-bold tracking-tight text-slate-900 dark:text-white">Limite Diário Atingido!</h3>
            <p class="text-xs text-slate-550 dark:text-slate-400">
                Você atingiu o limite máximo de <strong>3 buscas gratuitas por IP hoje</strong>.
            </p>
        </div>

        <!-- Marketing Persuasion -->
        <div class="p-4 bg-emerald-500/5 dark:bg-emerald-500/10 border border-emerald-500/25 dark:border-emerald-500/20 rounded-xl space-y-2">
            <h4 class="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wide">Como o LeadScout AI te ajuda a fechar vendas?</h4>
            <p class="text-xs text-slate-650 dark:text-slate-300 leading-relaxed">
                Empresas que utilizam nossas auditorias automáticas aumentam a conversão de reuniões em até <strong>3x</strong>. Qualificar a presença digital (site, SSL, e-mail) do seu cliente local antes de ligar cria autoridade instantânea e gera valor no primeiro contato.
            </p>
        </div>

        <!-- CTA Plan Upgrade -->
        <div class="space-y-2.5">
            <a href="{% url 'accounts:payments_settings' %}" class="w-full py-3 px-4 bg-gradient-to-r from-emerald-600 to-green-500 hover:from-emerald-700 hover:to-green-600 text-white text-sm font-bold rounded-xl transition duration-200 text-center block shadow-lg shadow-emerald-500/20">
                Fazer Upgrade para Plano Standard (Buscas Ilimitadas)
            </a>
        </div>

        <!-- Feedback Incentive -->
        {% if not request.user.organization.received_feedback_bonus %}
        <div class="border-t border-slate-200 dark:border-slate-800/80 pt-5 space-y-3" id="feedback-bonus-container">
            <div class="text-xs text-slate-550 dark:text-slate-400 space-y-1">
                <span class="font-bold text-slate-700 dark:text-slate-350 block">Quer testar mais um pouco?</span>
                <p>Deixe um feedback sincero sobre a ferramenta e ganhe <strong>+5 créditos</strong> de buscas na hora!</p>
            </div>
            
            <form id="feedback-bonus-form" class="space-y-2.5">
                {% csrf_token %}
                <textarea name="message" id="feedback-message" required placeholder="Escreva o que achou da ferramenta, críticas ou sugestões..." class="w-full bg-slate-50 dark:bg-black/50 ring-1 ring-slate-200 dark:ring-white/5 border-0 rounded-lg p-2.5 text-xs text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:ring-1 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900/50 outline-none h-16 resize-none"></textarea>
                <button type="submit" id="feedback-submit-btn" class="w-full py-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-750 text-xs font-semibold text-slate-700 dark:text-slate-300 rounded-lg border border-slate-200 dark:border-slate-700 transition duration-150">
                    Enviar Feedback e Resgatar +5 Créditos
                </button>
            </form>
            <div id="feedback-status" class="hidden text-xs font-medium text-emerald-600 dark:text-emerald-400 text-center"></div>
        </div>
        {% endif %}
    </div>
</div>

<script>
    document.addEventListener("DOMContentLoaded", () => {
        const feedbackForm = document.getElementById("feedback-bonus-form");
        if (feedbackForm) {
            feedbackForm.addEventListener("submit", async (e) => {
                e.preventDefault();
                const text = document.getElementById("feedback-message").value.trim();
                if (!text) return;
                
                const submitBtn = document.getElementById("feedback-submit-btn");
                submitBtn.disabled = true;
                submitBtn.textContent = "Processando...";
                
                const formData = new FormData(feedbackForm);
                try {
                    const response = await fetch("{% url 'leads:submit_feedback' %}", {
                        method: "POST",
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    const data = await response.json();
                    
                    const statusDiv = document.getElementById("feedback-status");
                    statusDiv.textContent = data.message;
                    statusDiv.classList.remove("hidden");
                    
                    if (response.ok) {
                        feedbackForm.classList.add("hidden");
                        setTimeout(() => {
                            window.location.reload();
                        }, 2200);
                    } else {
                        submitBtn.disabled = false;
                        submitBtn.textContent = "Tentar Novamente";
                    }
                } catch (err) {
                    console.error(err);
                    submitBtn.disabled = false;
                    submitBtn.textContent = "Tentar Novamente";
                }
            });
        }
    });
</script>
{% endif %}
```

- [ ] **Step 2: Desabilitar o formulário principal caso o modal esteja ativo**
No formulário de busca (`<form method="POST">`), caso `show_limit_modal` seja True, desabilitar os inputs e botões:
```html
<form method="POST" class="space-y-5">
    {% csrf_token %}
    <div class="space-y-1.5">
        <label class="block text-sm font-medium text-slate-650 dark:text-slate-300">Nicho / Categoria de Negócio</label>
        <input type="text" name="nicho" placeholder="Ex: Restaurantes, Dentistas, Imobiliárias" required {% if show_limit_modal %}disabled{% endif %} class="w-full bg-slate-100/50 dark:bg-black/50 ring-1 ring-slate-200 dark:ring-white/5 border-0 rounded-lg px-4 py-3 text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900/50 transition-all outline-none {% if show_limit_modal %}opacity-50 cursor-not-allowed{% endif %}">
    </div>
    <div class="space-y-1.5">
        <label class="block text-sm font-medium text-slate-650 dark:text-slate-300">Cidade / Localização</label>
        <input type="text" name="localizacao" placeholder="Ex: Natal - RN" required {% if show_limit_modal %}disabled{% endif %} class="w-full bg-slate-100/50 dark:bg-black/50 ring-1 ring-slate-200 dark:ring-white/5 border-0 rounded-lg px-4 py-3 text-slate-800 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500 focus:ring-2 focus:ring-emerald-500 focus:bg-white dark:focus:bg-slate-900/50 transition-all outline-none {% if show_limit_modal %}opacity-50 cursor-not-allowed{% endif %}">
    </div>
    
    <button type="submit" {% if show_limit_modal %}disabled{% endif %} class="relative group overflow-hidden rounded-lg p-[1px] w-full block mt-6 {% if show_limit_modal %}opacity-50 cursor-not-allowed{% endif %}">
        <span class="absolute inset-0 bg-gradient-to-r from-emerald-500 via-lime-400 to-emerald-500 opacity-70 group-hover:opacity-100 transition-opacity duration-300"></span>
        <div class="relative bg-slate-50 dark:bg-slate-950 px-4 py-3.5 rounded-[7px] flex items-center justify-center transition-all group-hover:bg-opacity-0">
            <span class="font-semibold text-slate-800 dark:text-white group-hover:text-white">Realizar Busca (Consome 1 Crédito)</span>
        </div>
    </button>
</form>
```

- [ ] **Step 3: Commit**
```bash
git add templates/leads/search_studio.html
git commit -m "feat(theme): build rate-limit marketing modal and feedback mechanism on Search Studio UI"
```

---

### Task 4: Criar Testes Unitários e Integrados

**Files:**
- Create/Modify: `leads/tests/test_views.py`

**Interfaces:**
- Consumes: Nenhuma
- Produces: Testes para a validação do rate limit por IP e do bônus de feedback.

- [ ] **Step 1: Criar testes na classe `leads/tests/test_views.py`**
Adicionar cenários de teste para:
1. Buscar leads e testar se atinge o rate limit no 4º POST se o usuário não tem plano.
2. Garantir que usuário com plano ativo não é barrado no rate limit.
3. Testar se o feedback adiciona 5 créditos apenas na primeira vez.

Código de exemplo a ser incorporado/escrito:
```python
from django.urls import reverse
from leads.models import IPRequestLog, Feedback
from accounts.models import Organization
from plans.models import Plan, UserPlan

# (Implementar os métodos de teste adequados dentro do arquivo)
```

- [ ] **Step 2: Executar testes**
Run: `./.venv/bin/python manage.py test`
Expected: todos os testes passando.

- [ ] **Step 3: Commit**
```bash
git add leads/tests/test_views.py docs/superpowers/plans/2026-06-24-rate-limit-ip.md
git commit -m "test(leads): assert IP rate-limiting and feedback-incentive workflows"
```

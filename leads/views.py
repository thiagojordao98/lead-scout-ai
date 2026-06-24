from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db import transaction
from .models import SearchQuery, Lead, PipelineCard
from .tasks import dispatch_search_query
from .ai import AIScriptGenerator


@login_required
def search_studio_view(request):
    org = request.user.organization
    if request.method == "POST":
        nicho = request.POST.get("nicho", "").strip()
        localizacao = request.POST.get("localizacao", "").strip()
        
        if not nicho or not localizacao:
            return render(request, "leads/search_studio.html", {
                "error": "Preencha todos os campos.",
                "credits_balance": org.credits_balance
            })

        with transaction.atomic():
            from accounts.models import Organization
            locked_org = Organization.objects.select_for_update().get(id=org.id)
            if locked_org.credits_balance < 1:
                return render(request, "leads/search_studio.html", {
                    "paywall": True,
                    "credits_balance": locked_org.credits_balance
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
        
        dispatch_search_query(query.id)
        return redirect("leads:search_results", query_id=query.id)

    return render(request, "leads/search_studio.html", {
        "credits_balance": org.credits_balance
    })

@login_required
def search_status_view(request, query_id):
    query = get_object_or_404(SearchQuery, id=query_id, organization=request.user.organization)
    return JsonResponse({"status": query.status})

@login_required
def search_results_view(request, query_id):
    query = get_object_or_404(SearchQuery, id=query_id, organization=request.user.organization)
    leads = Lead.objects.filter(
        search_query=query,
        pipeline_card__isnull=True
    ).select_related('audit', 'pipeline_card').order_by('-audit__score')
    return render(request, "leads/search_results.html", {"query": query, "leads": leads})


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
        if card.stage in stages:
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
    if lead.search_query:
        return redirect("leads:search_results", query_id=lead.search_query.id)
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


@login_required
def lead_detail_modal_view(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id, organization=request.user.organization)
    audit = getattr(lead, 'audit', None)
    return render(request, "leads/lead_detail_modal.html", {"lead": lead, "audit": audit})


@login_required
@require_POST
def generate_sales_script_view(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id, organization=request.user.organization)
    generator = AIScriptGenerator()
    script = generator.generate(lead)
    return JsonResponse({"script": script})


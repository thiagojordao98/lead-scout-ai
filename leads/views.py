from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
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
            return render(request, "leads/search_studio.html", {
                "error": "Preencha todos os campos.",
                "credits_balance": org.credits_balance
            })

        with transaction.atomic():
            org.refresh_from_db()
            if org.credits_balance < 1:
                return render(request, "leads/search_studio.html", {
                    "paywall": True,
                    "credits_balance": org.credits_balance
                })
            
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
    leads = Lead.objects.filter(search_query=query).select_related('audit').order_by('-audit__score')
    return render(request, "leads/search_results.html", {"query": query, "leads": leads})

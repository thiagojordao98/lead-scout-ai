import logging
import threading
from leads.models import SearchQuery, Lead
from leads.services import SerperClient, AuditService

logger = logging.getLogger(__name__)

# Dynamically import celery if available
try:
    from celery import shared_task
except ImportError:
    def shared_task(func):
        return func

@shared_task
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
    try:
        from celery import current_app
        if current_app.conf.broker_url:
            process_search_query_task.delay(search_query_id)
            logger.info(f"Dispatched search query {search_query_id} via Celery.")
            return
    except Exception as e:
        logger.debug(f"Celery dispatch failed: {e}")

    # Fallback to threading if Celery is not configured
    thread = threading.Thread(target=process_search_query_task, args=(search_query_id,))
    thread.daemon = True
    thread.start()
    logger.info(f"Dispatched search query {search_query_id} via daemon Thread.")

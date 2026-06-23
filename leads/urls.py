from django.urls import path
from . import views

app_name = "leads"

urlpatterns = [
    path("search/", views.search_studio_view, name="search_studio"),
    path("search/status/<int:query_id>/", views.search_status_view, name="search_status"),
    path("search/results/<int:query_id>/", views.search_results_view, name="search_results"),
    path("crm/", views.crm_kanban_view, name="crm_kanban"),
    path("crm/add-lead/<int:lead_id>/", views.add_to_pipeline_view, name="add_to_pipeline"),
    path("crm/update-stage/", views.update_card_stage_view, name="update_stage"),
]

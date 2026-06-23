from django.urls import path
from . import views

app_name = "leads"

urlpatterns = [
    path("search/", views.search_studio_view, name="search_studio"),
    path("search/status/<int:query_id>/", views.search_status_view, name="search_status"),
    path("search/results/<int:query_id>/", views.search_results_view, name="search_results"),
]

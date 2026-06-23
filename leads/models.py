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

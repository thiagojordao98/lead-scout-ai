from django.conf import settings
from django.db import models
from django.utils import timezone
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


class PipelineCard(models.Model):
    STAGE_CHOICES = [
        ('NOVO', 'Novo'),
        ('CONTATO', 'Contato'),
        ('NEGOCIACAO', 'Negociação'),
        ('FECHADO', 'Fechado'),
        ('PERDIDO', 'Perdido'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='pipeline_cards')
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name='pipeline_card')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='NOVO')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.lead.name} - {self.stage}"


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



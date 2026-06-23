import logging
import re
from urllib.parse import urlparse
import requests
from django.conf import settings
from leads.models import AuditResult

logger = logging.getLogger(__name__)

class SerperClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or getattr(settings, "SERPER_API_KEY", "")

    def search(self, nicho, localizacao):
        if not self.api_key:
            logger.info("Chave SERPER_API_KEY não configurada. Ativando modo simulador/mock.")
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
                logger.warning(
                    f"Falha na requisição Serper API. Status: {response.status_code}. "
                    f"Resposta: {response.text[:200]}. Ativando mock fallback."
                )
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
            logger.exception("Erro de conexão ou parse na Serper API. Ativando mock fallback.")
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


class AuditService:
    GENERIC_DOMAINS = {
        "gmail.com", "hotmail.com", "yahoo.com", "yahoo.com.br", 
        "outlook.com", "live.com", "aol.com", "terra.com.br", "uol.com.br",
        "icloud.com", "bol.com.br", "ig.com.br"
    }

    def audit_lead(self, lead) -> AuditResult:
        has_website = False
        has_ssl = False
        has_professional_email = False
        emails_found = []
        details = {}
        email_to_update = None

        if not lead.website:
            score = 100  # No website (+50), No SSL (+30), No professional email (+20)
            details["reason"] = "Sem website cadastrado."
        else:
            has_website = True
            cleaned_url = self._clean_url(lead.website)
            html_content = ""
            
            # Check HTTPS / SSL
            try:
                ssl_response = requests.get(f"https://{cleaned_url}", timeout=5)
                has_ssl = True
                details["https_status"] = ssl_response.status_code
                html_content = ssl_response.text
            except Exception as e:
                has_ssl = False
                details["ssl_error"] = str(e)

            # Fetch Content and Scrape Emails if SSL failed
            if not has_ssl:
                try:
                    page_response = requests.get(f"http://{cleaned_url}", timeout=5)
                    html_content = page_response.text
                    details["http_status"] = page_response.status_code
                except Exception as e:
                    details["http_error"] = str(e)

            if html_content:
                emails_found = list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html_content)))
                details["scraped_emails"] = emails_found

            # Email evaluation
            professional_found = False
            if emails_found:
                for email in emails_found:
                    domain = email.split('@')[-1].lower()
                    if domain not in self.GENERIC_DOMAINS:
                        professional_found = True
                        if not lead.email:
                            email_to_update = email
                        break

            has_professional_email = professional_found

            # Scoring
            score = 0
            if not has_ssl:
                score += 30
            if not has_professional_email:
                score += 20

        # Update lead fields in a single save call
        fields_to_update = ['is_hot']
        lead.is_hot = (score == 100)
        if email_to_update:
            lead.email = email_to_update
            fields_to_update.append('email')
        lead.save(update_fields=fields_to_update)

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
        netloc = parsed.netloc or parsed.path.split('/')[0]
        return netloc.replace("www.", "")


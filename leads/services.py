import logging
import requests
from django.conf import settings

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

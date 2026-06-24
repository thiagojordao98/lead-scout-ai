import os
import openai
from django.conf import settings

class AIScriptGenerator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")

    def generate(self, lead) -> str:
        audit = getattr(lead, 'audit', None)
        score = audit.score if audit else 0
        has_website = bool(lead.website)
        has_ssl = audit.has_ssl if audit else False
        has_professional_email = audit.has_professional_email if audit else False

        if not self.api_key:
            return self._generate_fallback(lead.name, score, has_website, has_ssl, has_professional_email)

        try:
            client = openai.OpenAI(api_key=self.api_key)
            prompt = f"""
            Você é um especialista em vendas B2B de alta performance. 
            Gere um script de abordagem fria de 3 parágrafos focado na dor do cliente.
            Use os seguintes dados da auditoria técnica da empresa:
            - Nome: {lead.name}
            - Website: {"OK" if has_website else "Sem site"} (SSL: {"OK" if has_ssl else "Sem SSL"})
            - E-mail: {"Profissional" if has_professional_email else "Não profissional / Gmail"}
            - Score de Urgência: {score}/100
            
            Regras:
            1. Tom profissional, amigável e focado em gerar valor imediatamente.
            2. Não cite pontuações ou jargões técnicos complexos; foque nos impactos de negócios (perda de clientes, falta de segurança, falta de credibilidade).
            3. Termine com uma chamada de ação (CTA) simples e direta para uma conversa de 10 minutos.
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return self._generate_fallback(lead.name, score, has_website, has_ssl, has_professional_email)

    def _generate_fallback(self, name, score, has_website, has_ssl, has_professional_email):
        if not has_website:
            return f"Olá equipe do {name},\n\n" \
                   f"Identifiquei que sua empresa é muito bem avaliada no Google Maps, mas atualmente não possui um site institucional próprio. Hoje, 80% das decisões de compra locais começam com uma busca na internet, e a falta de uma presença digital própria faz com que concorrentes menores apareçam na frente de vocês.\n\n" \
                   f"Desenvolvemos soluções sob medida que colocam empresas de destaque no topo dos resultados em poucos dias, permitindo receber contatos diretos de novos clientes de forma totalmente automatizada.\n\n" \
                   f"Podemos agendar uma rápida conversa de 10 minutos nesta semana para eu te mostrar como isso funcionará para vocês?"
        elif not has_ssl:
            return f"Olá equipe do {name},\n\n" \
                   f"Dando uma olhada no site de vocês, notei que os navegadores (Chrome/Safari) o marcam como 'Não Seguro' devido à ausência do certificado de segurança SSL. Isso afasta potenciais clientes que entram no site por medo de fraudes e prejudica seu ranqueamento no Google.\n\n" \
                   f"Corrigir essa falha de segurança leva poucas horas e eleva imediatamente o nível de confiança profissional que sua marca transmite aos visitantes online.\n\n" \
                   f"Que tal falarmos por 10 minutos nesta semana para resolvermos esse problema e garantirmos a integridade dos seus dados?"
        else:
            return f"Olá equipe do {name},\n\n" \
                   f"Achei fantástico o trabalho de vocês online. Entretanto, notei que o e-mail de contato principal ainda usa um domínio genérico (@gmail/@hotmail). Em transações B2B, o uso de e-mails corporativos aumenta a taxa de abertura de propostas e a credibilidade geral do negócio.\n\n" \
                   f"Podemos ajudar a configurar e-mails profissionais dedicados com seu próprio domínio sem qualquer atrito técnico, dando mais formalidade à sua marca.\n\n" \
                   f"Podemos agendar uma breve conversa de 10 minutos nesta semana para alinhar essa melhoria?"

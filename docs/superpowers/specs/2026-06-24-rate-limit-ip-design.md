# Design Spec: Limite de Requisições por IP e Pop-up de Venda/Feedback

**Data:** 2026-06-24  
**Status:** Aprovado pelo Usuário  
**Autor:** Antigravity

## 1. Objetivo e Requisitos
Limitar usuários que não possuem plano ativo a 3 buscas por IP por dia corrente. Quando o limite for atingido, exibir um pop-up de marketing persuasivo que:
1. Alerte sobre o limite grátis de 3 buscas atingido.
2. Apresente os benefícios do upgrade de plano (Estratégia de Marketing).
3. Ofereça um incentivo secundário: Deixar um feedback sobre a plataforma em troca de +5 créditos de busca (limitado a 1 bônus por organização para evitar abusos).

## 2. Modelagem do Banco de Dados

### 2.1. Novo Modelo `IPRequestLog`
Armazena a contagem de requisições de buscas por IP por dia.
* **Localização**: `leads/models.py`
* **Campos**:
  * `ip_address`: `models.GenericIPAddressField()`
  * `date`: `models.DateField(default=django.utils.timezone.localdate)`
  * `count`: `models.PositiveIntegerField(default=0)`
* **Restrições**: `unique_together = ('ip_address', 'date')`

### 2.2. Novo Modelo `Feedback`
Armazena os feedbacks enviados pelos usuários.
* **Localização**: `leads/models.py`
* **Campos**:
  * `user`: `models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')`
  * `message`: `models.TextField()`
  * `created_at`: `models.DateTimeField(auto_now_add=True)`

### 2.3. Novo Campo em `Organization`
* **Localização**: `accounts/models.py`
* **Campo**:
  * `received_feedback_bonus`: `models.BooleanField(default=False)`

## 3. Lógica das Views (`leads/views.py`)

### 3.1. Captura de IP
Função auxiliar para extrair o IP do cabeçalho da requisição:
```python
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

### 3.2. Controle de Limite em `search_studio_view`
* **Se o usuário não tem plano ativo** (`not request.user.is_active_plan`):
  * Obter IP do cliente.
  * Consultar ou criar o log para a data atual.
  * Se `log.count >= 3`:
    * Bloquear requisições POST com uma mensagem de erro ou flag.
    * No GET, passar `show_limit_modal = True` no contexto do template.
  * Se `log.count < 3` e a busca for realizada com sucesso (POST):
    * Incrementar o contador: `log.count += 1` e `log.save()`.

### 3.3. View de Feedback `submit_feedback_view`
* Método: `POST`
* Rota: `/leads/feedback/`
* Lógica:
  1. Cria o registro de `Feedback`.
  2. Obtém a organização do usuário.
  3. Se `org.received_feedback_bonus == False`:
     * Incrementa `credits_balance += 5`.
     * Define `received_feedback_bonus = True`.
     * Retorna JSON indicando concessão do bônus de créditos.
  4. Caso contrário, apenas salva o feedback sem adicionar créditos adicionais.

## 4. Roteamento (`leads/urls.py`)
Registrar a URL:
* `path('feedback/', views.submit_feedback_view, name='submit_feedback')`

## 5. Interface Gráfica (UI/UX)
No arquivo `templates/leads/search_studio.html`:
* Se `show_limit_modal` for verdadeiro:
  * Exibe um modal centralizado com overlay escuro desfocado (`backdrop-blur-md`).
  * Desabilita a possibilidade de fechar o modal clicando fora.
  * Mostra o banner de upgrade de plano ("Fazer Upgrade para Ilimitado") apontando para `accounts:payments_settings`.
  * Se o usuário ainda não tiver ganhado o bônus (`not request.user.organization.received_feedback_bonus`), exibe o formulário de feedback (textarea + botão de envio AJAX).
  * O envio AJAX dispara a rota `/leads/feedback/`, exibe uma mensagem de agradecimento, adiciona os 5 créditos e recarrega a página após 2 segundos para liberar o Search Studio.

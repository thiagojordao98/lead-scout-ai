# Design Spec: Padronização da Altura dos Cards do Kanban (CRM)

**Data:** 2026-06-24  
**Status:** Aprovado pelo Usuário  
**Autor:** Antigravity

## 1. Problema e Objetivo
Atualmente, os cards no pipeline de vendas (Kanban) utilizam a classe `h-full` de forma flexível. Quando uma coluna (estágio) possui apenas um card, o container flexível faz com que esse card estique verticalmente para ocupar toda a altura restante da coluna (mínimo de `500px`). Isso gera um visual desequilibrado e desproporcional.

O objetivo é padronizar a altura dos cards no desktop de forma fixa e elegante, enquanto mantemos a flexibilidade e adaptabilidade no mobile.

## 2. Solução Proposta
Ajustar o arquivo `templates/leads/crm_card_snippet.html` substituindo a classe de altura `h-full` do container principal do card por:
- `md:h-44` (176px) para telas desktop (médias e maiores), oferecendo uma altura fixa padrão onde as informações caibam perfeitamente com margem de segurança.
- `h-auto` para telas mobile (menores que `768px`), garantindo que o seletor nativo de mover estágio possa se expandir sem transbordar o card.

## 3. Alteração de Código
No arquivo [crm_card_snippet.html](file:///home/thiago/www/micro-saas/lead-scout-ai/templates/leads/crm_card_snippet.html), alterar o elemento principal:

```diff
-<div class="relative bg-white dark:bg-slate-950 p-4 rounded-xl ring-1 ring-slate-200/50 dark:ring-white/10 hover:ring-emerald-500/50 dark:hover:ring-emerald-500/50 transition-all shadow-md dark:shadow-lg cursor-pointer flex flex-col justify-between h-full text-slate-800 dark:text-slate-100"
+<div class="relative bg-white dark:bg-slate-950 p-4 rounded-xl ring-1 ring-slate-200/50 dark:ring-white/10 hover:ring-emerald-500/50 dark:hover:ring-emerald-500/50 transition-all shadow-md dark:shadow-lg cursor-pointer flex flex-col justify-between h-auto md:h-44 text-slate-800 dark:text-slate-100"
```

## 4. Validação e Testes
1. O pipeline de testes automatizados (`manage.py test`) deve passar sem regressões.
2. Visualmente, verificar se colunas com apenas 1 card exibem o card com a altura correta (176px no desktop) sem esticar.

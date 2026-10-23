# Planejamento Mensal — Lançamentos Editáveis

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transformar `/planning/monthly/` em uma tela operacional para incluir, editar e cancelar receitas e despesas do mês selecionado.

**Architecture:** Manter Django Templates + HTMX. As regras ficam em serviços do `ledger`; a tela de `planning` apenas resolve a família ativa, a competência e renderiza parciais. Cancelamento é lógico e auditável, sem exclusão física.

**Tech Stack:** Python 3.15, Django 6.1, PostgreSQL, Django Forms, HTMX, pytest e Ruff.

**Spec:** Requisitos acordados nesta conversa: duas tabelas separadas, botões “Nova entrada”/“Nova saída”, formulário para inclusão/edição e cancelamento auditável.

## Global Constraints

- Toda leitura e escrita deve respeitar a família ativa.
- Valores monetários permanecem como `Decimal`/`NUMERIC`.
- Competência selecionada filtra as duas tabelas.
- Lançamentos financeiros não podem ser apagados fisicamente.
- Respostas HTMX devem ter fallback funcional com HTML completo.

## Review Focus

- Usuário de outra família tentando editar ou cancelar: negar sem alterar o objeto.
- Categoria incompatível com receita/despesa: rejeitar no formulário e no serviço.
- Edição mudando competência: item sai da lista mensal atual e totais são recalculados.
- Lançamento cancelado: permanece no banco/auditoria e deixa de aparecer nos totais ativos.
- Requisições sem HTMX: continuam funcionando com redirecionamento/renderização normal.

### Task 1: Serviços e testes de alteração/cancelamento

**Files:**
- Modify: `ledger/services.py`
- Test: `ledger/tests/test_services.py`
- Test: `ledger/tests/test_audit.py`

- [x] Escrever testes falhando para atualizar receita/despesa, manter família/tipo e cancelar com auditoria.
- [x] Implementar serviços transacionais `update_income`, `update_expense` e `cancel_financial_event` usando snapshot antes/depois.
- [x] Rodar os testes do ledger/audit e confirmar verde.

### Task 2: Formulários, views e rotas de planejamento

**Files:**
- Modify: `ledger/forms.py`
- Modify: `planning/views.py`
- Modify: `planning/urls.py`
- Test: `planning/tests/test_views.py`

- [x] Escrever testes HTTP para exibir as duas tabelas, incluir, editar, cancelar, filtrar competência e bloquear outra família.
- [x] Implementar formulário de lançamento parametrizado por tipo e views protegidas por família.
- [x] Adicionar rotas de inclusão, edição e cancelamento com contexto mensal preservado.
- [x] Rodar os testes de planning e ledger.

### Task 3: Interface em tabelas separadas

**Files:**
- Modify: `templates/planning/monthly.html`
- Create: `templates/planning/_transaction_table.html`
- Create: `templates/planning/_transaction_form.html`
- Modify: `core/static/css/app.css`

- [x] Renderizar entradas e saídas em tabelas responsivas com ações por linha.
- [x] Adicionar formulários de inclusão/edição via HTMX e fallback não-HTMX.
- [x] Adicionar confirmação de cancelamento e mensagens de sucesso/erro.
- [x] Ajustar visual para leitura de planilha, estados vazios e mobile.

### Task 4: Verificação final

- [x] Rodar `make check-django`, `make test`, `make quality` e `make deploy-check`.
- [x] Conferir diff, branch e arquivos alterados.

# Navegação e onboarding inicial — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Tornar a aplicação utilizável desde a primeira entrada, com navegação real, dashboard contextual e criação da primeira conta.

**Architecture:** Reutilizar Django Templates, os serviços existentes de `identity` e `ledger` e o resumo mensal já implementado. O dashboard decide entre os estados sem família, sem conta e com dados; o layout base centraliza os links.

**Tech Stack:** Django 6.1, Django Templates, pytest-django, CSS existente.

**Spec:** `.ai/decisions/0009-family-context-and-roles.md`, `.ai/decisions/0010-money-and-rounding.md` e `docs/superpowers/specs/2026-10-23-junance-domain-slices-design.md`.

## Global Constraints

- Toda entidade financeira permanece vinculada à família autorizada.
- Valores monetários continuam usando `Decimal`/`NUMERIC`.
- Alterações de comportamento devem ter teste antes do código.
- Não introduzir SPA, dependências novas ou dados fictícios automáticos.
- A navegação deve apontar apenas para rotas existentes e respeitar autenticação.

## Review Focus

- Usuário autenticado sem família: dashboard deve orientar criação, sem tentar consultar dados financeiros.
- Família sem contas: dashboard deve oferecer o primeiro passo de cadastro.
- Formulário de conta com valor inicial decimal inválido: deve rejeitar a entrada.
- Conta de outra família: não pode aparecer nem ser aceita pelo fluxo de onboarding.
- Usuário anônimo: dashboard público não deve quebrar e links protegidos devem direcionar ao login/admin existente.

### Task 1: Dashboard contextual

**Files:**
- Modify: `core/views.py`
- Modify: `templates/core/dashboard.html`
- Test: `core/tests/test_dashboard.py`

- [ ] Escrever testes para os três estados do dashboard e para os links de navegação.
- [ ] Executar os testes e observar falha antes da implementação.
- [ ] Usar `get_active_family`, `family_accounts` e `monthly_summary` para fornecer contexto mínimo.
- [ ] Renderizar CTA de família, CTA de conta ou resumo mensal conforme o estado.
- [ ] Executar testes da unidade e depois a suíte completa.
- [ ] Commit: `feat: transformar painel em ponto de entrada`

### Task 2: Navegação global

**Files:**
- Modify: `templates/base.html`
- Modify: `core/static/css/app.css`
- Test: `core/tests/test_dashboard.py`

- [ ] Tornar os itens existentes links para dashboard, famílias, ledger, cartões, importações, planejamento e investimentos.
- [ ] Destacar o item ativo sem duplicar lógica por página.
- [ ] Adicionar ações de contexto para criar família, conta e lançamento.
- [ ] Validar os nomes reversos e os links renderizados.
- [ ] Commit: `feat: conectar navegação principal`

### Task 3: Cadastro da primeira conta

**Files:**
- Create: `ledger/forms.py` (extensão)
- Modify: `ledger/views.py`
- Modify: `ledger/urls.py`
- Modify: `identity/views.py`
- Create: `templates/ledger/account_form.html`
- Test: `ledger/tests/test_views.py`, `identity/tests/test_views.py`

- [ ] Escrever teste GET/POST do cadastro e isolamento do queryset por família.
- [ ] Executar os testes e observar falha antes da implementação.
- [ ] Criar `AccountForm` com nome, tipo e saldo inicial decimal.
- [ ] Criar `account_create` protegido, delegando persistência a `create_account`.
- [ ] Redirecionar a criação de família para o dashboard, que orientará o cadastro da conta.
- [ ] Executar testes específicos e a suíte completa.
- [ ] Commit: `feat: adicionar onboarding da primeira conta`

### Task 4: Verificação e documentação

**Files:**
- Modify: `README.md`

- [ ] Atualizar o fluxo de teste local e as rotas iniciais.
- [ ] Executar `make check-django`, `make test` e `make quality`.
- [ ] Revisar diff, migrações e links sem alteração de banco.
- [ ] Commit: `docs: documentar fluxo inicial da aplicação`

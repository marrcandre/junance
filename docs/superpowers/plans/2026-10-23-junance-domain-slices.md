# Junance Domain Slices Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir os primeiros fluxos financeiros do Junance em fatias verticais, com autorização por família, efeitos financeiros explícitos, rastreabilidade e importações revisáveis.

**Architecture:** O Junance continuará como um monólito modular Django. Cada domínio reunirá modelos, serviços transacionais, formulários, URLs, views, templates e testes; as views resolverão o contexto autorizado e delegarão regras financeiras aos serviços. PostgreSQL será o banco oficial e Django Templates + HTMX a interface principal.

**Tech Stack:** Python 3.15, Django 6.1, PostgreSQL 17, `uv`, Django Templates, HTMX, pytest, pytest-django, Ruff e Docker Compose apenas para PostgreSQL local.

**Spec:** `docs/superpowers/specs/2026-10-23-junance-domain-slices-design.md`

## Global Constraints

- Toda entidade financeira deve possuir vínculo com uma família.
- Toda leitura e escrita deve respeitar a família autorizada.
- Papéis de família devem ser explícitos e testados.
- Valores monetários usam `Decimal` no Python e `NUMERIC` no PostgreSQL.
- Compra no cartão registra despesa e obrigação.
- Pagamento de fatura liquida obrigação e não cria uma segunda despesa.
- Transferência entre contas próprias não é receita nem despesa.
- Operações financeiras relacionadas devem ser transacionais.
- Correções e exclusões que afetem o histórico precisam de rastreabilidade.
- Importações passam por recebimento, identificação, normalização, validação, prévia, confirmação, idempotência e auditoria.
- Arquivos reais devem ser anonimizados antes de entrar no repositório ou em artefatos de desenvolvimento.
- Não introduzir SPA, microsserviços, Redis, Celery, Django REST Framework ou outra dependência sem ADR aprovado.
- Usar os comandos oficiais do Makefile e não alterar banco de produção durante desenvolvimento ou deploy.

## Review Focus

- Usuário pertencente a duas famílias: a consulta e a escrita devem usar somente a família ativa autorizada; coberto na Task 2.
- Usuário sem papel suficiente: a operação deve retornar negativa sem revelar existência do objeto; coberto na Task 2.
- Valor monetário com casas, sinal ou arredondamento inválido: a operação deve rejeitar entrada sem converter para `float`; coberto na Task 3.
- Transferência, pagamento de fatura e investimento: os eventos devem aparecer nos saldos corretos sem virar receita ou despesa indevida; coberto nas Tasks 3, 5 e 8.
- Reprocessamento de arquivo confirmado: não deve criar registros financeiros duplicados e deve preservar a origem; coberto na Task 6.

## Mapa de arquivos e responsabilidades

Os nomes abaixo são o alvo de organização. Se a primeira tarefa revelar uma
convenção Django melhor, a mudança deve ser registrada no ADR da etapa antes de
criar os modelos.

- `core/`: dashboard e elementos compartilhados existentes.
- `identity/`: usuários, famílias, membros, papéis e contexto autorizado.
- `ledger/`: contas, categorias, receitas, despesas, transferências e consultas de saldo.
- `cards/`: cartões, compras, parcelas, faturas e liquidações.
- `audit/`: eventos de auditoria e trilha de alterações.
- `imports/`: recebimento, adaptadores, normalização, validação, prévia e confirmação.
- `planning/`: orçamentos, competências e relatórios.
- `investments/`: posições, aportes, resgates e rentabilidade.
- `templates/<app>/`: telas completas e parciais HTMX de cada domínio.
- `tests/` dentro de cada app: testes unitários, de serviço, autorização e integração HTTP.
- `.ai/decisions/`: ADRs para decisões que condicionem persistência ou segurança.

### Task 1: Fechar convenções da fundação

**Files:**
- Create: `.ai/decisions/0008-domain-module-layout.md`
- Modify: `.ai/roadmap.md`
- Modify: `README.md`
- Modify: `Makefile` apenas se algum gate necessário estiver ausente
- Test: `core/tests/test_project_health.py`

**Interfaces:**
- Produces: convenção final para apps por domínio, contexto de família, localização de serviços e política de migrations.

- [ ] **Step 1: Escrever checks de saúde do projeto** — cobrir `manage.py check`, rotas públicas existentes, carregamento de templates e execução dos comandos oficiais sem banco de produção.
- [ ] **Step 2: Rodar os checks para estabelecer a linha de base**

Run: `make check-django && make test && make quality`

Expected: checks passam com a fundação atual.

- [ ] **Step 3: Registrar as convenções e limites da primeira implementação** — documentar nomes dos apps, local dos serviços, política de migrations e regras para contexto autorizado.
- [ ] **Step 4: Atualizar roadmap e documentação operacional** — marcar a fundação técnica como concluída somente se os gates permanecerem verdes.
- [ ] **Step 5: Rodar a validação completa**

Run: `make check-django && make test && make quality && make deploy-check`

Expected: todos os comandos passam; limitações do ambiente ficam documentadas.

- [ ] **Step 6: Commit**

```bash
git add .ai/decisions/0008-domain-module-layout.md .ai/roadmap.md README.md Makefile core/tests/test_project_health.py
git commit -m "docs: fechar convenções da fundação"
```

### Task 2: Implementar identidade, famílias e papéis

**Files:**
- Create: `identity/models.py`
- Create: `identity/services.py`
- Create: `identity/permissions.py`
- Create: `identity/forms.py`
- Create: `identity/urls.py`
- Create: `identity/views.py`
- Create: `identity/admin.py`
- Create: `templates/identity/family_list.html`
- Create: `templates/identity/family_form.html`
- Test: `identity/tests/test_models.py`
- Test: `identity/tests/test_services.py`
- Test: `identity/tests/test_permissions.py`
- Test: `identity/tests/test_views.py`

**Interfaces:**
- Produces: `Family`, `FamilyMember`, `FamilyRole`, `get_active_family(request)`, `require_family_membership(user, family)` e serviços para criar família e alterar membro.
- Consumes: usuário padrão do Django e convenções definidas na Task 1.

- [ ] **Step 1: Escrever testes de modelo e papéis** — verificar unicidade do membro por família/usuário, papel explícito e impossibilidade de criar associação sem família.
- [ ] **Step 2: Rodar os testes para confirmar a falha**

Run: `uv run --locked pytest identity/tests/test_models.py -q`

Expected: FAIL porque os modelos ainda não existem.

- [ ] **Step 3: Implementar os modelos com constraints de banco** — usar relações explícitas, índices para consultas autorizadas e valores de papel estáveis.
- [ ] **Step 4: Escrever testes de serviços e isolamento** — cobrir criação da família, associação, troca de contexto, acesso negado entre duas famílias e papel insuficiente.
- [ ] **Step 5: Implementar `get_active_family` e permissões** — retornar somente família selecionada e pertencente ao usuário; não revelar objetos de outra família.
- [ ] **Step 6: Escrever testes HTTP** — cobrir login, criação/listagem de famílias e respostas de acesso negado.
- [ ] **Step 7: Implementar formulários, views, URLs e templates server-rendered** — manter o fluxo funcional sem depender de JavaScript.
- [ ] **Step 8: Rodar a fatia completa**

Run: `uv run --locked pytest identity -q && make check-django && make quality`

Expected: todos os testes de identidade passam e Ruff não aponta erros.

- [ ] **Step 9: Commit**

```bash
git add identity templates/identity
git commit -m "feat: adicionar famílias e papéis de acesso"
```

### Task 3: Implementar contas, categorias e movimentações

**Files:**
- Create: `ledger/models.py`
- Create: `ledger/services.py`
- Create: `ledger/queries.py`
- Create: `ledger/forms.py`
- Create: `ledger/urls.py`
- Create: `ledger/views.py`
- Create: `templates/ledger/account_list.html`
- Create: `templates/ledger/transaction_list.html`
- Create: `templates/ledger/transaction_form.html`
- Test: `ledger/tests/test_models.py`
- Test: `ledger/tests/test_services.py`
- Test: `ledger/tests/test_queries.py`
- Test: `ledger/tests/test_views.py`

**Interfaces:**
- Produces: `Account`, `Category`, `Income`, `Expense`, `Transfer`, `record_income(...)`, `record_expense(...)`, `record_transfer(...)` e consultas filtradas por família/período.
- Consumes: `get_active_family`, permissões e membros da Task 2.

- [ ] **Step 1: Escrever testes de domínio** — cobrir vínculo obrigatório à família, `Decimal`, sinais, moeda, datas de transação/competência/pagamento e transferência entre contas da mesma família.
- [ ] **Step 2: Rodar os testes para confirmar a falha**

Run: `uv run --locked pytest ledger/tests/test_services.py -q`

Expected: FAIL antes dos modelos e serviços.

- [ ] **Step 3: Implementar modelos e constraints** — usar `NUMERIC`, choices explícitos e relações de família em cada entidade financeira.
- [ ] **Step 4: Implementar serviços transacionais** — usar `transaction.atomic()`, validar contas e categorias no contexto da família e impedir transferência para a mesma conta ou outra família.
- [ ] **Step 5: Escrever testes de autorização e queries** — garantir que listagens, totais e detalhes nunca retornem dados de outra família.
- [ ] **Step 6: Implementar consultas e telas** — entregar contas, categorias mínimas, lançamento e listagem filtrada por competência.
- [ ] **Step 7: Validar saldos e classificação** — demonstrar por teste que transferência não é receita/despesa e que os totais respeitam o período correto.
- [ ] **Step 8: Rodar a fatia completa**

Run: `uv run --locked pytest ledger -q && make check-django && make quality`

Expected: testes de domínio, isolamento e HTTP passam.

- [ ] **Step 9: Commit**

```bash
git add ledger templates/ledger
git commit -m "feat: adicionar contas e movimentações"
```

### Task 4: Adicionar correções e auditoria do núcleo

**Files:**
- Create: `audit/models.py`
- Create: `audit/services.py`
- Create: `audit/queries.py`
- Modify: `ledger/models.py`
- Modify: `ledger/services.py`
- Test: `audit/tests/test_services.py`
- Test: `ledger/tests/test_audit.py`

**Interfaces:**
- Produces: `AuditEvent`, `record_audit_event(...)`, operações de correção/cancelamento com ator, timestamp, motivo e referência ao evento original.
- Consumes: eventos do `ledger` e usuário/família da Task 2.

- [ ] **Step 1: Escrever testes de histórico** — alteração autorizada registra ator, motivo e valores relevantes; exclusão física de evento usado é recusada.
- [ ] **Step 2: Rodar os testes para confirmar a falha**
- [ ] **Step 3: Implementar `AuditEvent` e serviço de auditoria** — garantir vínculo com família e transação atômica com a alteração financeira.
- [ ] **Step 4: Implementar correção/cancelamento no ledger** — manter histórico consultável e impedir mudança direta de eventos encerrados sem serviço autorizado.
- [ ] **Step 5: Rodar testes de regressão e qualidade**

Run: `uv run --locked pytest audit ledger -q && make quality`

Expected: alterações financeiras e trilha de auditoria passam juntas.

- [ ] **Step 6: Commit**

```bash
git add audit ledger
git commit -m "feat: rastrear correções financeiras"
```

### Task 5: Implementar cartões, compras, parcelas e faturas

**Files:**
- Create: `cards/models.py`
- Create: `cards/services.py`
- Create: `cards/queries.py`
- Create: `cards/forms.py`
- Create: `cards/urls.py`
- Create: `cards/views.py`
- Create: `templates/cards/card_list.html`
- Create: `templates/cards/purchase_form.html`
- Create: `templates/cards/invoice_detail.html`
- Test: `cards/tests/test_models.py`
- Test: `cards/tests/test_services.py`
- Test: `cards/tests/test_double_counting.py`
- Test: `cards/tests/test_views.py`

**Interfaces:**
- Produces: `Card`, `Invoice`, `Purchase`, `Installment`, `record_card_purchase(...)`, `settle_invoice(...)`.
- Consumes: família, auditoria e contas do `ledger`.

- [ ] **Step 1: Escrever testes de compra e parcelamento** — compra à vista e parcelada preservam vínculos, competência e obrigação.
- [ ] **Step 2: Escrever teste de não dupla contabilização** — pagar fatura reduz obrigação e saldo, mas não cria nova despesa.
- [ ] **Step 3: Rodar os testes para confirmar a falha**
- [ ] **Step 4: Implementar modelos e constraints** — todas as entidades pertencem à família e as parcelas vinculam compra e fatura.
- [ ] **Step 5: Implementar serviços transacionais** — compra cria despesa/obrigação; pagamento liquida obrigação e gera os efeitos de caixa previstos sem duplicar despesa.
- [ ] **Step 6: Implementar telas e consultas de fatura** — listar parcelas, competência, vencimento, total aberto e pagamentos autorizados.
- [ ] **Step 7: Rodar validação completa**

Run: `uv run --locked pytest cards ledger -q && make check-django && make quality`

Expected: regras de cartão e ausência de dupla contabilização passam.

- [ ] **Step 8: Commit**

```bash
git add cards templates/cards ledger
git commit -m "feat: adicionar cartões e faturas"
```

### Task 6: Implementar importações revisáveis e conciliação inicial

**Files:**
- Create: `imports/models.py`
- Create: `imports/services.py`
- Create: `imports/adapters/base.py`
- Create: `imports/adapters/ofx.py`
- Create: `imports/adapters/csv.py`
- Create: `imports/adapters/xlsx.py`
- Create: `imports/validators.py`
- Create: `imports/urls.py`
- Create: `imports/views.py`
- Create: `templates/imports/upload.html`
- Create: `templates/imports/preview.html`
- Create: `templates/imports/result.html`
- Test: `imports/tests/fixtures/` com arquivos pequenos e anonimizados
- Test: `imports/tests/test_adapters.py`
- Test: `imports/tests/test_validation.py`
- Test: `imports/tests/test_idempotency.py`
- Test: `imports/tests/test_views.py`

**Interfaces:**
- Produces: `ImportBatch`, `NormalizedEntry`, `receive_file(...)`, `preview_import(...)`, `confirm_import(...)` e chave determinística de idempotência.
- Consumes: contas/cartões, eventos do `ledger`/`cards` e auditoria.

- [ ] **Step 1: Definir fixtures anonimizadas e contrato normalizado** — incluir data, valor `Decimal`, sinal, descrição, identificador de origem, conta/cartão e tipo candidato.
- [ ] **Step 2: Escrever testes de adaptadores e validação** — cobrir formatos válidos, datas inválidas, sinais ambíguos, duplicidades e arquivo malformado.
- [ ] **Step 3: Rodar os testes para confirmar a falha**
- [ ] **Step 4: Implementar recebimento e adaptadores separados** — não misturar parsing específico de OFX, CSV e XLSX.
- [ ] **Step 5: Implementar prévia e confirmação** — nenhuma entrada financeira persistida antes da confirmação explícita.
- [ ] **Step 6: Implementar idempotência e auditoria** — repetir o mesmo arquivo/processo não cria duplicatas e mantém origem, ator e resultado.
- [ ] **Step 7: Implementar conciliação inicial** — permitir vincular entrada normalizada a evento existente sem ultrapassar a família autorizada.
- [ ] **Step 8: Rodar validação completa**

Run: `uv run --locked pytest imports -q && make check-django && make quality`

Expected: prévia, confirmação, rejeição e reprocessamento ficam cobertos.

- [ ] **Step 9: Commit**

```bash
git add imports templates/imports
git commit -m "feat: adicionar importações revisáveis"
```

### Task 7: Implementar planejamento e relatórios

**Files:**
- Create: `planning/models.py`
- Create: `planning/services.py`
- Create: `planning/queries.py`
- Create: `planning/urls.py`
- Create: `planning/views.py`
- Create: `templates/planning/monthly.html`
- Create: `templates/planning/budget_form.html`
- Test: `planning/tests/test_services.py`
- Test: `planning/tests/test_queries.py`
- Test: `planning/tests/test_views.py`

**Interfaces:**
- Produces: `Budget`, `monthly_summary(family, competence)`, `budget_progress(...)`.
- Consumes: categorias e eventos classificados de `ledger`, liquidações de `cards` e contexto de família.

- [ ] **Step 1: Escrever testes de competência e totais** — separar transação, pagamento e competência; excluir transferências e pagamentos de fatura das despesas/receitas indevidas.
- [ ] **Step 2: Rodar os testes para confirmar a falha**
- [ ] **Step 3: Implementar orçamento e queries agregadas** — manter agregações no banco quando apropriado, sem converter dinheiro para `float`.
- [ ] **Step 4: Implementar visão mensal server-rendered** — fornecer filtros por competência, categoria e conta.
- [ ] **Step 5: Rodar testes de isolamento e qualidade**

Run: `uv run --locked pytest planning -q && make quality`

Expected: relatórios respeitam família, competência e tipos de evento.

- [ ] **Step 6: Commit**

```bash
git add planning templates/planning
git commit -m "feat: adicionar planejamento mensal"
```

### Task 8: Implementar investimentos como patrimônio

**Files:**
- Create: `investments/models.py`
- Create: `investments/services.py`
- Create: `investments/queries.py`
- Create: `investments/urls.py`
- Create: `investments/views.py`
- Create: `templates/investments/position_list.html`
- Test: `investments/tests/test_services.py`
- Test: `investments/tests/test_queries.py`
- Test: `investments/tests/test_views.py`

**Interfaces:**
- Produces: `InvestmentPosition`, `InvestmentTransaction`, `record_contribution(...)`, `record_withdrawal(...)`, `calculate_return(...)`.
- Consumes: contas, auditoria e contexto de família.

- [ ] **Step 1: Escrever testes patrimoniais** — aportes e resgates alteram posição e caixa, mas não entram automaticamente como receita/despesa operacional.
- [ ] **Step 2: Rodar os testes para confirmar a falha**
- [ ] **Step 3: Implementar modelos e serviços transacionais** — separar posição, movimentação e rentabilidade; usar `Decimal`.
- [ ] **Step 4: Implementar consultas e telas** — listar posição, histórico e rentabilidade com período explícito.
- [ ] **Step 5: Rodar validação completa**

Run: `uv run --locked pytest investments planning -q && make check-django && make quality`

Expected: patrimônio permanece separado dos relatórios de receita e despesa.

- [ ] **Step 6: Commit**

```bash
git add investments templates/investments
git commit -m "feat: adicionar posições de investimentos"
```

### Task 9: Consolidar operação, segurança e documentação

**Files:**
- Modify: `.ai/roadmap.md`
- Create: `.ai/decisions/` ADRs das decisões abertas
- Modify: `README.md`
- Modify: `.github/workflows/ci.yml`
- Create: `docs/operations/` documentação de backup, migrations e dados de teste
- Test: suíte completa do projeto

**Interfaces:**
- Consumes: todos os domínios implementados.
- Produces: gates de entrega, documentação operacional e critérios para primeira implantação controlada.

- [ ] **Step 1: Escrever testes de integração da jornada principal** — família → conta → lançamento → cartão/fatura → importação → relatório.
- [ ] **Step 2: Executar a suíte completa em banco PostgreSQL local**

Run: `make db-up && make migrate && make test-cov`

Expected: testes passam sem banco de produção e com `DATABASE_URL` apontando para `localhost`/`127.0.0.1`.

- [ ] **Step 3: Fechar ADRs das decisões abertas** — matriz de papéis, família ativa, retenção de auditoria, idempotência, moeda e arredondamento.
- [ ] **Step 4: Documentar operação segura** — migrations explícitas, backup/restauração, dados anonimizados e procedimento de deploy.
- [ ] **Step 5: Validar todos os gates**

Run: `make check-django && make test && make quality && make deploy-check`

Expected: todos os checks passam ou a limitação fica registrada antes da entrega.

- [ ] **Step 6: Commit**

```bash
git add .ai .github/workflows/ci.yml README.md docs/operations
git commit -m "docs: consolidar operação segura do Junance"
```

## Critério de encerramento

O plano estará concluído quando cada etapa tiver um fluxo mínimo demonstrável,
testes de domínio e isolamento, migration revisada, documentação atualizada,
commit pequeno e os gates oficiais executados. A conclusão não autoriza
importar dados reais ou alterar produção sem uma etapa operacional aprovada.

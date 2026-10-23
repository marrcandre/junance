# ADR 0008 — Organização dos módulos de domínio

- Status: aceito
- Data: 2026-10-23

## Decisão

Organizar o monólito Django por módulos de domínio, mantendo modelos, serviços,
consultas, formulários, views, URLs e testes próximos de cada contexto.

## Motivo

As regras financeiras precisam ser implementadas em fatias verticais pequenas,
com comportamento verificável antes de ampliar abstrações compartilhadas.

## Convenções

- `identity` concentra usuários, famílias, membros, papéis e contexto ativo.
- `ledger` concentra contas, categorias e movimentações básicas.
- `cards` concentra cartões, compras, parcelas e faturas.
- `audit` concentra a trilha de alterações e eventos de auditoria.
- `imports` concentra recebimento, adaptadores, normalização e confirmação.
- `planning` concentra orçamentos e relatórios.
- `investments` concentra posições e movimentações patrimoniais.
- `core` permanece responsável pelo dashboard e elementos compartilhados.
- Regras que alteram mais de uma entidade vivem em serviços transacionais,
  usando `transaction.atomic()`.
- Toda entidade financeira possui `family` obrigatório e toda consulta recebe
  o contexto autorizado explicitamente.
- Cada app mantém seus testes de modelo, serviço, autorização e HTTP junto do
  domínio correspondente.

## Migrations e operação

Migrations são geradas e revisadas em cada etapa. O desenvolvimento usa apenas
o PostgreSQL local iniciado por `make db-up`; não se apagam bancos para
contornar falhas de migration. Deploys não executam migrations
automaticamente.

## Consequência

Os nomes e fronteiras podem evoluir quando o domínio for melhor compreendido,
mas qualquer mudança que afete autorização, persistência ou importação deve
ser registrada em novo ADR antes de orientar os modelos seguintes.

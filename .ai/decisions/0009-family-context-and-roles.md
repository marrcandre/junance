# ADR 0009 — Contexto ativo e papéis de família

- Status: aceito
- Data: 2026-10-23

## Decisão

O contexto ativo será selecionado pela sessão somente entre famílias às quais o
usuário pertence; proprietário e administrador podem gerenciar membros, e
membro pode operar dados autorizados sem gerenciar associação.

## Consequência

Toda consulta financeira deve receber a família resolvida pelo contexto
autorizado. Famílias sem associação válida não podem ser selecionadas por
alteração manual do identificador da sessão.

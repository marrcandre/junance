# ADR 0003 — PostgreSQL e uv

- Status: aceito
- Data: 2026-10-23

## Decisão

Usar PostgreSQL como banco oficial e `uv` como gerenciador de Python,
dependências e lockfile.

## Motivo

PostgreSQL fornece os tipos e garantias adequados ao domínio financeiro.
`uv` mantém instalação reproduzível e comandos locais consistentes.

## Consequência

O Compose executa somente o PostgreSQL local. O Django roda no ambiente Python
local e usa `DATABASE_URL` com `localhost`/`127.0.0.1`.

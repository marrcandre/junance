# ADR 0001 — Monólito modular Django

- Status: aceito
- Data: 2026-10-23

## Decisão

Usar um único projeto Django, organizado em módulos de domínio, como unidade
inicial de aplicação.

## Motivo

O produto ainda está validando regras financeiras. Um monólito reduz operação,
latência e complexidade de deploy, mantendo espaço para separação interna.

## Consequência

Serviços e módulos devem ter limites claros. Microsserviços só serão avaliados
quando houver uma necessidade operacional comprovada.

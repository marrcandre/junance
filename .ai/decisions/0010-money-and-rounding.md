# ADR 0010 — Moeda e arredondamento inicial

- Status: aceito
- Data: 2026-10-23

## Decisão

O Junance usará valores em reais brasileiros, com `Decimal` no Python e
`NUMERIC(14,2)` para valores monetários; quantidades patrimoniais podem usar
mais casas decimais, sem converter dinheiro para `float`.

## Consequência

Parcelamentos distribuem centavos restantes nas primeiras parcelas. Qualquer
suporte a múltiplas moedas ou mudança de precisão exige novo ADR e migração
revisada.

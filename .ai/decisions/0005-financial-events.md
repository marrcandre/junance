# ADR 0005 — Eventos financeiros sem dupla contabilização

- Status: aceito
- Data: 2026-10-23

## Decisão

Modelar eventos com efeitos financeiros distintos: compra, pagamento de
fatura, transferência, parcela e posição de investimento não são o mesmo tipo
de evento.

## Regras

- Compra no cartão cria despesa e obrigação.
- Pagamento de fatura liquida obrigação, sem nova despesa.
- Transferência própria altera saldos, sem receita ou despesa.
- Investimento representa posição patrimonial.

## Consequência

Relatórios e importações precisam conhecer o tipo e o vínculo do evento, em vez
de inferir tudo a partir de um lançamento genérico.

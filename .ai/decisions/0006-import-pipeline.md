# ADR 0006 — Importação revisável e idempotente

- Status: aceito
- Data: 2026-10-23

## Decisão

Importações serão independentes da instituição e passarão por recebimento,
identificação, normalização, validação, prévia, confirmação e auditoria.

## Motivo

Arquivos de Nubank, C6, Mercado Pago e outras origens podem ter formatos e
semânticas diferentes. A importação direta dificultaria correção e auditoria.

## Consequência

Arquivos reais devem ser anonimizados. Cada registro importado deve preservar
origem e processo, e repetir o mesmo arquivo não pode criar duplicatas.

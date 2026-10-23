# ADR 0011 — Idempotência e retenção de importações

- Status: aceito
- Data: 2026-10-23

## Decisão

Uma importação é identificada pelo hash do conteúdo dentro da família; suas
entradas normalizadas preservam o identificador externo, origem e auditoria.
Registros financeiros confirmados não são apagados para reprocessar arquivos.

## Consequência

Repetir o mesmo arquivo retorna o lote existente e não cria duplicatas. Dados
reais devem ser anonimizados em fixtures e a política de retenção de arquivos
originais deve ser definida antes da operação em produção.

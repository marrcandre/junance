# ADR 0004 — Família como limite de isolamento

- Status: aceito
- Data: 2026-10-23

## Decisão

Todo dado financeiro pertence a uma família, e toda leitura ou escrita deve
ser autorizada no contexto de uma família.

## Motivo

O produto atende finanças pessoais e familiares. Isolamento acidental ou
implícito seria um risco de segurança e privacidade.

## Consequência

Famílias, membros e papéis devem ser implementados antes dos modelos
financeiros. Testes de acesso entre famílias são obrigatórios.

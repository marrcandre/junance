# ADR 0002 — Templates Django e HTMX

- Status: aceito
- Data: 2026-10-23

## Decisão

Usar Django Templates como interface principal e HTMX para interações
incrementais.

## Motivo

Isso preserva uma aplicação simples, com boa entrega inicial, sem exigir uma
SPA, uma API pública ou uma segunda cadeia de build.

## Consequência

Views, templates e respostas parciais devem continuar acessíveis sem depender
de JavaScript complexo.

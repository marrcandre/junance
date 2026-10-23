# Importação da planilha mensal — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Importar a planilha mensal de Ju e Marco em uma conta histórica, com prévia, confirmação, categorias e idempotência.

**Architecture:** Estender o adaptador XLSX nativo existente para reconhecer tanto o formato tabular canônico quanto as abas mensais `MMYY`. O lote de importação terá uma conta de destino; a confirmação criará receitas/despesas no ledger usando serviços transacionais existentes.

**Tech Stack:** Django 6.1, PostgreSQL, XML/XLSX nativo da biblioteca padrão, Django Templates, pytest-django.

**Spec:** `.ai/decisions/0005-financial-events.md`, `.ai/decisions/0006-import-pipeline.md`, `.ai/decisions/0010-money-and-rounding.md`.

## Global Constraints

- Dados financeiros usam `Decimal` e permanecem vinculados à família.
- Investimentos, saldos e subtotais da planilha não viram despesas automaticamente.
- A confirmação é transacional, auditável e idempotente.
- O arquivo real do usuário não entra no repositório nem em fixtures.

## Review Focus

- Fórmulas com valor armazenado: usar o valor calculado disponível no XLSX, nunca a fórmula como dinheiro.
- Valores brasileiros com `R$`, ponto de milhar e vírgula decimal.
- Subtotais, saldos e cabeçalhos não devem virar lançamentos.
- Abas mensais sem data detalhada usam o primeiro dia da competência.
- Reconfirmação do mesmo lote não deve duplicar receitas, despesas ou categorias.

### Tasks

- [ ] Escrever e validar testes do adaptador de abas mensais.
- [ ] Implementar leitura nativa de workbook e normalização das seções de receita/despesa.
- [ ] Associar lote a conta e persistir lançamentos/categorias na confirmação.
- [ ] Integrar a conta histórica ao upload e à prévia.
- [ ] Executar checks completos e atualizar documentação.

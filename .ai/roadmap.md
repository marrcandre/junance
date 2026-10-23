# Roadmap

## Etapa 1 — Fundação técnica

Estado: concluída.

- Django, Python, `uv`, PostgreSQL e Makefile.
- Templates, HTMX e CSS inicial.
- CI, testes e Ruff.
- Documentação operacional e decisões de engenharia.

Critério de saída: a aplicação possui comandos reproduzíveis, CI, testes,
lint, PostgreSQL local isolado e convenções registradas para os módulos de
domínio.

## Etapa 2 — Autenticação, famílias e permissões

Estado: concluída.

- Usuários e autenticação.
- Famílias, membros e papéis.
- Isolamento de consultas e escritas.
- Testes explícitos contra acesso entre famílias.

## Etapa 3 — Contas e movimentações

Estado: concluída.

- Contas bancárias e categorias.
- Receitas, despesas e transferências.
- Saldos e datas com semântica definida.
- Primeira experiência de consulta semelhante a uma planilha.

## Etapa 4 — Cartões e faturas

Estado: concluída.

- Compras, parcelamentos e faturas.
- Pagamentos e conciliação.
- Garantia de que uma compra e seu pagamento não dupliquem despesas.

## Etapa 5 — Importação

Estado: concluída para CSV, OFX e XLSX revisáveis; PDF permanece posterior.

- OFX, CSV e XLSX.
- Normalização por instituição.
- Prévia, deduplicação, confirmação e auditoria.
- PDFs posteriormente, com conferência reforçada.

## Etapa 6 — Planejamento, relatórios e investimentos

Estado: concluída na primeira fatia funcional.

- Orçamentos e acompanhamento mensal.
- Dashboard financeiro baseado em dados confiáveis.
- Posições e rentabilidade de investimentos.

Dados de planilhas históricas só devem ser importados depois que as regras de
domínio e as exceções forem validadas.

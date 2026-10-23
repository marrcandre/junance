# ADR 0007 — Mudanças pequenas e verificáveis

- Status: aceito
- Data: 2026-10-23

## Decisão

O desenvolvimento avançará em mudanças pequenas, versionadas e verificadas
com testes, checks e lint relevantes.

## Regras

- Inspecionar antes de editar.
- Testar comportamento antes de declarar conclusão.
- Não mascarar falhas removendo dados ou relaxando validações.
- Não executar ações destrutivas ou em produção sem autorização explícita.
- Relatar arquivos alterados e comandos executados.
- Fazer commits frequentes, pequenos e coerentes.
- Usar mensagens de commit em inglês, sem trailers ou metadados que atribuam
  o commit ao agente, ao Superpowers ou a outra ferramenta, salvo solicitação
  explícita.

## Consequência

Uma etapa só é considerada concluída quando houver evidência de validação, ou
quando a limitação do ambiente estiver explicitamente registrada.

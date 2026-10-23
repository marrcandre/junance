# Atualização de Python e Django

## Intenção

Usar as versões estáveis mais recentes solicitadas para manter a fundação do Junance atualizada.

## Escopo

- Atualizar o requisito do projeto para Python 3.15.
- Atualizar Django para a série 6.1.
- Regenerar o `uv.lock` com as versões compatíveis.
- Alinhar `.python-version`, Dockerfile, CI e documentação.

## Fora do escopo

- Alterar modelos, views, templates ou regras de negócio.
- Adicionar funcionalidades financeiras.
- Alterar a estratégia de deploy ou banco de dados.

## Abordagens consideradas

1. Python 3.15 + Django 6.1: escolhida, pois atende literalmente ao pedido de usar as versões mais recentes.
2. Python 3.14 + Django 5.2 LTS: mais conservadora, mas não representa as versões mais recentes.

## Critérios de verificação

Executar `uv lock`, sincronização das dependências, `manage.py check`, testes e Ruff. Se o ambiente não permitir atualizar o lockfile ou instalar dependências, reportar a limitação sem declarar a atualização como validada.

# Junance — instruções para agentes

## Objetivo

O Junance é uma aplicação web de controle financeiro pessoal e familiar. O
produto deve priorizar clareza, rastreabilidade e segurança dos dados antes de
ampliar funcionalidades.

As decisões duráveis ficam em `.ai/`. Leia os documentos relevantes antes de
alterar o domínio, o banco de dados, as importações ou as permissões.

## Arquitetura atual

- Monólito modular em Django.
- Python 3.15 e Django 6.1.
- Django Templates + HTMX + CSS responsivo.
- PostgreSQL 17 como banco oficial.
- `uv` como gerenciador de Python e dependências.
- Makefile como interface oficial de comandos locais.
- Docker Compose somente para o PostgreSQL local.
- GitHub Actions para checks, testes e lint.

Não introduza SPA, microsserviços, Redis, Celery, Django REST Framework ou
outras dependências sem uma necessidade concreta documentada em `.ai/`.

## Antes de editar

1. Leia `README.md`, este arquivo e os documentos `.ai/` relacionados.
2. Inspecione o estado atual do repositório e preserve alterações existentes.
3. Identifique o menor conjunto de arquivos necessário.
4. Para mudanças de comportamento, escreva ou ajuste o teste antes do código.
5. Não misture refatorações não relacionadas com a tarefa.

## Comandos oficiais

```bash
make sync
make check-django
make test
make quality
make deploy-check
make db-up
make migrate
make dev
```

Use `make db-up` antes de testes que dependam do PostgreSQL. Nunca use banco
de produção para testes. O `DATABASE_URL` local deve apontar para
`localhost`/`127.0.0.1`, não para o hostname interno `db`.

## Regras de domínio financeiro

- Valores monetários usam `Decimal` no Python e `NUMERIC` no PostgreSQL; nunca
  use `float` para dinheiro.
- Toda entidade financeira deve possuir vínculo com uma família.
- Toda leitura e escrita deve respeitar a família autorizada.
- Papéis de família devem ser explícitos e testados.
- Compra no cartão registra despesa e obrigação.
- Pagamento de fatura liquida obrigação e não cria uma segunda despesa.
- Transferência entre contas próprias altera saldos, mas não é receita nem
  despesa.
- Compras parceladas preservam o vínculo entre compra, parcelas e fatura.
- Investimentos representam posição patrimonial, não receita automática.
- Datas de transação, competência e pagamento não devem ser confundidas.
- Operações financeiras relacionadas devem ser transacionais.
- Correções e exclusões que afetem o histórico precisam de rastreabilidade.

## Importações

Importações futuras devem seguir o fluxo:

1. Receber o arquivo.
2. Identificar instituição, conta/cartão e formato.
3. Normalizar para uma estrutura interna.
4. Validar datas, valores, sinais e duplicidades.
5. Exibir prévia para conferência.
6. Confirmar e persistir de forma idempotente e auditável.

Arquivos OFX, CSV, XLSX e PDF devem ser tratados como origens distintas. Dados
reais precisam ser anonimizados antes de entrar no repositório ou em qualquer
artefato de desenvolvimento.

## Segurança e operações

- Nunca versionar senhas, tokens, chaves privadas ou extratos reais.
- Não executar ações destrutivas sem autorização explícita.
- Não alterar banco de produção durante build ou deploy automaticamente.
- Não remover dados para fazer testes passarem.
- Validar permissões com testes de isolamento entre famílias.
- Tratar qualquer falha de migração como problema a investigar, não como algo
  a contornar apagando o banco.

## Qualidade e entrega

Antes de declarar a tarefa concluída, execute as verificações relevantes e
relate o resultado real. Nunca diga que testes passaram sem executar os
comandos.

### Commits

- Faça commits com frequência, em unidades pequenas e coerentes.
- Cada commit deve representar uma mudança revisável e verificável.
- Use mensagens de commit em português, claras e consistentes com Conventional
  Commits quando aplicável. Os tipos convencionais (`feat`, `fix`, `docs`, etc.)
  podem permanecer em inglês; a descrição deve ser escrita em português.
- Não adicione trailers ou metadados de atribuição ao agente, ao Superpowers,
  ao Codex ou a qualquer outra ferramenta (`Co-authored-by`, `Generated-by`,
  `Signed-off-by` ou equivalentes), salvo solicitação explícita do usuário.
- Não agrupe mudanças não relacionadas apenas para reduzir o número de
  commits.

Na entrega, informe:

- arquivos criados, alterados ou removidos;
- decisões tomadas e eventuais desvios;
- comandos executados;
- resultado dos testes, checks e lint;
- limitações do ambiente, se houver.

Código e identificadores devem ser escritos em inglês. Mensagens de commit
devem ser escritas em português brasileiro.
Documentação e explicações podem ser escritas em português brasileiro.

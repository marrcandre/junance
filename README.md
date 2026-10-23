# Junance

Controle financeiro pessoal e familiar.

O Junance será desenvolvido incrementalmente com Django, Django Templates, HTMX e PostgreSQL. O ambiente Python usa **uv** para dependências e ambientes virtuais; o **Makefile** fornece comandos padronizados; o **Docker Compose** executa apenas o PostgreSQL localmente.

> Estado atual: fundação técnica concluída e tela inicial disponível. Ainda não há movimentações, cartões, famílias, autenticação própria nem importação financeira implementados.

## Stack

- Python 3.15
- uv para dependências, lockfile e ambiente virtual
- Django 6.1
- Django Templates + HTMX
- PostgreSQL 17 no ambiente local
- Supabase PostgreSQL para produção (a configurar)
- Docker Compose
- pytest + pytest-django + pytest-cov
- Ruff
- GitHub Actions

## 1. Preparar o ambiente

Requisitos: Git, `uv`, GNU Make e, para executar com containers, Docker Engine com Docker Compose.

No diretório do projeto, gere o lockfile e sincronize as dependências:

```bash
make lock
make sync
```

O `uv.lock` gerado deve ser versionado no Git. Depois de criar ou alterar dependências, revise as mudanças em `pyproject.toml` e `uv.lock` antes de fazer commit.

Comandos úteis:

```bash
make help
make test
make quality
make check-django
```

## 2. Executar localmente com PostgreSQL no Docker e Django via uv

Copie as variáveis locais:

```bash
cp .env.example .env
```

Inicie apenas o PostgreSQL pelo Docker Compose:

```bash
make db-up
```

Em seguida, execute migrations e servidor Django localmente pelo `uv`:

```bash
make migrate
make dev
```

Abra `http://127.0.0.1:8000`.

Para criar um administrador, em outro terminal:

```bash
make createsuperuser
```

Para parar o PostgreSQL:

```bash
make db-down
```

Os comandos Django do Makefile carregam automaticamente o arquivo `.env` antes de chamar o `uv`. A aplicação local conecta em `localhost:5432`; o nome `db` só é usado para comunicação entre containers e não faz parte deste fluxo.

O banco fica no volume Docker `junance_postgres_data`. **Não use `docker compose down -v` a menos que queira apagar o banco local.**

Para acompanhar o banco:

```bash
make logs
make db-shell
```

## 3. Comandos do Makefile

| Comando | Finalidade |
|---|---|
| `make sync` | Sincroniza dependências a partir de `pyproject.toml` e, quando presente, `uv.lock` |
| `make lock` | Gera/atualiza o lockfile |
| `make upgrade` | Atualiza dependências e sincroniza o ambiente |
| `make add package=django-filter` | Adiciona dependência de produção |
| `make add-dev package=pytest-mock` | Adiciona dependência de desenvolvimento |
| `make dev` | Inicia o servidor Django local |
| `make test` | Executa testes com pytest |
| `make test-cov` | Executa testes com relatório de cobertura |
| `make quality` | Executa lint e verifica formatação |
| `make db-up` | Inicia o PostgreSQL local em container |
| `make up` | Inicia o PostgreSQL em container |

Consulte `make help` para a lista completa.

## Convenções de desenvolvimento

O desenvolvimento segue fatias verticais por domínio. Famílias e permissões
serão implementadas antes dos dados financeiros; cada etapa deve incluir
testes de autorização e isolamento quando houver dados pertencentes a uma
família.

Regras que produzem efeitos financeiros relacionados devem ficar em serviços
transacionais, e não somente em views ou templates. Use `Decimal` para
dinheiro, mantenha dados de teste anonimizados e revise as decisões em `.ai/`
antes de alterar domínio, banco, importações ou permissões.

## 4. Subir para o GitHub

Crie um repositório vazio chamado `junance` na sua conta GitHub. Inclua o `uv.lock` gerado antes do primeiro commit. Não marque a opção de adicionar README, `.gitignore` ou licença, pois estes arquivos já existem aqui.

```bash
git init
git add .
git commit -m "chore: initialize Junance project"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/junance.git
git push -u origin main
```

Substitua `SEU_USUARIO` pelo seu usuário GitHub. O comando `git remote add` deve ser executado apenas uma vez. Se já houver um remote configurado, confira com `git remote -v` antes de alterá-lo.

## 5. Tentar obter junance.vercel.app

1. Entre na sua conta da Vercel.
2. Escolha **Add New → Project**.
3. Importe o repositório GitHub `junance`.
4. Mantenha a detecção de Django/Python da Vercel; não configure um build de frontend Node.
5. Antes de publicar, configure as variáveis de ambiente conforme a seção abaixo.
6. Faça o primeiro deploy e confira o domínio atribuído em **Settings → Domains**.

A Vercel não permite reservar antecipadamente nomes `*.vercel.app`; eles dependem da disponibilidade. Se `junance.vercel.app` não estiver disponível, escolha um nome alternativo, como `junance-financas.vercel.app`.

## 6. Variáveis de ambiente

Para desenvolvimento local, use `.env.example` como referência e mantenha `.env` fora do Git.

Para a Vercel, configure no painel do projeto:
- `DJANGO_SECRET_KEY`: uma chave secreta forte, exclusiva para produção.
- `DJANGO_DEBUG`: `0`.
- `DJANGO_ALLOWED_HOSTS`: o domínio de produção atribuído à aplicação.
- `DATABASE_URL`: URL de conexão PostgreSQL do Supabase, preferencialmente o endpoint indicado para o tipo de conexão escolhido.
- `DB_SSL_REQUIRE`: `1` se a conexão do Supabase exigir SSL.

Nunca faça commit de `.env`, senha do banco, token ou chave privada. Não envie segredos no chat.

## 7. Banco remoto e migrações

O Compose usa um PostgreSQL local, isolado do banco remoto, e o Django local se conecta a ele via `localhost`. O banco do Supabase ainda não está conectado nem foi criado por este pacote.

Antes de apontar para produção:
1. Crie o projeto Supabase e configure a URL de conexão.
2. Gere uma `DJANGO_SECRET_KEY` exclusiva.
3. Configure hosts e SSL.
4. Defina uma estratégia explícita para executar migrações de produção.
5. Teste a implantação com dados de teste, nunca importando o histórico financeiro diretamente.

Não executamos migrações automaticamente durante o build/deploy: isso evita alterar o banco de produção de forma inadvertida. O processo será definido antes de criarmos os modelos de domínio.

## 8. Próximas etapas

1. Fundação e execução local.
2. Famílias, membros e isolamento de dados com testes.
3. Contas, categorias, receitas, despesas e transferências.
4. Cartões, faturas e parcelamentos sem dupla contabilização.
5. Painel mensal e planejamento.
6. Auditoria/importação das planilhas históricas.
7. Investimentos e rentabilidade.

A modelagem financeira e a importação só avançarão após validar as regras de negócio e as exceções das planilhas.

# Junance

Controle financeiro pessoal e familiar.

O Junance será desenvolvido incrementalmente com Django, Django Templates, HTMX e PostgreSQL. O projeto foi preparado para desenvolvimento local com Docker Compose e para uma implantação futura na Vercel com PostgreSQL no Supabase.

> Estado atual: fundação técnica e tela inicial. Ainda não há movimentações, cartões, famílias, autenticação própria nem importação financeira implementados.

## Stack

- Python 3.13
- Django 5.2 LTS
- Django Templates + HTMX
- PostgreSQL 17 no ambiente local
- Supabase PostgreSQL para produção (a configurar)
- Docker Compose
- pytest + pytest-django
- Ruff
- GitHub Actions

## 1. Executar localmente

Requisitos: Git, Docker Engine e Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

Abra `http://localhost:8000`.

Em outro terminal:

```bash
docker compose exec web pytest
docker compose exec web ruff check .
docker compose exec web python manage.py check
```

Criar usuário administrador local:

```bash
docker compose exec web python manage.py createsuperuser
```

Parar os serviços:

```bash
docker compose down
```

Os dados do banco local ficam no volume Docker `junance_postgres_data`. **Não use `docker compose down -v` a menos que queira apagar o banco local.**

## 2. Subir para o GitHub

Crie um repositório vazio chamado `junance` na sua conta GitHub. Não marque a opção de adicionar README, `.gitignore` ou licença, pois estes arquivos já existem aqui.

No diretório deste projeto:

```bash
git init
git add .
git commit -m "chore: initialize Junance project"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/junance.git
git push -u origin main
```

Substitua `SEU_USUARIO` pelo seu usuário GitHub. O comando `git remote add` deve ser executado apenas uma vez. Se já houver um remote configurado, confira com `git remote -v` antes de alterá-lo.

## 3. Tentar obter junance.vercel.app

1. Entre na sua conta da Vercel.
2. Escolha **Add New → Project**.
3. Importe o repositório GitHub `junance`.
4. Mantenha a detecção de Django/Python da Vercel; não configure um build de frontend Node.
5. Antes de publicar, configure as variáveis de ambiente conforme a seção abaixo.
6. Faça o primeiro deploy e confira o domínio atribuído em **Settings → Domains**.

A Vercel não permite reservar antecipadamente nomes `*.vercel.app`; eles dependem da disponibilidade. Se `junance.vercel.app` não estiver disponível, escolha um nome alternativo, como `junance-financas.vercel.app`.

## 4. Variáveis de ambiente

Para desenvolvimento local, use `.env.example` como referência e mantenha `.env` fora do Git.

Para a Vercel, configure no painel do projeto:
- `DJANGO_SECRET_KEY`: uma chave secreta forte, exclusiva para produção.
- `DJANGO_DEBUG`: `0`.
- `DJANGO_ALLOWED_HOSTS`: o domínio de produção atribuído à aplicação.
- `DATABASE_URL`: URL de conexão PostgreSQL do Supabase, preferencialmente o endpoint indicado para o tipo de conexão escolhido.
- `DB_SSL_REQUIRE`: `1` se a conexão do Supabase exigir SSL.

Nunca faça commit de `.env`, senha do banco, token ou chave privada. Não envie segredos no chat.

## 5. Banco remoto e migrações

O Compose usa um PostgreSQL local, isolado do banco remoto. O banco do Supabase ainda não está conectado nem foi criado por este pacote.

Antes de apontar para produção:
1. Crie o projeto Supabase e configure a URL de conexão.
2. Gere uma `DJANGO_SECRET_KEY` exclusiva.
3. Configure hosts e SSL.
4. Defina uma estratégia explícita para executar migrações de produção.
5. Teste a implantação com dados de teste, nunca importando o histórico financeiro diretamente.

Não executamos migrações automaticamente durante o build/deploy: isso evita alterar o banco de produção de forma inadvertida. O processo será definido antes de criarmos os modelos de domínio.

## 6. Próximas etapas

1. Fundação e execução local.
2. Famílias, membros e isolamento de dados com testes.
3. Contas, categorias, receitas, despesas e transferências.
4. Cartões, faturas e parcelamentos sem dupla contabilização.
5. Painel mensal e planejamento.
6. Auditoria/importação das planilhas históricas.
7. Investimentos e rentabilidade.

A modelagem financeira e a importação só avançarão após validar as regras de negócio e as exceções das planilhas.

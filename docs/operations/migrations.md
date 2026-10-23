# Migrations

Migrations devem ser criadas no worktree da alteração, revisadas junto dos
modelos e aplicadas localmente com:

```bash
make db-up
make migrate
```

Falhas de migration devem ser investigadas. Não remova o volume ou o banco
para fazer uma migration passar. Produção terá um procedimento explícito de
aplicação; o build e o deploy não executam migrations automaticamente.

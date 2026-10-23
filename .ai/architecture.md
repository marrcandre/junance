# Arquitetura do Junance

## Direção

O Junance será um monólito modular Django. A aplicação começará simples para
reduzir custo operacional e poderá separar módulos internamente conforme o
domínio crescer, sem introduzir microsserviços prematuramente.

```text
Django Templates + HTMX
          ↓
Views, formulários e serviços Django
          ↓
Domínio financeiro e autorização por família
          ↓
PostgreSQL
```

## Componentes

- `config/`: configuração Django, URLs, ASGI e WSGI.
- `core/`: núcleo inicial da aplicação.
- `templates/`: interface server-rendered.
- `core/static/`: CSS e arquivos estáticos.
- `compose.yaml`: PostgreSQL local, sem serviço Django.
- `Makefile`: comandos oficiais de desenvolvimento.
- `.github/workflows/`: automação de CI.

## Módulos de domínio previstos

1. Identidade, famílias e permissões.
2. Contas e saldos.
3. Categorias.
4. Movimentações.
5. Cartões, faturas e parcelas.
6. Importações e auditoria.
7. Planejamento e relatórios.
8. Investimentos.

Esses módulos não precisam ser implementados todos de uma vez. Cada etapa
deve produzir comportamento pequeno, testável e útil.

## Princípios

- O banco é PostgreSQL.
- O limite de autorização é a família.
- Regras financeiras importantes vivem em serviços/domínio, não apenas em
  templates ou views.
- Valores monetários usam `Decimal`/`NUMERIC`.
- Eventos financeiros devem ter efeitos explícitos e não duplicados.
- Importações são processos revisáveis, idempotentes e auditáveis.
- A interface deve permanecer simples e acessível antes de ganhar complexidade.

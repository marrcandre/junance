# Implementação incremental por domínios verticais

## Intenção

Construir o Junance em fatias verticais pequenas, cada uma entregando um fluxo
financeiro utilizável, testável e protegido por autorização de família. O
objetivo é validar as regras do domínio antes de ampliar a interface ou criar
abstrações genéricas.

## Contexto atual

O projeto possui a fundação técnica Django, Templates, HTMX, PostgreSQL, `uv`,
Makefile, CI, pytest e Ruff. A aplicação ainda não possui autenticação própria,
famílias, dados financeiros ou importações. As decisões permanentes estão em
`.ai/`, especialmente a família como limite de isolamento, a separação dos
eventos financeiros e o fluxo de importação revisável.

## Objetivos

- Implementar primeiro identidade, famílias e permissões.
- Garantir isolamento entre famílias em todas as leituras e escritas.
- Entregar contas, categorias e movimentações antes de cartões e importações.
- Manter regras financeiras importantes em serviços/domínio transacionais.
- Usar `Decimal` no Python e `NUMERIC` no PostgreSQL.
- Preservar rastreabilidade de correções, exclusões e importações.
- Fazer cada domínio produzir uma entrega executável e verificável.

## Fora do escopo inicial

- SPA, API pública, Django REST Framework, Redis ou Celery.
- Microsserviços ou separação operacional do monólito.
- Importação de dados reais sem anonimização.
- PDF como primeiro formato de importação.
- Deploy automático com migrations em produção.
- Dashboard complexo antes de haver dados confiáveis.

## Critérios de sucesso

1. Um usuário pode criar ou acessar uma família e operar somente dentro dela.
2. Duas famílias não conseguem ler, alterar ou inferir dados uma da outra.
3. Receitas, despesas e transferências produzem efeitos financeiros distintos.
4. Compras no cartão, parcelas, faturas e pagamentos não geram dupla
   contabilização.
5. Uma importação passa por prévia, validação, confirmação, idempotência e
   auditoria antes de alterar o domínio financeiro.
6. Cada etapa possui testes de comportamento, autorização e regressão.
7. Os comandos oficiais (`make check-django`, `make test`, `make quality` e
   `make deploy-check`) permanecem executáveis ou têm suas limitações
   documentadas.

## Abordagens consideradas

### 1. Domínios verticais — escolhida

Cada etapa atravessa modelo, serviço, autorização, view, template e testes para
entregar um fluxo completo. Essa abordagem reduz o tempo até o primeiro valor,
expõe cedo as regras difíceis e evita desenhar um modelo financeiro genérico
antes de conhecer seus casos reais.

### 2. Camadas técnicas

Construir todos os modelos, depois serviços, views e templates. Essa opção pode
facilitar uma padronização inicial, mas posterga a validação e favorece
abstrações sem comportamento comprovado.

### 3. Fluxos de usuário sem ordem de domínio

Priorizar telas isoladas como cadastro, lançamento e consulta. Essa opção
valida a experiência visual rapidamente, mas pode deixar permissões, auditoria
e efeitos financeiros inconsistentes entre telas.

## Arquitetura proposta

Manter um monólito modular Django, organizado por domínio e não por uma API
separada. Cada módulo deve concentrar seus modelos, serviços, formulários,
URLs, views e testes, seguindo a estrutura que o projeto consolidar na
primeira etapa de domínio.

```text
Django Templates + HTMX
          ↓
Views, formulários e respostas parciais
          ↓
Serviços transacionais por domínio
          ↓
Modelos com vínculo obrigatório à família
          ↓
PostgreSQL
```

As views não devem decidir regras financeiras críticas. Elas validam entrada,
resolvem o contexto autorizado e delegam operações aos serviços. Consultas
devem receber ou derivar explicitamente a família autorizada; não haverá
consulta financeira global por conveniência.

## Sequência de entregas

### 1. Fechamento da fundação

Confirmar configuração, convenções de módulos, estratégia de migrations,
tratamento de erros, mensagens de interface e gates de CI. A entrega é
documental e operacional; não deve antecipar o domínio financeiro.

### 2. Identidade, famílias e papéis

Usar o sistema de usuários do Django como identidade inicial. Criar família,
membro e papel explícito, além do mecanismo de resolução da família ativa.
Definir capacidades mínimas de proprietário, administrador e membro antes de
criar dados financeiros. Testar acesso permitido, acesso negado e isolamento
entre famílias.

### 3. Contas, categorias e movimentações

Criar contas e categorias vinculadas à família. Modelar receitas, despesas e
transferências como eventos distintos, com valores monetários em `Decimal`,
datas semanticamente separadas e operações transacionais. Entregar cadastro,
listagem, filtros por período e lançamento básico.

### 4. Correções e rastreabilidade do núcleo financeiro

Definir estados de edição, cancelamento ou exclusão lógica conforme o caso.
Registrar quem alterou o quê e quando, sem apagar histórico para mascarar
falhas. Fechar o primeiro fluxo de consulta mensal com saldos e totais que não
incluam transferências como receita ou despesa.

### 5. Cartões, compras, parcelas e faturas

Criar cartão, ciclo de fatura, compra e parcela com vínculos explícitos.
Registrar compra no cartão como despesa e obrigação. Registrar pagamento de
fatura como liquidação da obrigação, sem segunda despesa. Testar compras à
vista, parceladas, fechamento, vencimento e pagamento parcial quando aplicável.

### 6. Conciliação

Adicionar estados de conciliação e vínculos com registros externos sem
misturar ainda todos os formatos de importação. A conciliação deve ser
idempotente, auditável e compatível com correções manuais autorizadas.

### 7. Importações revisáveis

Implementar um pipeline com recebimento, identificação, normalização,
validação, prévia, confirmação, persistência idempotente e auditoria. Começar
por um formato com dados de teste anonimizados, mantendo OFX, CSV e XLSX como
adaptadores distintos. PDF será posterior, com revisão reforçada.

### 8. Planejamento e relatórios

Adicionar orçamento e visão mensal somente sobre eventos já classificados e
confiáveis. Relatórios devem distinguir competência, transação e pagamento e
excluir transferências, pagamentos de fatura e efeitos patrimoniais indevidos.

### 9. Investimentos

Modelar posições, aportes e resgates como patrimônio. Rentabilidade deve ser
calculada separadamente de receitas e despesas e permanecer vinculada à
família.

## Regras transversais de cada etapa

- Escrever testes de comportamento antes da implementação correspondente.
- Incluir testes de autorização e isolamento quando houver dado de família.
- Usar `transaction.atomic()` para operações com efeitos relacionados.
- Não usar `float` para valores monetários.
- Não introduzir dependência ou serviço fora da arquitetura sem decisão
  registrada em `.ai/`.
- Manter telas acessíveis sem depender de JavaScript complexo.
- Fazer commits pequenos, coerentes e verificáveis.
- Rodar os checks oficiais antes de declarar cada etapa concluída.

## Riscos e mitigação

- **Modelo genérico demais:** começar por eventos explícitos e adiar
  abstrações até haver dois ou mais casos comprovados.
- **Vazamento entre famílias:** centralizar resolução de contexto e exigir
  testes com duas famílias em cada módulo financeiro.
- **Dupla contabilização:** representar obrigação, liquidação e transferência
  com tipos e vínculos diferentes; validar totais com testes de domínio.
- **Importação destrutiva:** separar prévia e confirmação, usar idempotência e
  preservar origem e auditoria.
- **Histórico não rastreável:** preferir cancelamento ou correção registrada a
  exclusão física de eventos já usados em cálculos.
- **Escopo excessivo:** aceitar uma etapa somente quando seu fluxo mínimo for
  útil, testado e documentado.

## Decisões ainda a fechar durante a primeira etapa

- nomes finais dos módulos Django e localização dos serviços;
- matriz detalhada de permissões por papel;
- política de família ativa para usuários pertencentes a várias famílias;
- política de exclusão e retenção de auditoria;
- formato inicial da chave de idempotência de importações;
- regras exatas de arredondamento e moeda suportada.

Essas decisões devem ser registradas em ADRs antes de condicionarem os
modelos financeiros ou a persistência de dados.

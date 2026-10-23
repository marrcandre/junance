# Dados de teste e deploy

Fixtures e arquivos de importação devem ser pequenos, sintéticos ou
anonimizados. O CI usa PostgreSQL de teste em `localhost` e executa Django
check, pytest e Ruff.

Antes de publicar:

1. configurar uma chave secreta exclusiva e `DJANGO_DEBUG=0`;
2. configurar hosts e SSL;
3. apontar `DATABASE_URL` para o banco correto;
4. revisar e aplicar migrations com procedimento aprovado;
5. validar restauração de backup e smoke test com dados de teste;
6. confirmar que nenhuma importação real ou credencial está no repositório.

# Backup e restauração

O banco local usa o volume Docker `junance_postgres_data`. `docker compose
down -v` é destrutivo e só pode ser usado quando o volume local puder ser
descartado.

Antes da primeira implantação, definir backup automatizado do PostgreSQL,
retenção, criptografia, teste periódico de restauração e responsável pela
execução. Nunca usar produção para testes ou importar histórico financeiro sem
anonimização e conferência.

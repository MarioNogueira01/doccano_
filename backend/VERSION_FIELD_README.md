# 📋 Campo Version - Documentação

## 🎯 Objetivo

O campo `version` foi adicionado à tabela `project_version` para rastrear automaticamente o número sequencial de cada versão de um projeto. Cada vez que um projeto é reaberto, este valor é incrementado automaticamente.

## 🏗️ Estrutura da Tabela

### Campos Atualizados
- **`id`**: Chave primária autogerada
- **`project`**: Chave estrangeira para `Project` (relacionamento 1:N)
- **`start_date`**: Data/hora de início da versão (auto_now_add=True)
- **`end_date`**: Data/hora de fim da versão (null=True, blank=True)
- **`status`**: String com valores "open" ou "closed"
- **`version`**: **NOVO** - Número inteiro sequencial da versão (default=1)

### Relacionamentos
- **Project**: Um projeto pode ter múltiplas versões
- **Related Name**: `project.versions.all()` para acessar versões de um projeto

## 🚀 Como Usar

### 1. Aplicar as Migrations

```bash
cd backend
python manage.py migrate
```

### 2. Popular Dados Existentes (se necessário)

```bash
# Populate version numbers for existing records
python manage.py populate_version_numbers

# Populate all projects with versions (if not done before)
python manage.py populate_versions

# Dry run (ver o que seria criado/atualizado)
python manage.py populate_version_numbers --dry-run
```

### 3. Testar o Campo Version

```bash
python test_version_field.py
```

## 📊 Comportamento Automático

### Criação de Novas Versões
Quando um projeto é reaberto, o sistema automaticamente:

1. **Calcula** o número da nova versão baseado no número de versões existentes para o projeto
2. **Incrementa** o valor em 1
3. **Cria** uma nova entrada na tabela `project_version` com o número calculado

### Exemplo de Sequência
```
Projeto ID 1:
- Versão 1: version=1, status=closed
- Versão 2: version=2, status=closed  
- Versão 3: version=3, status=open (atual)

Projeto ID 2:
- Versão 1: version=1, status=open (atual)
```

## 🔧 Consultas Úteis

### Django Shell

```python
from projects.models import Project, Version

# Listar todas as versões de um projeto ordenadas por número
project = Project.objects.get(id=1)
versions = project.versions.all().order_by('version')

# Versão atual (mais recente)
current_version = project.versions.filter(status='open').first()

# Versões fechadas
closed_versions = project.versions.filter(status='closed').order_by('version')

# Verificar se números de versão estão sequenciais
versions = project.versions.all().order_by('start_date')
version_numbers = [v.version for v in versions]
is_sequential = version_numbers == list(range(1, len(version_numbers) + 1))
```

### SQL (pgAdmin)

```sql
-- Listar versões de um projeto com números sequenciais
SELECT 
    v.id,
    v.version,
    v.start_date,
    v.end_date,
    v.status,
    p.name as project_name
FROM projects_version v
JOIN projects_project p ON v.project_id = p.id
WHERE v.project_id = 1
ORDER BY v.version;

-- Verificar se há gaps nos números de versão
SELECT 
    project_id,
    version,
    LAG(version) OVER (PARTITION BY project_id ORDER BY version) as prev_version
FROM projects_version
WHERE project_id = 1
ORDER BY version;
```

## 🛠️ Comandos de Management

### `populate_version_numbers`
Popula o campo `version` para registros existentes.

```bash
# Popular todos os projetos
python manage.py populate_version_numbers

# Popular projeto específico
python manage.py populate_version_numbers --project-id 1

# Dry run
python manage.py populate_version_numbers --dry-run
```

### `populate_versions`
Cria versões iniciais para projetos que não têm versões.

```bash
# Criar versões para todos os projetos
python manage.py populate_versions

# Criar versão para projeto específico
python manage.py populate_versions --project-id 1

# Dry run
python manage.py populate_versions --dry-run
```

## 🔄 Fluxo de Funcionamento

### 1. Projeto Criado
- Cria versão 1 automaticamente via signal
- `version=1`, `status='open'`

### 2. Projeto Fechado
- Fecha versão atual
- `status='closed'`, `end_date=now()`

### 3. Projeto Reaberto
- Incrementa `project_version` no modelo Project
- Calcula novo número de versão: `count(existing_versions) + 1`
- Cria nova versão com `version=new_number`, `status='open'`

## ⚠️ Regras Importantes

1. **Não alterar manualmente** o campo `version` - é calculado automaticamente
2. **Sempre usar** `order_by('start_date')` para garantir sequência correta
3. **Verificar** se números estão sequenciais após operações manuais
4. **Backup** antes de executar migrations em produção

## 🧪 Testes

Execute o script de teste para verificar se tudo está funcionando:

```bash
python test_version_field.py
```

O teste irá:
- Verificar versões existentes
- Simular reabertura de projeto
- Verificar se números estão sequenciais
- Mostrar resultados detalhados

## 📝 Exemplo de Saída Esperada

```
🧪 Testando o campo version do modelo Version...
📊 Projetos encontrados: 3
🎯 Usando projeto: Meu Projeto (ID: 1)
📋 Versões existentes: 2
📝 Versões existentes:
  - ID: 1, Version: 1, Status: closed, Start: 2024-01-01 10:00:00
  - ID: 2, Version: 2, Status: closed, Start: 2024-01-15 14:30:00

➕ Testando criação de nova versão...
🔓 Reabrindo projeto...
✅ Nova versão criada: Version 3 - Meu Projeto (open) - 2024-01-20 09:15
   - ID: 3
   - Version: 3
   - Status: open
   - Start Date: 2024-01-20 09:15:00

📋 Todas as versões após o teste:
  - ID: 1, Version: 1, Status: closed, Start: 2024-01-01 10:00:00
  - ID: 2, Version: 2, Status: closed, Start: 2024-01-15 14:30:00
  - ID: 3, Version: 3, Status: open, Start: 2024-01-20 09:15:00

✅ Números de versão estão sequenciais e corretos!
�� Teste concluído! 
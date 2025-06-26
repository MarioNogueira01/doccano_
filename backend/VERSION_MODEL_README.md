# 📋 Modelo Version - Documentação

## 🎯 Objetivo

A tabela `Version` foi criada para armazenar dados de cada versão de um projeto separadamente da tabela `Project`, permitindo um controle mais granular do histórico de versões.

## 🏗️ Estrutura da Tabela

### Campos
- **`id`**: Chave primária autogerada
- **`project`**: Chave estrangeira para `Project` (relacionamento 1:N)
- **`start_date`**: Data/hora de início da versão (auto_now_add=True)
- **`end_date`**: Data/hora de fim da versão (null=True, blank=True)
- **`status`**: String com valores "open" ou "closed"

### Relacionamentos
- **Project**: Um projeto pode ter múltiplas versões
- **Related Name**: `project.versions.all()` para acessar versões de um projeto

## 🚀 Como Usar

### 1. Aplicar a Migration

```bash
cd backend
python manage.py migrate
```

### 2. Popular Dados Existentes

```bash
# Populate all projects
python manage.py populate_versions

# Populate specific project
python manage.py populate_versions --project-id 1

# Dry run (ver o que seria criado)
python manage.py populate_versions --dry-run
```

### 3. Testar o Modelo

```bash
python test_version_model.py
```

## 📊 Consultas Úteis

### Django Shell

```python
from projects.models import Project, Version

# Listar todas as versões de um projeto
project = Project.objects.get(id=1)
versions = project.versions.all()

# Versão atual (mais recente)
current_version = project.versions.first()

# Versões fechadas
closed_versions = project.versions.filter(status='closed')

# Versões por período
from django.utils import timezone
from datetime import timedelta
recent_versions = project.versions.filter(
    start_date__gte=timezone.now() - timedelta(days=30)
)
```

### SQL (pgAdmin)

```sql
-- Listar versões de um projeto
SELECT 
    v.id,
    v.start_date,
    v.end_date,
    v.status,
    p.name as project_name
FROM projects_version v
JOIN projects_project p ON v.project_id = p.id
WHERE p.id = 1
ORDER BY v.start_date DESC;

-- Estatísticas de versões por projeto
SELECT 
    p.name,
    COUNT(v.id) as total_versions,
    COUNT(CASE WHEN v.status = 'open' THEN 1 END) as open_versions,
    COUNT(CASE WHEN v.status = 'closed' THEN 1 END) as closed_versions
FROM projects_project p
LEFT JOIN projects_version v ON p.id = v.project_id
GROUP BY p.id, p.name
ORDER BY total_versions DESC;
```

## 🔧 API Endpoints

### Listar Versões de um Projeto
```
GET /api/v1/projects/{project_id}/versions/
```

**Resposta:**
```json
{
  "project": {
    "id": 1,
    "name": "Meu Projeto",
    "current_version": 2,
    "current_status": "open"
  },
  "versions": [
    {
      "id": 1,
      "project": 1,
      "project_name": "Meu Projeto",
      "start_date": "2024-01-01T10:00:00Z",
      "end_date": "2024-01-15T15:30:00Z",
      "status": "closed",
      "duration_display": "14d 5h 30m"
    }
  ]
}
```

## 🎛️ Admin Django

Acesse o admin Django em `/admin/` para gerenciar versões:

- **Lista**: Mostra ID, Projeto, Data Início, Data Fim, Status, Duração
- **Filtros**: Por status, data de início, projeto
- **Busca**: Por nome do projeto
- **Ordenação**: Por data de início (mais recente primeiro)

## 🔄 Integração com Sistema Existente

### Compatibilidade
- ✅ Não altera a estrutura atual da tabela `Project`
- ✅ Mantém compatibilidade com anotações existentes
- ✅ Não impacta exportações e datasets
- ✅ Compatível com PostgreSQL

### Funcionalidades Adicionais
- **Duração**: Calcula automaticamente a duração de cada versão
- **Fechamento**: Método `close_version()` para fechar versões
- **Relacionamento**: Acesso fácil via `project.versions.all()`

## 🧪 Testes

### Executar Teste Automático
```bash
python test_version_model.py
```

### Teste Manual no Django Shell
```python
python manage.py shell

from projects.models import Project, Version

# Criar versão
project = Project.objects.first()
version = Version.objects.create(
    project=project,
    status='open'
)

# Testar métodos
print(version.duration)
version.close_version()
print(version.status)  # 'closed'
```

## 📈 Próximos Passos

1. **Integração Frontend**: Criar interface para visualizar versões
2. **Automação**: Integrar criação automática de versões ao fechar/reabrir projetos
3. **Relatórios**: Adicionar relatórios por versão
4. **Backup**: Implementar backup automático por versão

## 🐛 Troubleshooting

### Erro: "Table doesn't exist"
```bash
python manage.py migrate projects
```

### Erro: "No module named 'projects'"
```bash
# Verificar se está no diretório correto
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Erro: "Permission denied"
```bash
# Verificar permissões do banco
python manage.py check
```

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs do Django
2. Executar `python manage.py check`
3. Testar com `python test_version_model.py`
4. Consultar documentação do Django 
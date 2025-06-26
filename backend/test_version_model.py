#!/usr/bin/env python
"""
Script de teste para verificar o modelo Version.
Execute com: python test_version_model.py
"""

import os
import sys
import django
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from projects.models import Project, Version


def test_version_model():
    """Testa o modelo Version."""
    print("🧪 Testando o modelo Version...")
    
    # 1. Verificar se existem projetos
    projects = Project.objects.all()
    print(f"📊 Projetos encontrados: {projects.count()}")
    
    if not projects.exists():
        print("❌ Nenhum projeto encontrado. Crie um projeto primeiro.")
        return
    
    # 2. Pegar o primeiro projeto para teste
    project = projects.first()
    print(f"🎯 Usando projeto: {project.name} (ID: {project.id})")
    
    # 3. Verificar versões existentes
    existing_versions = Version.objects.filter(project=project)
    print(f"📋 Versões existentes: {existing_versions.count()}")
    
    # 4. Criar uma nova versão se não existir
    if not existing_versions.exists():
        print("➕ Criando primeira versão...")
        version = Version.objects.create(
            project=project,
            start_date=project.created_at,
            status=project.status
        )
        print(f"✅ Versão criada: {version}")
    else:
        version = existing_versions.first()
        print(f"📝 Versão existente: {version}")
    
    # 5. Testar métodos do modelo
    print(f"⏱️  Duração da versão: {version.duration}")
    print(f"📅 Início: {version.start_date}")
    print(f"📅 Fim: {version.end_date or 'Em andamento'}")
    print(f"🔒 Status: {version.status}")
    
    # 6. Testar fechamento de versão
    if version.status == 'open':
        print("🔒 Testando fechamento de versão...")
        version.close_version()
        print(f"✅ Versão fechada: {version}")
    
    # 7. Listar todas as versões do projeto
    all_versions = Version.objects.filter(project=project).order_by('-start_date')
    print(f"\n📋 Todas as versões do projeto '{project.name}':")
    for i, v in enumerate(all_versions, 1):
        print(f"  {i}. {v}")
    
    print("\n✅ Teste concluído com sucesso!")


def test_version_relationships():
    """Testa os relacionamentos do modelo Version."""
    print("\n🔗 Testando relacionamentos...")
    
    # Verificar se o relacionamento está funcionando
    project = Project.objects.first()
    if project:
        versions = project.versions.all()
        print(f"📊 Projeto '{project.name}' tem {versions.count()} versões")
        
        for version in versions:
            print(f"  - Versão {version.id}: {version.start_date} -> {version.end_date or 'Agora'}")


if __name__ == "__main__":
    try:
        test_version_model()
        test_version_relationships()
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc() 
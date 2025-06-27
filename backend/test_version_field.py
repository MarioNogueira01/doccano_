#!/usr/bin/env python
"""
Script de teste para verificar o campo version do modelo Version.
Execute com: python test_version_field.py
"""

import os
import sys
import django
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from projects.models import Project, Version


def test_version_field():
    """Testa o campo version do modelo Version."""
    print("🧪 Testando o campo version do modelo Version...")
    
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
    existing_versions = Version.objects.filter(project=project).order_by('start_date')
    print(f"📋 Versões existentes: {existing_versions.count()}")
    
    if existing_versions.exists():
        print("📝 Versões existentes:")
        for version in existing_versions:
            print(f"  - ID: {version.id}, Version: {version.version}, Status: {version.status}, Start: {version.start_date}")
    
    # 4. Testar criação de nova versão
    print("\n➕ Testando criação de nova versão...")
    
    # Simular reabertura do projeto
    if project.status == 'closed':
        print("🔓 Reabrindo projeto...")
        project.status = 'open'
        project.project_version += 1
        project.save()
        
        # Calcular número da nova versão
        existing_versions_count = Version.objects.filter(project=project).count()
        new_version_number = existing_versions_count + 1
        
        # Criar nova versão
        new_version = Version.objects.create(
            project=project,
            status='open',
            version=new_version_number
        )
        print(f"✅ Nova versão criada: {new_version}")
        print(f"   - ID: {new_version.id}")
        print(f"   - Version: {new_version.version}")
        print(f"   - Status: {new_version.status}")
        print(f"   - Start Date: {new_version.start_date}")
    else:
        print("ℹ️  Projeto já está aberto. Fechando para testar reabertura...")
        project.status = 'closed'
        project.save()
        
        # Fechar versão atual
        last_version = Version.objects.filter(project=project, status='open').first()
        if last_version:
            last_version.status = 'closed'
            last_version.end_date = timezone.now()
            last_version.save()
            print(f"🔒 Versão fechada: {last_version}")
        
        # Reabrir projeto
        print("🔓 Reabrindo projeto...")
        project.status = 'open'
        project.project_version += 1
        project.save()
        
        # Calcular número da nova versão
        existing_versions_count = Version.objects.filter(project=project).count()
        new_version_number = existing_versions_count + 1
        
        # Criar nova versão
        new_version = Version.objects.create(
            project=project,
            status='open',
            version=new_version_number
        )
        print(f"✅ Nova versão criada: {new_version}")
        print(f"   - ID: {new_version.id}")
        print(f"   - Version: {new_version.version}")
        print(f"   - Status: {new_version.status}")
        print(f"   - Start Date: {new_version.start_date}")
    
    # 5. Verificar todas as versões após o teste
    print("\n📋 Todas as versões após o teste:")
    all_versions = Version.objects.filter(project=project).order_by('start_date')
    for version in all_versions:
        print(f"  - ID: {version.id}, Version: {version.version}, Status: {version.status}, Start: {version.start_date}")
    
    # 6. Verificar se os números de versão são sequenciais
    version_numbers = [v.version for v in all_versions]
    expected_numbers = list(range(1, len(version_numbers) + 1))
    
    if version_numbers == expected_numbers:
        print("✅ Números de versão estão sequenciais e corretos!")
    else:
        print("❌ Números de versão não estão sequenciais!")
        print(f"   Atual: {version_numbers}")
        print(f"   Esperado: {expected_numbers}")
    
    print("\n🎉 Teste concluído!")


if __name__ == "__main__":
    test_version_field() 
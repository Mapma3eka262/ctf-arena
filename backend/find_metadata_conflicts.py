#!/usr/bin/env python3
# backend/find_metadata_conflicts.py

import os
import re
import ast

def find_metadata_conflicts():
    """Найти все модели с полем 'metadata'"""
    models_dir = "app/models"
    
    conflicts = []
    
    for filename in os.listdir(models_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            filepath = os.path.join(models_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Ищем классы, наследующиеся от Base
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Проверяем, есть ли поле metadata
                    for item in node.body:
                        if (isinstance(item, ast.AnnAssign) and 
                            isinstance(item.target, ast.Name) and 
                            item.target.id == 'metadata'):
                            conflicts.append((filename, node.name))
                            break
                            
                    # Также проверяем через регулярные выражения
                    if re.search(rf'class {node.name}\(.*Base.*\):', content):
                        if re.search(rf'^\s*metadata\s*:', content, re.MULTILINE):
                            if (filename, node.name) not in conflicts:
                                conflicts.append((filename, node.name))
    
    return conflicts

if __name__ == "__main__":
    print("🔍 Поиск конфликтующих имен 'metadata' в моделях...")
    conflicts = find_metadata_conflicts()
    
    if conflicts:
        print("❌ Найдены конфликты:")
        for filename, classname in conflicts:
            print(f"   - {filename}: {classname}")
    else:
        print("✅ Конфликтов не найдено")

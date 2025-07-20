# -*- coding: utf-8 -*-
"""
WEBAG - Core Module (sem dependencias Flask)
Modulo principal que funciona independente do Flask
"""

# Re-exportar funcionalidades core
from utils.core_utils import (
    sanitize_user_input,
    allowed_file,
    validate_coordinates,
    sanitize_filename,
    create_safe_path
)

# Funcionalidades core disponíveis
__all__ = [
    'sanitize_user_input',
    'allowed_file', 
    'validate_coordinates',
    'sanitize_filename',
    'create_safe_path'
]

def get_system_status():
    """Retorna status do sistema"""
    import os
    
    status = {
        'database': os.path.exists('instance/webgis.db'),
        'config': os.path.exists('config/config.py'),
        'templates': os.path.exists('templates/index.html'),
        'static': os.path.exists('static/app.js'),
        'core_utils': True  # Se chegou ate aqui, esta funcionando
    }
    
    return status

if __name__ == "__main__":
    print("=== WEBAG Core Module Test ===")
    
    # Testar funcionalidades
    test_input = '<script>alert("test")</script>User'
    clean = sanitize_user_input(test_input)
    print(f"Sanitization: '{clean}'")
    
    print(f"KML file valid: {allowed_file('test.kml')}")
    print(f"EXE file valid: {allowed_file('virus.exe')}")
    
    valid, coords = validate_coordinates(-23.5505, -46.6333)
    print(f"Coordinates valid: {valid} -> {coords}")
    
    status = get_system_status()
    print(f"System status: {status}")
    
    print("✅ Core module functioning!")
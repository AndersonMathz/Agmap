# -*- coding: utf-8 -*-
"""
WEBAG - Utilitarios Core (sem dependencias Flask)
Funcionalidades essenciais que funcionam independente do Flask
"""
import re
import os

def sanitize_user_input(user_input):
    """Sanitizar entrada do usuario"""
    if not user_input:
        return ""
    
    # Remover caracteres perigosos
    sanitized = str(user_input)
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    sanitized = sanitized.strip()
    
    return sanitized[:1000]  # Limitar tamanho

def allowed_file(filename, allowed_extensions=None):
    """Verificar se extensao do arquivo e permitida"""
    if allowed_extensions is None:
        allowed_extensions = {'kml', 'kmz', 'shp', 'geojson'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def validate_coordinates(lat, lon):
    """Validar coordenadas geograficas"""
    try:
        lat = float(lat)
        lon = float(lon)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude deve estar entre -90 e 90"
        
        if not (-180 <= lon <= 180):
            return False, "Longitude deve estar entre -180 e 180"
        
        return True, (lat, lon)
        
    except (ValueError, TypeError):
        return False, "Coordenadas invalidas"

def sanitize_filename(filename):
    """Sanitizar nome de arquivo para evitar path traversal"""
    # Remove caracteres perigosos
    dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    return filename

def create_safe_path(base_path, filename):
    """Criar caminho seguro para arquivos"""
    safe_filename = sanitize_filename(filename)
    safe_path = os.path.join(base_path, safe_filename)
    
    # Verificar se o caminho final esta dentro do diretorio base
    if not os.path.abspath(safe_path).startswith(os.path.abspath(base_path)):
        raise ValueError("Caminho invalido")
    
    return safe_path

# Testes automaticos
if __name__ == "__main__":
    print("=== Teste dos Core Utils ===")
    
    # Teste sanitizacao
    test_input = '<script>alert("test")</script>Usuario'
    result = sanitize_user_input(test_input)
    print(f"Sanitizacao: '{test_input}' -> '{result}'")
    
    # Teste validacao arquivo
    print(f"KML valido: {allowed_file('test.kml')}")
    print(f"EXE invalido: {allowed_file('virus.exe')}")
    
    # Teste coordenadas
    valid, result = validate_coordinates(-23.5505, -46.6333)
    print(f"Coordenadas SP: {valid} -> {result}")
    
    print("✅ Todos os testes passaram!")
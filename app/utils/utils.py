import re
import os
import xml.etree.ElementTree as ET

# Imports opcionais
try:
    from werkzeug.utils import secure_filename
    WERKZEUG_AVAILABLE = True
except ImportError:
    WERKZEUG_AVAILABLE = False

try:
    from flask import current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    # Mock current_app para fallback
    class MockApp:
        config = {'ALLOWED_EXTENSIONS': {'kml', 'kmz'}}
    current_app = MockApp()

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False

def sanitize_filename(filename):
    """Sanitizar nome de arquivo para evitar path traversal"""
    if WERKZEUG_AVAILABLE:
        return secure_filename(filename)
    else:
        # Fallback simples se werkzeug não estiver disponível
        # Remove caracteres perigosos
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        return filename

def allowed_file(filename, allowed_extensions=None):
    """Verificar se extensão do arquivo é permitida"""
    if allowed_extensions is None:
        if FLASK_AVAILABLE and FLASK_AVAILABLE:
            try:
                allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
            except:
                allowed_extensions = {'kml', 'kmz'}
        else:
            allowed_extensions = {'kml', 'kmz'}
    
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def sanitize_html(html_content):
    """Sanitizar conteúdo HTML para evitar XSS"""
    if BLEACH_AVAILABLE:
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
        allowed_attrs = {}
        return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    else:
        # Fallback simples se bleach não estiver disponível
        # Remove tags HTML perigosas
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<link[^>]*>',
            r'<meta[^>]*>'
        ]
        
        sanitized = html_content
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized

def validate_kml_content(kml_content):
    """Validar e sanitizar conteúdo KML"""
    try:
        # Verificar se é XML válido
        root = ET.fromstring(kml_content)
        
        # Verificar se é um documento KML válido
        if root.tag != '{http://www.opengis.net/kml/2.2}kml':
            return False, "Arquivo não é um documento KML válido"
        
        # Verificar tamanho do arquivo
        if len(kml_content) > 10 * 1024 * 1024:  # 10MB
            return False, "Arquivo muito grande"
        
        # Sanitizar conteúdo
        sanitized_content = sanitize_kml_content(kml_content)
        
        return True, sanitized_content
        
    except ET.ParseError:
        return False, "Arquivo XML malformado"
    except Exception as e:
        return False, f"Erro ao processar arquivo: {str(e)}"

def sanitize_kml_content(kml_content):
    """Sanitizar conteúdo KML removendo elementos perigosos"""
    # Remover scripts e elementos perigosos
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',
        r'<iframe[^>]*>.*?</iframe>',
        r'<object[^>]*>.*?</object>',
        r'<embed[^>]*>.*?</embed>',
        r'javascript:',
        r'on\w+\s*=',
        r'<link[^>]*>',
        r'<meta[^>]*>'
    ]
    
    sanitized = kml_content
    for pattern in dangerous_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    
    return sanitized

def validate_coordinates(lat, lon):
    """Validar coordenadas geográficas"""
    try:
        lat = float(lat)
        lon = float(lon)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude deve estar entre -90 e 90"
        
        if not (-180 <= lon <= 180):
            return False, "Longitude deve estar entre -180 e 180"
        
        return True, (lat, lon)
        
    except (ValueError, TypeError):
        return False, "Coordenadas inválidas"

def sanitize_user_input(user_input):
    """Sanitizar entrada do usuário"""
    if not user_input:
        return ""
    
    # Remover caracteres perigosos
    sanitized = str(user_input)
    sanitized = re.sub(r'[<>"\']', '', sanitized)
    sanitized = sanitized.strip()
    
    return sanitized[:1000]  # Limitar tamanho

def create_safe_path(base_path, filename):
    """Criar caminho seguro para arquivos"""
    safe_filename = sanitize_filename(filename)
    safe_path = os.path.join(base_path, safe_filename)
    
    # Verificar se o caminho final está dentro do diretório base
    if not os.path.abspath(safe_path).startswith(os.path.abspath(base_path)):
        raise ValueError("Caminho inválido")
    
    return safe_path

def log_security_event(event_type, details, user=None):
    """Registrar eventos de segurança"""
    import logging
    from datetime import datetime
    
    logger = logging.getLogger('security')
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'details': details,
        'user': user.username if user else 'anonymous'
    }
    
    logger.warning(f"Security Event: {log_entry}")
    
    # Em produção, você pode querer enviar para um sistema de monitoramento
    # como Sentry, Loggly, ou um SIEM 
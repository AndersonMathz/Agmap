# Configuração do Gunicorn para produção

# Número de workers
workers = 4

# Tipo de worker
worker_class = 'sync'

# Timeout
timeout = 120

# Bind
bind = '0.0.0.0:8000'

# Logs
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# Processo
daemon = False
pidfile = 'gunicorn.pid'

# Segurança
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Headers de segurança
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
} 
#!/bin/bash
# WEBAG - Instalação de Dependências

echo "=== WEBAG Dependencies Installation ==="

# Verificar Python
if command -v python3 &> /dev/null; then
    echo "✅ Python3 encontrado: $(python3 --version)"
else
    echo "❌ Python3 não encontrado"
    exit 1
fi

# Verificar pip
if python3 -m pip --version &> /dev/null; then
    echo "✅ pip encontrado"
elif command -v pip3 &> /dev/null; then
    echo "✅ pip3 encontrado"
    alias pip='pip3'
elif command -v pip &> /dev/null; then
    echo "✅ pip encontrado"
else
    echo "❌ pip não encontrado"
    echo "Instale com: sudo apt install python3-pip"
    exit 1
fi

# Verificar se requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt não encontrado"
    exit 1
fi

echo "📦 Instalando dependências..."

# Tentar instalar com diferentes métodos
if python3 -m pip install -r requirements.txt; then
    echo "✅ Dependências instaladas com python3 -m pip"
elif pip3 install -r requirements.txt; then
    echo "✅ Dependências instaladas com pip3"
elif pip install -r requirements.txt; then
    echo "✅ Dependências instaladas com pip"
else
    echo "❌ Falha na instalação das dependências"
    echo "Tente manualmente:"
    echo "  python3 -m pip install --user -r requirements.txt"
    exit 1
fi

# Verificar instalação
echo "🧪 Verificando instalação..."

python3 -c "
import sys
success = True

try:
    import flask
    print(f'✅ Flask: {flask.__version__}')
except ImportError:
    print('❌ Flask: Não instalado')
    success = False

try:
    import flask_sqlalchemy
    print(f'✅ Flask-SQLAlchemy: {flask_sqlalchemy.__version__}')
except ImportError:
    print('❌ Flask-SQLAlchemy: Não instalado')
    success = False

try:
    import flask_login
    print(f'✅ Flask-Login: {flask_login.__version__}')
except ImportError:
    print('❌ Flask-Login: Não instalado')
    success = False

if success:
    print('🎉 Todas as dependências instaladas com sucesso!')
    sys.exit(0)
else:
    print('⚠️  Algumas dependências falharam')
    sys.exit(1)
"

echo "=== Instalação concluída ==="
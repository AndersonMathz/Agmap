"""
WEBAG - Configuração de Banco de Dados
Suporte para SQLite (desenvolvimento) e PostgreSQL (produção)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurações de banco por ambiente
DATABASE_CONFIGS = {
    'sqlite': {
        'url': 'sqlite:///instance/webgis.db',
        'echo': True,  # Log SQL em desenvolvimento
        'pool_pre_ping': True
    },
    'postgresql': {
        'url': os.environ.get('DATABASE_URL', 
               'postgresql://webgis_user:webgis_pass123@localhost:5432/webgis_db'),
        'echo': False,  # Menos verboso em produção
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True
    }
}

def get_database_config(db_type='sqlite'):
    """Retorna configuração do banco baseada no tipo"""
    return DATABASE_CONFIGS.get(db_type, DATABASE_CONFIGS['sqlite'])

def create_database_engine(db_type='sqlite'):
    """Cria engine do SQLAlchemy"""
    config = get_database_config(db_type)
    return create_engine(config['url'], **{k:v for k,v in config.items() if k != 'url'})

# Para uso em desenvolvimento
def get_development_session():
    """Sessão de desenvolvimento com SQLite"""
    engine = create_database_engine('sqlite')
    Session = sessionmaker(bind=engine)
    return Session()

# Para uso em produção
def get_production_session():
    """Sessão de produção com PostgreSQL"""
    engine = create_database_engine('postgresql')
    Session = sessionmaker(bind=engine)
    return Session()

# Verificar disponibilidade do banco
def check_database_availability():
    """Verifica qual banco está disponível"""
    try:
        # Tentar PostgreSQL primeiro
        engine = create_database_engine('postgresql')
        with engine.connect():
            return 'postgresql'
    except:
        # Fallback para SQLite
        try:
            engine = create_database_engine('sqlite')
            with engine.connect():
                return 'sqlite'
        except Exception as e:
            raise Exception(f"Nenhum banco de dados disponível: {e}")

if __name__ == "__main__":
    # Teste de conectividade
    print("=== Teste de Conectividade de Banco ===")
    try:
        db_type = check_database_availability()
        print(f"✅ Banco disponível: {db_type}")
        
        if db_type == 'postgresql':
            print("🐘 PostgreSQL conectado - Modo produção")
        else:
            print("📁 SQLite conectado - Modo desenvolvimento")
            
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
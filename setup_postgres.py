import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

try:
    import psycopg2
except ImportError:
    install('psycopg2-binary')
    import psycopg2

conn_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'CambiaEstaPasword2026!',
    'host': '10.147.18.204',
    'port': 5432
}

try:
    print("Conectando a PostgreSQL en 10.147.18.204...")
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("Habilitando extensión pgvector...")
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    print("✓ Extensión 'vector' habilitada.")
    
    print("Creando tabla para Memoria de Chat (chat_messages)...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            message JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Crear índice para búsquedas rápidas por sesión
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON chat_messages(session_id);")
    print("✓ Tabla 'chat_messages' lista.")
    
    print("Creando tabla para Base de Conocimientos RAG (document_vectors)...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_vectors (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            content TEXT,
            metadata JSONB,
            embedding VECTOR(768)
        );
    """)
    print("✓ Tabla 'document_vectors' lista.")
    
    cursor.close()
    conn.close()
    print("\n¡Configuración de Base de Datos completada con éxito! 🚀")
except Exception as e:
    print(f"\n❌ Error: {e}")

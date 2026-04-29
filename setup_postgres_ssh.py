import paramiko
import sys

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('10.147.18.204', username='root', password='Twinc3pt.2', timeout=10)
    
    commands = [
        "docker exec -i postgres-n8n psql -U n8n -d n8n -c \"CREATE EXTENSION IF NOT EXISTS vector;\"",
        "docker exec -i postgres-n8n psql -U n8n -d n8n -c \"CREATE TABLE IF NOT EXISTS chat_messages (id SERIAL PRIMARY KEY, session_id VARCHAR(255) NOT NULL, message JSONB NOT NULL, created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);\"",
        "docker exec -i postgres-n8n psql -U n8n -d n8n -c \"CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);\"",
        "docker exec -i postgres-n8n psql -U n8n -d n8n -c \"CREATE TABLE IF NOT EXISTS n8n_documents (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, content TEXT NOT NULL, metadata JSONB, embedding vector(768));\"",
        "docker exec -i postgres-n8n psql -U n8n -d n8n -c \"CREATE INDEX IF NOT EXISTS idx_n8n_documents_embedding ON n8n_documents USING hnsw (embedding vector_cosine_ops);\""
    ]
    
    for cmd in commands:
        print(f"Executing: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print("Output:", stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print("Error:", err)
            
    ssh.close()
    print("\n✅ Base de datos configurada exitosamente con pgvector.")
except Exception as e:
    print(f"Failed to execute via SSH: {e}")
    sys.exit(1)

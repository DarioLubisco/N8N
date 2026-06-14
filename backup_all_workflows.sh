#!/bin/bash
set -e

echo "Starting N8N native backup..."

# Ensure export directory exists in n8n volume
mkdir -p /home/synapse/docker/n8n/data/workflows_backup
chmod 777 /home/synapse/docker/n8n/data/workflows_backup

# Clean previous backup
rm -rf /home/synapse/docker/n8n/data/workflows_backup/*
rm -rf /home/synapse/source/N8N/workflows/*

# Export ALL workflows (active and inactive) from N8N database natively
docker exec -i n8n n8n export:workflow --backup --output=/home/node/.n8n/workflows_backup/

# Copy to the git tracking directory
cp /home/synapse/docker/n8n/data/workflows_backup/*.json /home/synapse/source/N8N/workflows/

# Sanitize OpenRouter API Keys (to bypass GitHub push protection)
sed -i 's/sk-or-v1-[a-zA-Z0-9]*/sk-or-v1-REDACTED/g' /home/synapse/source/N8N/workflows/*.json

# Git operations
cd /home/synapse/source/N8N
git add workflows/
git commit -m "Auto-backup of all N8N workflows ($(date +'%Y-%m-%d %H:%M:%S'))" || true
git push origin main

echo "Backup and sync to GitHub completed successfully!"

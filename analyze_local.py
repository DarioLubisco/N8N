import json
import os
import re

with open('/home/synapse/source/N8N/columns.json', 'r') as f:
    columns_data = json.load(f)

column_names = [c["COLUMN_NAME"] for c in columns_data]

# Initialize matrix
usage_matrix = {col: {"SP": False, "Analytics": False, "Scrapper": False} for col in column_names}

search_dirs = [
    '/home/synapse/source/repos/Clasificacion Medicamentos',
    '/home/synapse/source/N8N',
    '/home/synapse/source/Pedidos/analytics_engine'
]

file_paths = []
for d in search_dirs:
    for root, _, files in os.walk(d):
        for file in files:
            if file.endswith(('.sql', '.py', '.js', '.json')):
                file_paths.append(os.path.join(root, file))

for path in file_paths:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(path, 'r', encoding='utf-16') as f:
                content = f.read()
        except:
            continue
            
    if 'por_aprobacion_equivalencias' in content:
        # Determine category based on path and name
        lower_path = path.lower()
        
        is_scrapper = 'scraper' in lower_path or 'scrapper' in lower_path or 'investigador' in lower_path or 'orquestador' in lower_path
        is_analytics = 'analytics' in lower_path or 'fuzzy' in lower_path or 'score' in lower_path or 'limpieza' in lower_path
        is_sp = path.endswith('.sql') and not is_scrapper and not is_analytics
        
        if 'chunk_' in lower_path:
            is_sp = True
            
        # Extract mentioned columns
        for col in column_names:
            # simple regex to find exact word match for the column
            if re.search(rf'\b{col}\b', content, re.IGNORECASE):
                if is_scrapper: usage_matrix[col]["Scrapper"] = True
                if is_analytics: usage_matrix[col]["Analytics"] = True
                if is_sp: usage_matrix[col]["SP"] = True

with open('/home/synapse/source/N8N/usage_matrix.json', 'w') as f:
    json.dump(usage_matrix, f, indent=2)

print("Usage matrix generated successfully.")

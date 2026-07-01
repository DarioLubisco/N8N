import json
import os

with open('/home/synapse/source/N8N/columns.json', 'r') as f:
    columns = json.load(f)

fields_js = []
for c in columns:
    col_name = c["COLUMN_NAME"]
    col_type = c["DATA_TYPE"].upper()
    if c.get("CHARACTER_MAXIMUM_LENGTH"):
        col_type += f"({c['CHARACTER_MAXIMUM_LENGTH']})"
    
    # Lógica de inferencia heurística
    is_sp = "false"
    is_analytics = "false"
    is_scrapper = "false"

    # Scrapper / IA Update: campos Descriptivos, o imagenes, o origen_dato
    if col_name.endswith('_Des') or col_name in ['url_imagen', 'origen_dato', 'codbarras', 'es_medicamento', 'requiere_recipe', 'generico', 'blister', 'patrocinador']:
        is_scrapper = "true"
        
    # Analytics / Score: todo lo que termina en _Score, Score_Final
    if col_name.endswith('_Score') or col_name == 'Score_Final':
        is_analytics = "true"
        is_scrapper = "true" # Scrapper usually generates scores too or Analytics

    # Stored Procedures: status, auditoria, usuarios, timestamps
    if col_name in ['status', 'status2', 'usuario', 'usuario_root', 'LastUpdated', 'timestamp1', 'timestamp2'] or "PA_Alter" in col_name:
        is_sp = "true"

    # Core
    if col_name in ['codigo', 'descrip1art', 'principio_activo', 'concentracion', 'forma_farmaceutica', 'fabricante', 'marca', 'contenido_neto', 'codigo_atc']:
        is_sp = "true" # SPs usually read core data

    fields_js.append(f'{{ name: "{col_name}", type: "{col_type}", sp: {is_sp}, analytics: {is_analytics}, scrapper: {is_scrapper} }}')

fields_str = ",\n            ".join(fields_js)

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Depuración Avanzada: por_aprobacion_equivalencias</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --text-color: #e2e8f0;
            --card-bg: #1e293b;
            --border-color: #334155;
            --primary-color: #3b82f6;
            --hover-color: #2563eb;
            --accent-color: #10b981;
            --danger-color: #ef4444;
            --danger-hover: #dc2626;
        }}

        body {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 2rem;
            display: flex;
            justify-content: center;
        }}

        .container {{
            max-width: 1200px;
            width: 100%;
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border-color);
        }}

        h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; color: #ffffff; }}
        p.subtitle {{ color: #94a3b8; margin-bottom: 2rem; font-size: 0.95rem; }}

        .table-container {{
            overflow-x: auto;
            max-height: 65vh;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }}

        table {{ width: 100%; border-collapse: collapse; text-align: left; }}
        th, td {{ padding: 0.8rem; border-bottom: 1px solid var(--border-color); vertical-align: middle; }}
        
        th {{
            background-color: #0f172a; font-weight: 600; color: #cbd5e1;
            text-transform: uppercase; font-size: 0.75rem; letter-spacing: 0.05em;
            position: sticky; top: 0; z-index: 10;
        }}

        tr:hover td {{ background-color: #334155; }}

        .type-badge {{
            background-color: #475569; color: #f8fafc; padding: 0.2rem 0.4rem;
            border-radius: 4px; font-size: 0.75rem; font-family: monospace;
        }}

        /* Checkbox styling */
        .chk-wrap {{
            display: flex; justify-content: center; align-items: center;
        }}
        .chk-wrap input[type="checkbox"] {{
            width: 1.2rem; height: 1.2rem; cursor: pointer; accent-color: var(--primary-color);
        }}
        .chk-eliminar input[type="checkbox"] {{
            accent-color: var(--danger-color);
        }}

        .actions {{ margin-top: 2rem; display: flex; justify-content: space-between; align-items: center; }}
        .btn-group {{ display: flex; gap: 1rem; }}

        button {{
            padding: 0.75rem 1.5rem; border: none; border-radius: 6px;
            font-weight: 600; cursor: pointer; transition: all 0.2s ease;
        }}
        .btn-secondary {{ background-color: transparent; color: var(--text-color); border: 1px solid var(--border-color); }}
        .btn-secondary:hover {{ background-color: var(--border-color); }}
        .btn-danger {{ background-color: var(--danger-color); color: white; }}
        .btn-danger:hover {{ background-color: var(--danger-hover); }}
        
        .results {{
            margin-top: 2rem; padding: 1rem; background-color: #0f172a;
            border-radius: 8px; font-family: monospace; display: none; color: var(--danger-color);
        }}
        .indicator-header {{ text-align: center; font-size: 0.7rem; color: #64748b; }}
    </style>
</head>
<body>

    <div class="container">
        <h1>Depuración: Procurement.por_aprobacion_equivalencias</h1>
        <p class="subtitle">Seleccione las columnas a <b>ELIMINAR</b>. Se han precargado los orígenes detectados por heurística (Stored Procedures, Analytics, Scrapper).</p>

        <div class="table-container">
            <table id="fieldsTable">
                <thead>
                    <tr>
                        <th width="10%" style="text-align:center; color: var(--danger-color);">Eliminar<br><input type="checkbox" id="chkAllDelete" onclick="toggleAllDelete(this)"></th>
                        <th width="30%">Nombre del Campo</th>
                        <th width="20%">Tipo de Dato</th>
                        <th width="10%" class="indicator-header" title="Usado en Stored Procedures">⚙️<br>SP</th>
                        <th width="10%" class="indicator-header" title="Utiliza Analytics">📊<br>Analytics</th>
                        <th width="10%" class="indicator-header" title="Actualizado por Scrapper/IA">🕷️<br>Scrapper</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Generado dinámicamente -->
                </tbody>
            </table>
        </div>

        <div class="actions">
            <div style="font-size: 0.9rem; color: #94a3b8;">
                Total de columnas: <span id="totalCols">{len(columns)}</span>
            </div>
            <div class="btn-group">
                <button class="btn-danger" onclick="generateQuery()">Generar Script de Eliminación</button>
            </div>
        </div>
        
        <div class="results" id="outputArea"></div>
    </div>

    <script>
        const fields = [
            {fields_str}
        ];

        const tbody = document.querySelector('#fieldsTable tbody');

        fields.forEach((field, index) => {{
            const tr = document.createElement('tr');
            
            tr.innerHTML = `
                <td class="chk-wrap chk-eliminar">
                    <input type="checkbox" class="delete-chk" value="${{field.name}}">
                </td>
                <td style="font-weight: 500; font-family: monospace; color: #60a5fa;">${{field.name}}</td>
                <td><span class="type-badge">${{field.type}}</span></td>
                <td class="chk-wrap"><input type="checkbox" ${{field.sp ? "checked" : ""}}></td>
                <td class="chk-wrap"><input type="checkbox" ${{field.analytics ? "checked" : ""}}></td>
                <td class="chk-wrap"><input type="checkbox" ${{field.scrapper ? "checked" : ""}}></td>
            `;
            tbody.appendChild(tr);
        }});

        function toggleAllDelete(source) {{
            const checkboxes = document.querySelectorAll('.delete-chk');
            checkboxes.forEach(c => c.checked = source.checked);
        }}

        function generateQuery() {{
            const checkboxes = document.querySelectorAll('.delete-chk:checked');
            const selectedFields = Array.from(checkboxes).map(c => c.value);
            
            const outputArea = document.getElementById('outputArea');
            outputArea.style.display = 'block';
            
            if (selectedFields.length === 0) {{
                outputArea.innerHTML = "No se ha seleccionado ninguna columna para eliminar.";
                outputArea.style.color = "#94a3b8";
                return;
            }}

            const cols = selectedFields.map(f => `DROP COLUMN ${{f}}`).join(', \\n    ');
            const sql = `ALTER TABLE Procurement.por_aprobacion_equivalencias\\n    ${{cols}};`;
            
            outputArea.style.color = "var(--danger-color)";
            outputArea.innerHTML = `<strong>Script para ELIMINAR ${{selectedFields.length}} columnas:</strong><br><br>${{sql.replace(/\\n/g, '<br>').replace(/ /g, '&nbsp;')}}`;
        }}
    </script>
</body>
</html>"""

with open('/home/synapse/.gemini/antigravity/brain/3a7921fc-f63c-41e9-a950-7476b8e6af40/interfaz_depuracion_avanzada.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

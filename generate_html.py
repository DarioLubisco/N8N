import json

with open('/home/synapse/source/N8N/columns.json', 'r') as f:
    columns = json.load(f)

fields_js = []
for c in columns:
    col_name = c["COLUMN_NAME"]
    col_type = c["DATA_TYPE"].upper()
    if c.get("CHARACTER_MAXIMUM_LENGTH"):
        col_type += f"({c['CHARACTER_MAXIMUM_LENGTH']})"
    fields_js.append(f'{{ name: "{col_name}", type: "{col_type}", desc: "Campo de la tabla base" }}')

fields_str = ",\n            ".join(fields_js)

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Depuración de Tabla: por_aprobacion_equivalencias (Completa)</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --text-color: #e2e8f0;
            --card-bg: #1e293b;
            --border-color: #334155;
            --primary-color: #3b82f6;
            --hover-color: #2563eb;
            --accent-color: #10b981;
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
            max-width: 900px;
            width: 100%;
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border-color);
        }}

        h1 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
            color: #ffffff;
        }}

        p.subtitle {{
            color: #94a3b8;
            margin-bottom: 2rem;
            font-size: 0.95rem;
        }}

        .table-container {{
            overflow-x: auto;
            max-height: 60vh;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th, td {{
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            background-color: #0f172a;
            font-weight: 600;
            color: #cbd5e1;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.05em;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        tr:hover td {{
            background-color: #334155;
        }}

        .type-badge {{
            background-color: #475569;
            color: #f8fafc;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-family: monospace;
        }}

        /* Custom Checkbox */
        .checkbox-wrapper input[type="checkbox"] {{
            display: none;
        }}

        .checkbox-wrapper label {{
            display: inline-flex;
            align-items: center;
            cursor: pointer;
        }}

        .checkbox-wrapper label::before {{
            content: "";
            width: 1.25rem;
            height: 1.25rem;
            border: 2px solid var(--border-color);
            border-radius: 4px;
            margin-right: 1rem;
            background-color: var(--bg-color);
            transition: all 0.2s ease;
        }}

        .checkbox-wrapper input[type="checkbox"]:checked + label::before {{
            background-color: var(--primary-color);
            border-color: var(--primary-color);
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 20 20' fill='white'%3E%3Cpath fill-rule='evenodd' d='M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z' clip-rule='evenodd'/%3E%3C/svg%3E");
            background-size: 80%;
            background-position: center;
            background-repeat: no-repeat;
        }}

        .actions {{
            margin-top: 2rem;
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
        }}

        button {{
            padding: 0.75rem 1.5rem;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s ease;
        }}

        .btn-secondary {{
            background-color: transparent;
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }}

        .btn-secondary:hover {{
            background-color: var(--border-color);
        }}

        .btn-primary {{
            background-color: var(--primary-color);
            color: white;
        }}

        .btn-primary:hover {{
            background-color: var(--hover-color);
        }}
        
        .results {{
            margin-top: 2rem;
            padding: 1rem;
            background-color: #0f172a;
            border-radius: 8px;
            font-family: monospace;
            display: none;
            color: var(--accent-color);
        }}
    </style>
</head>
<body>

    <div class="container">
        <h1>Depuración: Procurement.por_aprobacion_equivalencias (Completa)</h1>
        <p class="subtitle">Análisis de los {len(columns)} campos exactos extraídos de la base de datos SQL Server.</p>

        <div class="table-container">
            <table id="fieldsTable">
                <thead>
                    <tr>
                        <th width="10%">Conservar</th>
                        <th width="40%">Nombre del Campo</th>
                        <th width="30%">Tipo de Dato</th>
                        <th width="20%">Categoría</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Generado dinámicamente -->
                </tbody>
            </table>
        </div>

        <div class="actions">
            <button class="btn-secondary" onclick="selectAll()">Marcar/Desmarcar Todos</button>
            <button class="btn-primary" onclick="generateQuery()">Generar Selección</button>
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
            
            let cat = "Base";
            if (field.name.endsWith('_Score')) cat = "Puntuación";
            if (field.name.endsWith('_Des')) cat = "Descriptivo";
            if (['timestamp1', 'timestamp2', 'LastUpdated'].includes(field.name)) cat = "Auditoría";

            tr.innerHTML = `
                <td>
                    <div class="checkbox-wrapper">
                        <input type="checkbox" id="chk_${{index}}" value="${{field.name}}" checked>
                        <label for="chk_${{index}}"></label>
                    </div>
                </td>
                <td style="font-weight: 500; font-family: monospace; color: #60a5fa;">${{field.name}}</td>
                <td><span class="type-badge">${{field.type}}</span></td>
                <td style="color: #94a3b8; font-size: 0.9rem;">${{cat}}</td>
            `;
            tbody.appendChild(tr);
        }});

        function selectAll() {{
            const checkboxes = document.querySelectorAll('input[type="checkbox"]');
            const allChecked = Array.from(checkboxes).every(c => c.checked);
            checkboxes.forEach(c => c.checked = !allChecked);
        }}

        function generateQuery() {{
            const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
            const selectedFields = Array.from(checkboxes).map(c => c.value);
            
            const outputArea = document.getElementById('outputArea');
            outputArea.style.display = 'block';
            
            if (selectedFields.length === 0) {{
                outputArea.innerHTML = "No se ha seleccionado ningún campo.";
                outputArea.style.color = "#ef4444";
                return;
            }}

            const sql = `SELECT \\n    ${{selectedFields.join(', \\n    ')}} \\nFROM Procurement.por_aprobacion_equivalencias;`;
            
            outputArea.style.color = "var(--accent-color)";
            outputArea.innerHTML = `<strong>Campos Seleccionados (${{selectedFields.length}} de ${{fields.length}}):</strong><br><br>${{sql.replace(/\\n/g, '<br>').replace(/ /g, '&nbsp;')}}`;
        }}
    </script>
</body>
</html>"""

with open('/home/synapse/.gemini/antigravity/brain/3a7921fc-f63c-41e9-a950-7476b8e6af40/interfaz_depuracion_completa.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

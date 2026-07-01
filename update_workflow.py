import json

file_path = '/home/synapse/source/N8N/workflows/fDCuAMGVUsXPdmXp.json'

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

new_jscode = """const headers = {
  "Authorization": "Bearer tk_64eae1632788ad2e1a68bc13f5ba2c959943d2f4"
};

try {
  const projects = await this.helpers.httpRequest({
    method: 'GET',
    url: 'http://10.147.18.4:3456/api/v1/projects',
    headers,
    json: true
  });

  // Encontrar todos los proyectos llamados "Inbox"
  const inboxProjects = projects.filter(p => p.title.toLowerCase() === 'inbox');
  const inboxIds = inboxProjects.map(p => p.id);

  if (inboxIds.length === 0) {
    return [];
  }

  let tasks = [];
  for (const inboxId of inboxIds) {
    try {
      const projectTasks = await this.helpers.httpRequest({
        method: 'GET',
        url: `http://10.147.18.4:3456/api/v1/projects/${inboxId}/tasks`,
        headers,
        json: true
      });
      if (projectTasks && Array.isArray(projectTasks)) {
        tasks = tasks.concat(projectTasks);
      }
    } catch (e) {
      console.error(`Error obteniendo tareas del Inbox ${inboxId}:`, e);
    }
  }

  if (!tasks || tasks.length === 0) {
    return [];
  }

  // Limpiar la lista de proyectos para pasar solo ID y Título a Dify
  // Esto evita exceder el límite de 4000 caracteres de Dify
  const cleanProjects = projects.map(p => ({ id: p.id, title: p.title }));

  const results = [];
  for (const task of tasks) {
    // Ignorar las tareas que ya han sido marcadas como no clasificables
    if (task.title.startsWith('*')) {
      continue;
    }

    try {
      const difyResponse = await this.helpers.httpRequest({
        method: 'POST',
        url: 'https://dify.farmaciaamericana.es/v1/workflows/run',
        headers: {
          "Authorization": "Bearer app-rnKhjfFeCmOrbeUYpouf5nzO"
        },
        body: {
          inputs: {
            titulo: task.title,
            descripcion: task.description,
            lista_proyectos: JSON.stringify(cleanProjects)
          },
          response_mode: 'blocking',
          user: 'n8n-system'
        },
        json: true
      });

      const text = difyResponse.data?.outputs?.text || '';
      const parsed = JSON.parse(text.trim());
      const targetProjectId = Number(parsed.project_id);
      const isTargetInbox = inboxIds.includes(targetProjectId);

      // Validamos si la IA lo pudo clasificar correctamente
      if (Number(parsed.confidence) >= 85 && !isTargetInbox && targetProjectId > 0) {
        results.push({
          json: {
            task_id: task.id,
            title: task.title,
            project_id: targetProjectId,
            confidence: Number(parsed.confidence)
          }
        });
      } else {
        // Falló en la clasificación (confianza baja o intentó moverlo a un Inbox)
        // Agregamos el asterisco para que no lo vuelva a intentar
        await this.helpers.httpRequest({
          method: 'POST',
          url: `http://10.147.18.4:3456/api/v1/tasks/${task.id}`,
          headers,
          body: {
            title: `* ${task.title}`
          },
          json: true
        });
      }
    } catch (e) {
      // Falló por error técnico (red, timeout, JSON inválido)
      await this.helpers.httpRequest({
        method: 'POST',
        url: `http://10.147.18.4:3456/api/v1/tasks/${task.id}`,
        headers,
        body: {
          title: `* ${task.title}`
        },
        json: true
      });
    }
  }

  return results;
} catch (error) {
  throw new Error('Error en el flujo de Vikunja/Dify: ' + error.message);
}"""

# Buscar el nodo de Procesar Ruteo con IA
for node in data.get('nodes', []):
    if node.get('name') == 'Procesar Ruteo con IA':
        node['parameters']['jsCode'] = new_jscode

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Workflow actualizado con proyectos limpios y lógica multi-Inbox.")

async function main() {
  const headers = {
    "Authorization": "Bearer tk_64eae1632788ad2e1a68bc13f5ba2c959943d2f4",
    "Content-Type": "application/json"
  };

  try {
    console.log("Obteniendo proyectos...");
    const projectsResp = await fetch('http://10.147.18.4:3456/api/v1/projects', { headers });
    const projects = await projectsResp.json();
    console.log(`Proyectos obtenidos: ${projects.length}`);

    // Limpiar asteriscos de las tareas antes de probar
    console.log("Limpiando asteriscos de las tareas...");
    const { execSync } = require('child_process');
    execSync('docker exec -i vikunja-db psql -U vikunja -d vikunja -c "UPDATE tasks SET title = REGEXP_REPLACE(title, \'^\\\\*\\\\s*\', \'\') WHERE title LIKE \'* %\';"');

    const inboxProjects = projects.filter(p => p.title.toLowerCase() === 'inbox');
    const inboxIds = inboxProjects.map(p => p.id);
    console.log("Inbox IDs:", inboxIds);

    let tasks = [];
    for (const inboxId of inboxIds) {
      console.log(`Obteniendo tareas para el Inbox ${inboxId}...`);
      const tasksResp = await fetch(`http://10.147.18.4:3456/api/v1/projects/${inboxId}/tasks`, { headers });
      const tasksData = await tasksResp.json();
      if (tasksData && Array.isArray(tasksData)) {
        tasks = tasks.concat(tasksData);
      }
    }
    console.log(`Tareas encontradas: ${tasks.length}`);

    for (const task of tasks) {
      console.log(`\nProcesando tarea: "${task.title}" (ID: ${task.id})`);
      try {
        console.log("Llamando a Dify...");
        const difyResponse = await fetch('https://dify.farmaciaamericana.es/v1/workflows/run', {
          method: 'POST',
          headers: {
            "Authorization": "Bearer app-rnKhjfFeCmOrbeUYpouf5nzO",
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            inputs: {
              titulo: task.title,
              descripcion: task.description,
              lista_proyectos: JSON.stringify(projects)
            },
            response_mode: 'blocking',
            user: 'n8n-system'
          })
        });

        const difyData = await difyResponse.json();
        console.log("Dify Response Raw:", JSON.stringify(difyData));
        const text = difyData?.data?.outputs?.text || '';
        console.log("Dify text output:", text);
        const parsed = JSON.parse(text.trim());
        const targetProjectId = Number(parsed.project_id);
        const isTargetInbox = inboxIds.includes(targetProjectId);

        console.log(`Dify parsed: project_id=${targetProjectId}, confidence=${parsed.confidence}, isTargetInbox=${isTargetInbox}`);

        if (Number(parsed.confidence) >= 85 && !isTargetInbox && targetProjectId > 0) {
          console.log(`[EXITO] La tarea se movería al proyecto: ${targetProjectId}`);
        } else {
          console.log("[FALLO] No cumple criterios de clasificación. Se marcaría con asterisco.");
        }
      } catch (e) {
        console.error("[ERROR EN BUCLE]", e.message);
      }
    }
  } catch (err) {
    console.error("[ERROR GENERAL]", err.message);
  }
}

main();

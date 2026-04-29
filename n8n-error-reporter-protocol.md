# n8n Error Reporter Protocol

Esta skill proporciona las pautas de alto nivel para la arquitectura y gestión del reporte de errores en los flujos de trabajo de n8n dentro del ecosistema de Synapse. El objetivo principal es asegurar que los errores críticos lleguen efectivamente a los administradores a través de los canales designados (como Telegram o Email) y, al mismo tiempo, mitigar la fatiga de alertas eliminando los falsos positivos.

## Principios Fundamentales

1. **Centralización del Manejo de Errores**
   - Utilizar un **Flujo Global de Manejo de Errores** (Global Error Workflow) impulsado por el nodo `Error Trigger`.
   - Evitar configurar notificaciones de error individuales en cada flujo. La delegación al flujo global asegura estandarización y mantenibilidad.

2. **Cero Falsos Positivos (Alert Fatigue)**
   - No todos los errores merecen una alerta inmediata. El flujo global debe implementar lógica para filtrar errores no accionables o esperados.
   - **Reintentos Automáticos:** Para operaciones propensas a fallos transitorios (ej. llamadas a APIs externas, timeouts, rate limits), configurar el nodo para reintentar (Retry On Fail) *antes* de que el error sea definitivo y escale al flujo global.
   - **Tolerancia a Fallos:** En pasos no críticos, utilizar la opción "Continue On Fail" para evitar que el flujo falle por completo si ese paso no compromete el resultado final.

3. **Manejo Local vs Global**
   - Si un error requiere lógica de recuperación local (fallback), utilizar el nodo o patrón `Try/Catch` (por ejemplo, sub-flujos o condicionales que validan el output).
   - Si un error requiere intervención humana o detiene el proceso lógico de negocio, debe escalar al `Error Trigger` global.

## Mejores Prácticas para el Flujo de Manejo de Errores Global

Cuando diseñes o mantengas el flujo de Errores Global, asegúrate de implementar lo siguiente:

- **Enriquecimiento del Contexto:**
  La alerta enviada debe incluir toda la información crítica para facilitar el triaje rápido:
  - Nombre del flujo de trabajo (`Workflow Name`).
  - Nombre del nodo que falló (`Node Name`).
  - Mensaje descriptivo del error (`Error Message`).
  - Enlace directo a la ejecución (`Execution URL`), para depuración rápida.
  - Fecha y hora.

- **Filtrado Dinámico:**
  - Implementar un nodo `Switch` o `If` justo después del `Error Trigger` para descartar:
    - Errores generados en entornos de desarrollo/pruebas.
    - Códigos de error específicos que son conocidos y están programados para ser ignorados.

- **Enrutamiento por Canal:**
  - Enviar notificaciones de infraestructura crítica al **Bot de Notificación de Errores** en Telegram (documentado en `synapse_credentials.md`).
  - Para errores de procesos de negocio menos críticos, considerar notificaciones agrupadas o correos electrónicos para no saturar los canales de mensería en tiempo real.

## Instrucciones Operativas

Al desarrollar nuevos flujos o modificar los existentes:
- **Verificar Settings del Workflow:** Asegúrate de que el flujo de trabajo tenga configurado el `Error Workflow` apuntando al flujo central de reporte de errores (si se maneja a nivel de workspace o de configuración del flujo).
- **No duplicar:** Confía en el sistema central de errores. No agregues nodos HTTP o de mensajería en el flujo normal solo para notificar que algo falló, deja que falle elegantemente y que el Global Error Handler se encargue.

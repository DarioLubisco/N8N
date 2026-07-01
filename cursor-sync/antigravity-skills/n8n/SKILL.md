---
name: n8n-error-reporter
description: Protocolo activo y mejores prácticas de alto nivel para el reporte y manejo de errores en n8n, garantizando notificaciones efectivas y previniendo falsos positivos.
---

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

- **Estructura e Identidad de Errores (Entity-Based Logging):**
  Evitar mensajes de error vagos y genéricos (ej. "The service refused the connection"). Todos los errores generados en flujos de monitorización deben atraparse localmente (`Continue On Fail` + `If` + `Stop And Error`) para emitir una **estructura pre-constituida basada en entidades** que aclare identidades de Primer y Segundo grado. La alerta debe contener:
  - **Nivel de Gravedad:** Crítico (1er Grado - ej. BD, DNS) o Advertencia (2do Grado - ej. APIs internas, procesos dependientes).
  - **Entidad Origen:** Máquina e IP que ejecuta el chequeo (ej. `Servidor Debian Webservices (IP: 10.147.18.204)`).
  - **Entidad Destino:** Máquina e IP objetivo (ej. `Servidor Desktop Dario Windows (IP: 10.200.8.114)`).
  - **Servicio Afectado:** Qué protocolo o microservicio específico falló.
  - **Causas Probables:** Diagnóstico inferido para agilizar la resolución.
  - **Log Nativo y Actionable Links:** El error técnico capturado por n8n (`$json.error.message`) y el enlace directo a la ejecución (`Execution URL`).

  *Ejemplo de Estructura de Plantilla (Inyectada vía Stop and Error):*
  ```text
  🚨 CRÍTICO (Primer Grado): Pérdida de Servicio Central
  🖥️ Entidad Origen: Servidor Debian Webservices (IP ZeroTier: 10.147.18.204)
  🎯 Entidad Destino: Servidor Windows SRV-DC-AMC (IP LAN: 10.200.8.5)
  🔌 Servicio Afectado: MSSQL Server (Instancia: Saint)
  
  📝 Diagnóstico: El nodo no pudo validar la consulta de latencia.
  🔍 Causas Probables: El túnel ZeroTier está caído o el servicio se detuvo.
  🛠️ Log Nativo (n8n): {{ $json.error.message }}
  ```

- **Fallback para Errores No Estructurados (Errores Nativos/No Capturados):**
  Para flujos que no inyectan una estructura pre-constituida basada en entidades (por ejemplo, errores de sintaxis, fallos de red inesperados o excepciones de SQL), el nodo de formateo central (`Format Alert Data`) en el flujo global debe implementar una lógica que valide y envuelva el error nativo en una estructura amigable y descriptiva. Esto previene el envío de mensajes mudos o excesivamente técnicos a Telegram sin contexto sobre qué flujo u operación falló.

  *Expresión Estándar para `alert_body` en `Format Alert Data`:*
  ```javascript
  {{ 
    (() => {
      const rawError = $json.execution?.error?.messages?.[0] || $json.trigger?.error?.messages?.[0] || $json.error?.messages?.[0] || $json.execution?.error?.message || $json.trigger?.error?.message || $json.error?.message || "⚠️ ERROR DESCONOCIDO";
      if (rawError.includes("Servicio Afectado") || rawError.includes("Entidad Origen")) {
        return rawError;
      }
      const wfName = $json.workflow?.name || "Desconocido";
      const nodeName = $json.execution?.lastNodeExecuted || "Desconocido";
      const execId = $json.execution?.id || "N/A";
      const errorMsg = $json.execution?.error?.message || $json.execution?.error?.description || $json.error?.message || "Sin mensaje específico";
      return `🚨 <b>FALLO EN FLUJO DE TRABAJO</b>\n\n📋 <b>Flujo:</b> ${wfName}\n⚙️ <b>Nodo:</b> ${nodeName}\n🆔 <b>Ejecución:</b> #${execId}\n\n❌ <b>Error:</b> <code>${errorMsg}</code>`;
    })()
  }}
  ```

- **Filtrado Dinámico:**
  - Implementar un nodo `Switch` o `If` justo después del `Error Trigger` para descartar:
    - Errores generados en entornos de desarrollo/pruebas.
    - Códigos de error específicos que son conocidos y están programados para ser ignorados.

- **Enrutamiento por Canal:**
  - Enviar notificaciones de infraestructura crítica al **Bot de Notificación de Errores** oficial (documentado en `synapse_credentials.md`).
  - **REGLA DE SESIÓN:** Si la alerta incluye botones interactivos (ej. Mute), el bot que envía la notificación **DEBE** ser el mismo que el bot configurado en el `Mute Handler`. De lo contrario, los callbacks no funcionarán.

- **Manejo de Silencio (Mute Logic):**
  - Todas las alertas críticas deben ofrecer opciones de silencio (1h, 4h, 12h) y una opción de "Reactivar/Desilenciar".
  - El estado de silencio debe centralizarse en una `DataTable` de n8n para que sea consultable por cualquier flujo de la organización.
  - Para retrocompatibilidad con scripts locales (PowerShell), el flujo de errores debe actualizar también los archivos de estado locales (`mute.txt`) mediante comandos SSH si aplica.

## ⚖️ Protocolo de Prioridad de Herramientas

**REGLA DE ORO:** El uso del **MCP (`n8n-arquitectura` o `n8n-mcp`)** es la vía MANDATORIA y PRIORITARIA para cualquier interacción con n8n.

1.  **Prioridad 1: MCP (`n8n-arquitectura`)**: Debe usarse para crear, actualizar, buscar y consultar detalles de flujos. Es el método más estable y seguro para mantener la integridad del código del flujo.
2.  **Prioridad 2: MCP (`n8n-mcp`)**: Alternativa secundaria si el anterior presenta problemas de conectividad.
3.  **Prioridad 3: Browser Subagent (ÚLTIMO RECURSO)**: Solo debe usarse para tareas que el MCP no puede realizar técnicamente (como asignar etiquetas/tags o configurar el Error Workflow global en la interfaz visual) O si el usuario lo solicita explícitamente tras fallar los métodos anteriores.

> [!IMPORTANT]
> Nunca uses el navegador para editar la lógica de un flujo si el MCP está disponible. El MCP garantiza que el código generado siga los estándares del SDK y evita errores de manipulación visual.

### ⚠️ Regla Estricta contra Flujos "Fantasma" (Corrupción de UI)

Cuando crees o modifiques flujos de trabajo a través del código JSON/SDK o mediante el MCP, es crítico evitar generar **"Flujos Fantasma"**. Un flujo fantasma es aquel que el backend de n8n guarda y ejecuta sin errores, pero que el frontend (lienzo visual) es incapaz de renderizar, dejando la pantalla en blanco o corrupta.

Esto ocurre por dos razones principales:

1. **Parámetros de Nodo Inventados o Incompletos (Crash de Interfaz):**
   - El frontend de n8n espera estructuras exactas en los parámetros de cada nodo (ej. el nodo FTP requiere `"operation"`, el Schedule requiere `"rule": {"interval": [{"field": "minutes", ...}]}`).
   - Si como Agente "inventas" parámetros, omites propiedades requeridas, o asumes estructuras genéricas (como `"interval": [{}]`), el framework de interfaz gráfica (UI) colapsará al intentar leer propiedades inexistentes y no dibujará ningún nodo.
   - **Acción requerida:** **NUNCA** "adivines" la estructura JSON de los parámetros. Utiliza estrictamente las herramientas del servidor MCP (`search_nodes` y `get_node_types`) para obtener la estructura real y nativa antes de crear un flujo, y pasa el resultado siempre por `validate_workflow`.

2. **Ausencia de Coordenadas Geométricas (`position`):**
   - Si omites el campo `position: [x, y]` o usas un formato inválido, los nodos se apilarán en el origen `[0,0]` o la interfaz se romperá.
   - **Acción requerida:** Debes obligatoriamente asignar o preservar las coordenadas `[x, y]` con suficiente espaciado lógico para que el flujo sea visualizable.


## Instrucciones Operativas

Al desarrollar nuevos flujos o modificar los existentes:
- **Verificar Settings del Workflow:** Asegúrate de que el flujo de trabajo tenga configurado el `Error Workflow` apuntando al flujo central de reporte de errores (si se maneja a nivel de workspace o de configuración del flujo).
- **No duplicar:** Confía en el sistema central de errores. No agregues nodos HTTP o de mensajería en el flujo normal solo para notificar que algo falló, deja que falle elegantemente y que el Global Error Handler se encargue.

## Organización y Buenas Prácticas de Flujos de Trabajo (Pedidos-Synapse)

Dado el rol de n8n como orquestador en la Fase 1 de **Pedidos-Synapse** (particularmente para la ingesta de archivos Excel vía WhatsApp), es fundamental aplicar estrategias robustas para mantener los flujos de trabajo organizados, escalables y fáciles de mantener.

### 1. Organización Estructural y Nomenclatura (Naming Conventions)
Para evitar que el tablero principal se desorganice, utiliza las herramientas nativas y reglas estrictas de nombrado:
- **Tags (Etiquetas):** Utilízalas como método principal para filtrar flujos. Ejemplos de etiquetas útiles: `Producción`, `Pruebas`, `WhatsApp-Ingesta`, `Proveedores-Híbridos`.
- **Nomenclatura de Workflows:** Usa el formato estructurado `[ESTADO] [Dominio] - [Acción]`.
  - Ejemplo: `[PROD] [CRM] - Ingesta de Pedidos WhatsApp` o `[QA] [ERP] - Sync AppSheet`.
- **Accesibilidad MCP:** Todo flujo marcado como `[PROD]` **DEBE** tener habilitada la opción `Available in MCP` en sus Settings para permitir la orquestación programática.
- **Nomenclatura de Nodos:** **NUNCA** dejes el nombre por defecto (ej. `HTTP Request1`). Usa siempre el formato **"Verbo + Sustantivo"** (ej. `Obtener Tasa BCV`, `Guardar en Postgres`) para que la lógica sea legible como una historia.

### 2. Modularidad mediante "Execute Workflow"
Evita los flujos gigantes o monolíticos. Aplica el principio de "divide y vencerás":
- **Flujo Maestro:** Encargado exclusivamente de recibir la entrada (ej. webhook de WhatsApp).
- **Flujos de Procesamiento:** Sub-flujos independientes (ej. convertir Excel a JSON/SQL). Esto permite reutilizar la misma lógica para archivos que provengan de Email, FTP u otros canales.
- **Regla de Refactorización:** Si una secuencia lógica (ej. formatear datos, calcular impuestos, logging) requiere más de 5 nodos, o se utiliza en más de dos flujos, **debe extraerse a un sub-flujo independiente**.

### 3. Documentación y Agrupación Visual
- **Sticky Notes:** Utiliza las notas nativas del lienzo para documentar la función de cada bloque, dependencias de bases de datos, y variables de entorno requeridas.
- **Agrupación de Nodos (Grouping):** Selecciona grupos lógicos de nodos y agrúpalos (letra 'C'). Asigna colores semánticos:
  - 🔵 **Azul:** Ingesta de datos / Triggers.
  - 🟡 **Amarillo:** Transformación y lógica de negocio (Code/IF).
  - 🟢 **Verde:** Acciones exitosas de escritura (SQL, API POST).
  - 🔴 **Rojo:** Manejo local de errores / Dead-Letter Queues.

### 4. Gestión de Entornos y Variables
Protege siempre los parámetros de conexión y credenciales de base de datos o servidores:
- **Credenciales Nativas:** Utiliza estrictamente el gestor de credenciales nativo de n8n para nodos integrados (ej. Postgres, FTP, SSH).
- **Variables Globales SSOT:** Para valores estáticos, IPs, o API Keys de servicios externos usados en scripts, **DEBES** consumir el sub-flujo `[CONFIG] Global Variables`. Utiliza el nodo `Execute Workflow` para obtener estas variables en lugar de quemarlas (hardcode) en los nodos de lógica.
- **Seguridad:** Nunca introduzcas contraseñas en texto plano dentro de un nodo `Code` o en notas visibles.

### 5. Sincronización y Control de Versiones
Para mantener consistencia con scripts externos (como `Clas_Med_Final.py`):
- **Exportación y Versionado (Git):** Configura n8n para sincronizar los flujos (en formato JSON) con un repositorio de control de versiones (GitHub/GitLab) automáticamente o periódicamente. Esto asegura la recuperabilidad de versiones funcionales anteriores en caso de que un cambio rompa la comunicación con la base de datos o lógica externa.

### 6. Patrón de Ejecución Estándar (Python via SSH)
Para ejecutar lógica compleja (ETL, Procesamiento de Datos, SQL Merge) que requiera dependencias de sistema o drivers ODBC, se debe seguir este estándar:
- **Evitar `Execute Command` Directo:** No ejecutar comandos nativos dentro del contenedor de n8n para evitar conflictos de arquitectura o falta de librerías.
- **Nodo SSH:** Utilizar el nodo `n8n-nodes-base.ssh` para conectarse al host **Debian (Webservices)**.
- **Ubicación de Scripts:** Los scripts deben residir en `/opt/scripts/` en el servidor Debian.
- **Intérprete:** Usar `python3`.
- **Desacoplamiento de Infraestructura (Mandatorio):** NUNCA se deben quemar (hardcode) cadenas de conexión de bases de datos (IPs, usuarios, contraseñas) u otros secretos directamente en los scripts Python (`.py`). Se debe utilizar SIEMPRE un archivo `.env` en el directorio de ejecución y cargar las variables utilizando `python-dotenv` u `os.environ`. Esto asegura la portabilidad y previene que los cambios en la infraestructura rompan el código.
- **Ventaja:** Permite que el script corra nativamente en el host con acceso completo a los túneles ZeroTier/Tailscale y drivers de base de datos persistentes.

### 7. Concepto de "Proveedores-Híbridos"
Se clasifican bajo esta etiqueta los flujos que integran sistemas externos tradicionales (Legacy) con nuestra infraestructura moderna:
- **Entrada:** FTP, Archivos TXT/CSV de ancho fijo, Emails.
- **Procesamiento:** Orquestación en n8n + Ejecución de Python nativo vía SSH.
- **Salida:** Inserción atómica en SQL Server (MSSQL) mediante `MERGE` para garantizar idempotencia.

### 8. Tolerancia a Fallos y Degradación Elegante
Más allá de la notificación de errores, previene que fallos transitorios rompan el flujo:
- **Reintentos (Retry):** En nodos que dependan de APIs externas (ej. AppSheet, DolarToday), habilita `Retry On Fail` con pausas exponenciales.
- **Dead-Letter Queues:** Si un nodo de escritura final (ej. `SQL Insert`) falla debido a datos malformados, enruta los datos a una rama de error que los guarde en un archivo temporal (ej. JSON en Debian) para revisión manual, evitando perder el payload original.

### 9. Desarrollo Ágil (Testing & Dry Runs)
- **Pinning Data (Fijar Datos):** Cuando desarrolles un flujo, ejecuta el nodo inicial (ej. llamada a una API o webhook) una vez y activa **"Pin Data"**. Esto permite construir y probar el resto de la lógica sin saturar APIs externas ni consumir cuotas.
- **Dry Runs:** Para flujos críticos, implementa una lógica (ej. una variable `TEST_MODE = true`) que omita el último nodo destructivo (el `SQL Update` o el envío del SMS), permitiendo simular el flujo completo en el entorno de producción sin consecuencias.

### 10. Resiliencia de Agentes IA

Todo nodo de tipo `AI Agent` en producción debe implementar patrones de resiliencia para garantizar la continuidad del servicio. Existen dos tipos de backup independientes:

- **Escalada Cognitiva (Model Selector):** Si el modelo principal no puede resolver la tarea, un segundo modelo más potente toma el control. Implementar con el nodo `Model Selector` (`@n8n/n8n-nodes-langchain.modelSelector`) conectando 2+ modelos como subnodes del agente.
- **Fallback por Infraestructura (onError):** Si el proveedor de IA está caído (timeout, rate limit, error de red), un agente de emergencia independiente atiende la solicitud. Implementar con `onError: 'continueErrorOutput'` en el agente principal y `.onError()` conectando a un segundo `AI Agent` con un modelo alternativo.

**Reglas generales:**
- No conectar un solo modelo directamente al agente sin backup.
- El agente de emergencia debe tener sus propias instancias de Tools (subnodes no se comparten entre agentes).
- El system prompt del agente de emergencia debe ser idéntico al principal, indicando que actúa como respaldo.
- Documentar la arquitectura de modelos específica del proyecto en un archivo dedicado (ej. `Plan_Implementacion_IA.md`), NO en esta skill.


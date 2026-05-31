# Matriz Estratégica de Modelos de IA para Infraestructura Synapse (n8n)

Basado en la arquitectura actual de Synapse (n8n, SQL Server, WhatsApp/Evolution API, Docling), hemos descartado los modelos gratuitos de OpenRouter (por inestabilidad), manteniendo únicamente Gemini en su capa gratuita (cuando aplique) y los modelos de pago más rentables.

## 1. Análisis de Casos de Uso (Workflows de n8n)

### A. Extracción de Facturas PDF (El "Cerebro" Contable)
**Flujo actual:** Docling (Local Docker) -> Extrae Markdown -> Granite (Ollama Remoto) -> PostgreSQL.
**Análisis:** Granite es excelente y no tiene costo por token (ya que corre en tu servidor Ollama remoto). Sin embargo, si el servidor remoto se cae o necesitas un modelo de respaldo (Fallback) en n8n para no detener la contabilidad, necesitas un modelo en OpenRouter que sea **muy estricto siguiendo instrucciones JSON**.
**Modelos ideales:** Gemini 2.5 Flash (por su ventana de contexto gigante para PDFs largos) o GPT-4o-mini.

### B. Importación de Inventario (WhatsApp / Email -> SQL)
**Flujo:** Recibe Excel/Texto -> Extrae 10 columnas clave -> `MERGE` en SQL Server.
**Análisis:** Requiere alta velocidad y capacidad analítica moderada para entender formatos desordenados de proveedores.
**Modelos ideales:** Llama 3.3 70B (extremadamente barato y rápido) o Gemini 2.5 Flash.

### C. CRM y Atención al Cliente (WhatsApp / Pagomóvil)
**Flujo:** Cliente escribe al bot -> IA clasifica intención -> Responde o transfiere a Chatwoot -> Valida pagos.
**Análisis:** Alto volumen de mensajes. Requiere muy baja latencia, tono conversacional natural y costo casi nulo por mensaje.
**Modelos ideales:** Llama 3.3 70B Instruct (el más humano y económico) o GPT-4o-mini.

### D. Agente Autónomo (Hermes) y Tareas de Infraestructura
**Flujo:** Tareas de administración de servidores, scripting, resolución de errores en n8n.
**Análisis:** Requiere el mayor nivel de razonamiento lógico y programación del mundo. El volumen de mensajes es bajo (solo lo usas tú).
**Modelos ideales:** Claude 3.5 Sonnet (El mejor del mercado para código) o Gemini 2.5 Pro.

---

## 2. Tabla de Precios y Conveniencia (Exportable a Excel)

Puedes copiar la siguiente tabla y pegarla directamente en Excel o Google Sheets. Los precios están calculados por **1 Millón de Tokens** (aprox. 750,000 palabras o 1,500 facturas completas).

| Proveedor | Modelo en OpenRouter | Costo Input (Lectura) / 1M Tokens | Costo Output (Escritura) / 1M Tokens | Velocidad | Score LMSYS | Costo/Beneficio | Conveniencia por Caso de Uso |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Google** | `google/gemini-3.1-flash-lite-preview` | **$0.25** | **$1.50** | 🚀 Muy Alta | **1240** | **708** | **PRINCIPAL (FACTURAS):** Extracción JSON de Facturas PDF (Post-Docling). Procesamiento masivo de datos. |
| **Meta** | `meta-llama/llama-3.3-70b-instruct` | **$0.10** | **$0.32** | 🚀 Muy Alta | **1290** | **3071** | **PRINCIPAL (CRM):** Atención al Cliente WhatsApp. ¡El más rentable! |
| **Alibaba** | `qwen/qwen-2.5-72b-instruct` | **$0.36** | **$0.40** | 🚀 Muy Alta | **1280** | **1684** | **PRINCIPAL (ETL):** Conversión de Inventarios (Texto a SQL). Excelente en lógica y JSON estricto. |
| **DeepSeek** | `deepseek/deepseek-r1` | **$0.55** | **$2.19** | Media (Pensa) | **1361** | **496** | **PRINCIPAL (HERMES):** Agente de Sistema. Programación avanzada a precio ridículo. |
| **OpenAI** | `openai/gpt-4o-mini` | **$0.15** | **$0.60** | ⚡ Alta | **1265** | **1686** | **ALTERNO:** Clasificación de correos, ruteo rápido en n8n. |
| **Anthropic** | `anthropic/claude-sonnet-4.6` | **$3.00** | **$15.00** | Normal | **1360** | **75** | **RESERVA DE LUJO:** Si DeepSeek R1 no logra resolver un problema de código, usa Claude. |
| **Anthropic** | `anthropic/claude-opus-4.7` | **$5.00** | **$25.00** | Lenta | **1370** | **45** | **ESPECIAL:** Tareas de razonamiento extremo o resolución de problemas arquitectónicos gigantes. |
| **Google** | `google/gemini-3.1-pro-preview` | **$2.00** | **$12.00** | Media | **1345** | **96** | **ALTERNO:** Análisis profundo de documentos masivos o imágenes. |

---

## 3. Recomendación Arquitectónica para n8n (100% Cloud OpenRouter)

Al eliminar los servidores locales (Ollama/Granite), toda la carga de IA pasa a OpenRouter. Para optimizar tus $7 y mantener la resiliencia en n8n, tu configuración queda así:

1. **Facturas y Contabilidad (Docling):** 
   - Usa **Gemini 3.1 Flash Lite Preview**. Su ventana de contexto gigante leerá el Markdown generado por Docling sin problemas y devolverá el JSON perfecto para SQL. Costo: Centavos por miles de facturas.
2. **Atención al Cliente (WhatsApp CRM):** 
   - Usa **Llama 3.3 70B (`meta-llama/llama-3.3-70b-instruct`)**. Sigue siendo imbatible en precio/rendimiento para chat humano.
3. **ETL de Inventarios por Correo/WhatsApp:** 
   - Usa **Qwen 2.5 72B (`qwen/qwen-2.5-72b-instruct`)**. Son perfectos para estructurar las 10 columnas y hacer el `MERGE` a SQL sin alucinaciones.
4. **Agente de Servidor (Hermes):** 
   - Usa **DeepSeek R1 (`deepseek/deepseek-r1`)** como motor principal. Si la tarea es demasiado compleja o richiede interazioni velocissime senza "pensare" troppo, passa a **Claude Sonnet 4.6**.

# Plan de Implementación IA — Farmacia Americana

> **Documento vivo.** Referencia técnica de la arquitectura de modelos de IA para todos los flujos de n8n y el Hermes Agent en Debian.

---

## 1. Proveedor Único: OpenRouter

Todos los modelos se consumen a través de una **única credencial OpenRouter** (`openRouterApi`).
- Centraliza costos en una sola factura.
- Permite cambiar de modelo sin tocar credenciales.
- API Key gestionada en n8n → Settings → Credentials → `OpenRouter API`.

---

## 2. Arquitectura de Modelos por Nivel

| Nivel | Rol | Modelo (OpenRouter) | Trigger de Activación |
|:-----:|:---|:---|:---|
| 🚦 0 | Semáforo (Router) | `google/gemini-2.5-flash-lite` | Siempre (primer contacto) |
| 💬 1 | Chatbot Ventas | `meta-llama/llama-3.3-70b-instruct` | Intención de venta detectada |
| 🧠 2 | Escalada Analítica | `deepseek/deepseek-v4-flash` | Llama no resuelve / objeción precio |
| 🔬 C | Sub-agente Extractor Visual | `qwen/qwen3-vl-32b-instruct` | Cliente envía imagen (receta, caja) |
| 🔱 3 | Hermes Agent (Debian) | `nousresearch/hermes-4-405b` | DeepSeek no resuelve / tarea autónoma |
| 🛡️ ∞ | Modo Offline | `qwen/qwen2.5-vl-72b-instruct` | OpenRouter sin conexión (comodín total) |

---

## 3. Sistema de Doble Backup

Cada agente IA implementa **dos** mecanismos de resiliencia independientes:

### Backup Tipo A: Escalada Cognitiva (Model Selector)

**Problema:** El modelo principal no puede razonar la respuesta (tarea demasiado compleja).
**Mecanismo:** Nodo `Model Selector` conecta 2 modelos al mismo agente. Si el principal falla cognitivamente, el segundo (más potente) toma el control.

**Parejas de escalada aprobadas:**

| Agente | Modelo Principal | Modelo Escalada |
|:---|:---|:---|
| Chatbot Ventas | Llama 3.3 70B | DeepSeek V4 Flash |
| Semáforo | Gemini 2.5 Flash Lite | GPT-4o-mini-2024-07-18 |
| Hermes Agent | Hermes 4 405B | DeepSeek V4 Flash |

> **Nota:** Qwen 2.5 VL 72B cubre el Tipo B (infraestructura) para todos los agentes. No se requiere un tercer modelo en el Model Selector — el par Tipo A + Tipo B cumple la política del skill.

### Backup Tipo B: Fallback por Infraestructura (onError)

**Problema:** OpenRouter está caído, timeout, rate limit o error de red. El modelo ni siquiera responde.
**Mecanismo:** `onError: 'continueErrorOutput'` en el agente principal → `.onError()` conecta a un segundo `AI Agent` independiente con **Qwen 2.5 VL 72B** como comodín universal.

```
[Agente Principal] ──(éxito)──→ [Respuesta al cliente]
        │
        └──(error)──→ [Agente Emergencia Qwen] ──→ [Respuesta al cliente]
```

**Reglas del Agente de Emergencia (Qwen):**
- Misma credencial OpenRouter, modelo diferente (`qwen/qwen2.5-vl-72b-instruct`).
- Sus propias instancias de Tools SQL (subnodes no se comparten entre agentes).
- System prompt idéntico al principal + aviso: *"Estás actuando como respaldo de emergencia."*
- **Con memoria conversacional completa:** El Agente de Emergencia debe tener conectado el mismo tipo de memoria (`WindowBufferMemory` vinculado al `sessionId`) para heredar el contexto exacto donde falló el titular.

### Cobertura Tipo C: Sub-agente Extractor Visual

**Problema:** El cliente envía una imagen (foto de receta médica, caja de medicamento, vencimiento) dentro de la conversación. Llama y V4 Flash son modelos texto→texto y no pueden procesarla.
**Mecanismo:** El Agente Principal invoca el Sub-agente Extractor como **Tool**. El sub-agente recibe la imagen con el contexto de la conversación y devuelve un JSON estructurado. El Agente Principal usa ese JSON para buscar en SQL.

**Modelo:** `qwen/qwen3-vl-32b-instruct` — Ratio C/B: **338** (mejor de la categoría)
- $0.104 input / $0.416 output — 2.4× más barato que Qwen2.5 VL 72B
- Generación Qwen3 → mejor OCR que Qwen2.5 en texto médico español
- 131k contexto — acepta prompt de extracción completo sin truncarse
- **Contexto habilitado:** El sub-agente Extractor DEBE estar conectado a un nodo de memoria conversacional (o recibir el historial completo inyectado) para extraer la información visual considerando todo lo discutido previamente en el chat.

**System prompt del sub-agente (extractor puro):**
```
Eres un extractor de datos médicos desde imágenes para una farmacia.
Analiza la imagen y devuelve ÚNICAMENTE un JSON con:
{
  "tipo": "receta_medica | foto_caja | foto_vencimiento | otro",
  "medicamentos": [
    { "nombre": "...", "dosis": "...", "cantidad": "...", "instrucciones": "..." }
  ],
  "confianza": "alta | media | baja"
}
Si no identificas medicamentos: {"tipo": "no_identificado", "medicamentos": []}
NO elabores. Solo JSON.
```

**Diferencia clave con Tipo B:**
- Tipo B (Qwen 2.5 VL 72B): se activa cuando OpenRouter **falla** — es reactivo
- Tipo C (Qwen3 VL 32B): se activa cuando el input **contiene imagen** — es proactivo, el agente lo llama como Tool dentro del flujo normal

---

## 4. Flujo Completo: Copiloto Ventas Farmacia

**Workflow n8n:** `[PROD] Copiloto Ventas Farmacia` — ID: `XW91jFQU3Iu9lYPV`

```
Cliente (WhatsApp)
       ↓
  [Webhook POST /copiloto-ventas]
       ↓
  [Agente Principal]
  ├─ Tipo A (Model Selector):
  │   ├─ Input 0: Llama 3.3 70B      → rapport, chat natural, respuestas rápidas
  │   └─ Input 1: DeepSeek V4 Flash  → objeción precio, comparativa, argumento técnico
  ├─ Memoria: 10 turnos por sesión
  ├─ Tools SQL (4): Stock, Alternativas, Precios USD, Vencimientos
  ├─ Tool Tipo C: [Sub-agente Extractor Visual]
  │               ├─ Modelo: Qwen3 VL 32B
  │               ├─ Recibe: imagen_url + contexto_conversacion
  │               └─ Devuelve: JSON { tipo, medicamentos[], confianza }
  │
  ├──(éxito)──→ Respuesta al cliente
  │
  └──(error: Tipo B)──→ [Agente Emergencia Qwen 2.5 VL 72B]
                        ├─ Tools: 2 queries SQL (stock + alternativas)
                        └──→ Respuesta al cliente
```

---

## 5. Reglas de Credenciales

| Credencial | Nombre en n8n | Uso |
|:---|:---|:---|
| OpenRouter API | `OpenRouter API` | Todos los modelos IA (sin prefijo de entorno) |
| SQL Server | `[PROD] MSSQL - Saint Enterprise` | Todas las Tools SQL de los agentes |

- **UNA sola credencial OpenRouter** para todos los modelos.
- **Nunca hardcodear** API Keys en nodos `Code` o Sticky Notes.
- Las credenciales SQL se auto-asignan al crear workflows vía MCP.

---

## 6. Checklist de Producción

Antes de activar cualquier flujo con `AI Agent`:

- [ ] ¿Tiene Model Selector con escalada cognitiva? (Tipo A)
- [ ] ¿Tiene rama `.onError()` con Agente Emergencia Qwen? (Tipo B)
- [ ] ¿El system prompt lista los nombres exactos de las Tools?
- [ ] ¿La memoria conversacional usa `sessionId` del cliente (no "default")?
- [ ] ¿Las Tools SQL usan `$fromAi()` para parámetros dinámicos?
- [ ] ¿Los nodos siguen nomenclatura "Verbo + Sustantivo"?
- [ ] ¿Hay Sticky Notes con colores semánticos (🔵🟡🟢🔴)?
- [ ] ¿El Error Workflow global está asignado en Settings?
- [ ] ¿La credencial OpenRouter está creada y funcional?

# Guía de Estrategias de Enrutamiento de OpenRouter para n8n

Este documento detalla cómo podemos aprovechar las capacidades avanzadas de enrutamiento de OpenRouter dentro de nuestros flujos de trabajo en n8n (como Copiloto Ventas, Hermes Agent, etc.) para garantizar alta disponibilidad, reducir costos y optimizar la latencia/rendimiento.

---

## 1. Comportamiento por Defecto: Balanceo de Carga por Precio

Por defecto, si solo enviamos el parámetro `model` en nuestra petición (ej. `meta-llama/llama-3.3-70b-instruct`), OpenRouter realiza un **balanceo de carga priorizando el precio**:
1. Filtra los proveedores que han tenido caídas significativas en los últimos 30 segundos.
2. De los proveedores estables, selecciona priorizando el de menor costo.
3. Utiliza los proveedores restantes como opciones de respaldo (*fallbacks*).

> **Nota para n8n:** Si enviamos herramientas (`tools`) o definimos `max_tokens`, OpenRouter automáticamente ignorará a los proveedores que no soporten estas características.

---

## 2. Ordenamiento y Priorización Explícita (Sorting)

Si para un nodo específico de n8n necesitamos priorizar la velocidad sobre el costo (ej. respuestas en tiempo real por WhatsApp), podemos sobreescribir el balanceo de carga usando el objeto `provider.sort`.

Opciones disponibles para `sort`:
- `"price"`: Prioriza el precio más bajo (comportamiento base).
- `"throughput"`: Prioriza la mayor velocidad de generación de tokens.
- `"latency"`: Prioriza el menor tiempo de respuesta inicial.

### Atajos de Modelo (Shortcuts)
Para mayor simplicidad en el nodo HTTP de n8n, podemos añadir un sufijo directamente al nombre del modelo:
- `modelo:nitro` -> Equivale a `sort: "throughput"`. (Ej. `meta-llama/llama-3.3-70b-instruct:nitro`)
- `modelo:floor` -> Equivale a `sort: "price"`.

---

## 3. Fallbacks Avanzados y Partición Global

Cuando configuramos múltiples modelos de respaldo (ej. primero Claude, luego GPT-4o, luego Gemini) en el parámetro `models` (un array en lugar de un string), OpenRouter agrupa los *endpoints* por modelo. Esto significa que intentará todos los proveedores de Claude antes de pasar a GPT-4o.

Si nuestro objetivo es **"usar el modelo más rápido disponible en este instante, sin importar cuál de los 3 sea"**, debemos usar la partición global:

```json
{
  "models": [
    "anthropic/claude-sonnet-4.5",
    "openai/gpt-5-mini",
    "google/gemini-3-flash-preview"
  ],
  "provider": {
    "sort": {
      "by": "throughput",
      "partition": "none"
    }
  }
}
```
*Esto es sumamente útil para garantizar respuestas ultra rápidas en canales síncronos como Telegram o WhatsApp.*

---

## 4. Umbrales de Rendimiento (Percentiles)

Podemos exigir requisitos mínimos de rendimiento sin excluir del todo a los proveedores más lentos (simplemente los mueve al final de la lista de prioridad). OpenRouter evalúa esto en ventanas móviles de 5 minutos utilizando percentiles (`p50`, `p75`, `p90`, `p99`).

- **`preferred_min_throughput`**: Rendimiento mínimo preferido en tokens/seg.
- **`preferred_max_latency`**: Latencia máxima aceptada en segundos.

**Caso de Uso Práctico:** "Encontrar el modelo más barato, pero que el 90% de las veces responda a más de 50 tokens por segundo".
```json
{
  "provider": {
    "sort": { "by": "price", "partition": "none" },
    "preferredMinThroughput": { "p90": 50 }
  }
}
```

---

## 5. Control de Proveedores Específicos

En escenarios donde sabemos que un proveedor específico falla frecuentemente desde nuestra región, o necesitamos usar créditos BYOK (Bring Your Own Key), podemos manipular la lista de proveedores:

- **`order`**: Array de slugs de proveedores. Fuerza a OpenRouter a intentar estos proveedores *exactamente* en este orden. (Ej. `["openai", "together"]`).
- **`allow_fallbacks`**: (Booleano). Si se establece en `false` junto con `order`, la petición fallará si los proveedores indicados no responden, evitando que salte a un proveedor más costoso inesperadamente.
- **`ignore`**: Array de proveedores a excluir completamente. (Útil si un proveedor tiene problemas de red constantes con n8n).
- **`only`**: Array restrictivo. Solo usará los proveedores en esta lista.

### Apuntar a Endpoints Específicos (Variantes)
Podemos ser granulares. Usar `"deepinfra"` abarca todos sus nodos. Usar `"deepinfra/turbo"` solo apunta al nodo de máxima velocidad de ese proveedor.

---

## 6. Filtros de Calidad y Políticas de Datos

Para cumplir con normativas empresariales o requisitos técnicos de nuestras integraciones:

- **`require_parameters: true`**: Garantiza que la petición no se envíe a proveedores que ignoren parámetros enviados (esencial cuando usamos `response_format: { "type": "json_object" }` o definimos `tools`).
- **`data_collection: "deny"`**: Excluye proveedores que guardan datos de forma no transitoria o que entrenan modelos con nuestros prompts. Vital para datos confidenciales de farmacias/SAINT.
- **`zdr: true`**: Fuerza *Zero Data Retention*. Solo permite endpoints que certifiquen no retener los prompts.
- **`quantizations`**: Filtra por nivel de compresión del modelo (ej. `["fp8"]`). Modelos muy comprimidos (int4) pueden degradar la calidad de razonamiento lógico en nuestras tareas de programación (Python/SQL).
- **`max_price`**: Define el costo tope aceptable. Ej. `{"prompt": 1, "completion": 2}` ($1 por 1M tokens de entrada, $2 por 1M tokens de salida).

---

## 7. Características Beta de Proveedores (Headers Especiales)

Para exprimir las funciones más recientes (especialmente con Anthropic/Claude), OpenRouter permite pasar headers personalizados a través del nodo HTTP de n8n:

Header: `x-anthropic-beta`

**Valores útiles para nuestro proyecto:**
- `fine-grained-tool-streaming-2025-05-14`: Para obtener actualizaciones en tiempo real de los argumentos de una función/herramienta mientras el modelo la genera.
- `interleaved-thinking-2025-05-14`: Permite que los bloques de razonamiento interno de Claude se entrelacen con el output regular.
- `structured-outputs-2025-11-13`: Valida estrictamente los parámetros de las herramientas contra nuestro esquema JSON (vital para agentes que ejecutan acciones críticas).

*Nota: Para habilitar varios, se separan por comas.*

---
**Documento generado para estandarizar el uso de IA y LLMs dentro de la infraestructura n8n.**

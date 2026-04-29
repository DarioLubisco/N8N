Para lograr una integración omnicanal robusta y eficiente, aprovechando tus 6 GB de RAM y discos de 15k RPM, seguiremos una estrategia donde **Chatwoot es el centro de mando** y **n8n es el cerebro procesador**.

Aquí tienes la hoja de ruta técnica paso a paso:

---

### Fase 1: Configuración de Canales en Chatwoot (El Hub)
Chatwoot centralizará las conversaciones para que n8n solo tenga que escuchar a un único origen.

1.  **WhatsApp (vía Evolution API):**
    *   En Evolution API, genera una instancia y escanea el QR.
    *   En Chatwoot, ve a `Ajustes > Bandejas de entrada > Añadir bandeja`.
    *   Selecciona "API" (o el conector específico si usas un bridge). La mayoría usa la integración nativa de Evolution API enviando los webhooks a la URL de tu instancia de Chatwoot.
2.  **Telegram:**
    *   Crea un bot con [@BotFather](https://t.me/botfather) y obtén el Token.
    *   En Chatwoot, añade una nueva bandeja de tipo **Telegram** y pega el token. Es instantáneo.
<truncated 3001 bytes>
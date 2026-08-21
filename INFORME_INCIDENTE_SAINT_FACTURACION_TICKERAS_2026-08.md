# INFORME — Incidente Saint Enterprise: cuelgues de facturación y tickeras (8–20 ago 2026)

> **Autor:** ZCode (asistente de infraestructura) · **Revisión:** Dario Lubisco / Willy
> **Sistemas:** SVR-SAINT-AMC (SQL Server 2025, cloud), cajas CAJA001–004 (x64, usuario
> `farmacia americana`), DARIO-DESKTOP (Win11 ARM, servidor de tickera XP-80C por USB).
> **Estado final:** ✅ facturación ~7–11 s de SQL (antes 105–175 s) + tickera por LAN directa (<1 s).

---

## 1. Resumen ejecutivo

El 8/8/2026 se mudó el servidor SQL a la nube y toda la red interna a ZeroTier/Tailscale.
Desde ese día cada factura se congelaba 80–175 s. Tras 3 días de diagnóstico instrumental
(XE de SQL, monitoreo de NIC, logs de spooler, pruebas forenses de colas) se identificaron
**seis capas de problemas apiladas**, ninguna visible por separado:

1. **Ventana TCP chica del cliente embebido de Saint (32-bit) × latencia 154 ms** → 118 KB/s.
2. **Packet size 2400 del SQL** que fijaba el buffer de lectura del driver viejo.
3. **Tickeras apuntando a un puerto TCP 9100 muerto** (la impresora es USB en otro PC).
4. **Drivers de impresora corruptos** en varios almacenes (jobs EMF "documento dañado").
5. **Redirects LPT por sesión** (la reconexión caía en la sesión equivocada; LPT1 físico
   exige elevación para usuarios estándar → cuelgues de minutos).
6. **MagicDNS de Tailscale secuestrando el nombre `dario-desktop`** hacia una IP muerta,
   pisando el archivo hosts.

**La solución final** separa los planos correctamente: SQL por ZeroTier (necesario),
impresión por **IP LAN directa** (las cajas y el PC de Darío están en el mismo switch),
cuenta de servicio dedicada, driver instalado localmente y tarea por-usuario al logon.

---

## 2. Evidencia clave (mediciones)

### 2.1 El cuelgue de facturación era la carga de plantillas SFTITM

Saint ejecuta `SELECT A.* FROM SFTITM ORDER BY itemid` (48 filas, **4.13 MB** de plantillas
fiscales, columna `image`) **3–5 veces por factura**. Con XE se capturó en vivo: el servidor
termina el query en **79 ms de CPU** y queda esperando en `ASYNC_NETWORK_IO` el resto
(transferencia al cliente).

| Packet size SQL | Carga SFTITM | Factura completa |
| :--- | :--- | :--- |
| 2416 (original) | ~35 s × 3–5 | **105–175 s** |
| 8000 | ~10.5 s × 3–5 | ~42–53 s |
| **32767 (final)** | **~2.7 s × 2–4** | **~7–11 s** |

La red soportaba 4–8 MB/s (probado con cliente moderno .NET: misma tabla en 0.5 s) —
el límite era la ventana del cliente (ventana ÷ RTT): 20 KB ÷ 154 ms ≈ 130 KB/s.
Por eso en LAN (RTT 1 ms) nunca se notó: el mismo defecto daba 20 MB/s.

### 2.2 La red de impresión estaba rota de fábrica tras el 8/8

- Puerto TCP RAW `10.147.18.63:9100` **muerto** (la tickera es USB en DARIO-DESKTOP).
- Cola con job veneno de 64 KB "document" `[Error, Printing, Retained]` que tapaba
  las `Factura Ticket` reales (log PrintService/Admin: "daño en el archivo").
- El `print$` de DARIO-DESKTOP (Windows **ARM**) no sirve drivers x64 → instalaciones
  infinitas pidiendo consentimiento.
- `dario-desktop` resolvía a la IP Tailscale muerta pese al hosts (MagicDNS/NRPT pisa hosts).

---

## 3. Arquitectura final (la que quedó operativa)

```
CAJAS (x64, usuario "farmacia americana"; SynapseAdmin oculto y solo SSH)
  │
  ├─ SQL ─────────── ZeroTier 10.147.18.192, packet size 32767
  │
  └─ TICKERA ─────── \\10.200.8.110\XP-80C (copy 1)   ← IP LAN directa (0 ms)
                      credencial: DARIO-DESKTOP\Impresora (cuenta de servicio)
                      driver XP-80C x64 instalado LOCALMENTE en cada caja
                      tarea "ConectarImpresoraLAN" al logon del cajero:
                        cmdkey + rundll32 /in + SetDefaultPrinter
```

### Componentes por caja
| Componente | Detalle |
| :--- | :--- |
| Conexión | `\\10.200.8.110\XP-80C (copy 1)` — única, y predeterminada |
| Credencial | `cmdkey /add:10.200.8.110 /user:DARIO-DESKTOP\Impresora /pass:***` (ver `synapse.credentials`) |
| Driver | XP-80C x64 local (trasplantado: archivos `XP80*` de `spool\drivers\x64\3` + clave de registro `...\Version-3\XP-80C`) |
| Tarea programada | `ConectarImpresoraLAN` — disparo al logon del SID del cajero, `InteractiveToken`, oculta |
| Política | `PointAndPrint`: `NoWarningNoElevationOnInstall=1`, `RestrictDriverInstallationToAdministrators=0` |
| Saint | Impresor #1 → la conexión de IP o 'Predeterminada' (son la misma) |

### En el servidor de tickera (DARIO-DESKTOP)
- Share `XP-80` con **Everyone Full**; `print$` Everyone Read.
- Cuenta local `Impresora` (contraseña en `synapse.credentials`: `DARIO_PC_ADMIN_PASSWORD`).
- ZeroTier OK (MTU 1280 — arreglado a mano). Tailscale opcional/intermitente — **no usar
  su nombre en configs** (MagicDNS pisa hosts).

---

## 4. Cookbook de remedios (lo aprendido a golpes)

| Síntoma | Causa | Remedio |
| :--- | :--- | :--- |
| Factura 80–175 s, SQL esperando `ASYNC_NETWORK_IO` | ventana chica × RTT | `sp_configure 'network packet size', 32767` + reiniciar Saint en cada caja |
| Cola que no drena | job `[Error, Retained]` | `Get-PrintJob \| Remove-PrintJob` + `Restart-Service Spooler`; si persiste: parar spooler y borrar `C:\Windows\System32\spool\PRINTERS\*` |
| Impresora `Error, PendingDeletion` | borrado a medias | parar spooler → limpiar `spool\PRINTERS` → arrancar → recrear |
| "Controlador no válido" al asignar driver | almacén corrupto | usar otro driver del fabricante presente o trasplantar (archivos + `reg export/import` de la clave del driver) |
| Driver no baja del print$ | servidor ARM (print$ sin x64) | trasplantar desde una caja que lo tenga (ver §3) |
| Instalación pide consentimiento siempre | Point&Print | política `NoWarningNoElevationOnInstall=1` (y/o driver ya local) |
| `net use` como cajero → Acceso denegado en LPT1 | LPT1 físico exige elevación | usar **LPT2** (nombre libre) o conexión de impresora por UNC |
| Redirect funciona en mi sesión pero Saint no imprime | redirects **por sesión** | tarea por-usuario (SID + InteractiveToken) al logon del cajero |
| Credencial guardada con la clave en el usuario | `cmdkey` sin `/pass:` | **SIEMPRE** `/pass:` — y `cmdkey /delete:<target>` antes de re-crear |
| Nombre `dario-desktop` resuelve a IP muerta pese a hosts | MagicDNS/NRPT de Tailscale | **usar IPs** (`10.200.8.110`), nunca nombres, en configs de impresión |
| App colgada sin SQL activo ni cola | escritura bloqueada a LPT físico muerto | recrear el redirect / conexión; no esperar el timeout |
| Caja guindada + "no imprime" tras reinicio nocturno | redirect no restaurado (red tardía) | tarea al logon con loop de reintentos (60 × 10 s) |

### Instrumentación usada (reutilizable)
- **XE event_file** `XE_ALL_CAJAS` (rpc/batch_completed + attention por hostname LIKE '%CAJA%').
  Ring buffer NO (lock con dispatch activo). Dump: `fn_xe_file_target_read_file` + XQuery
  **rutas absolutas** (`/event/...`) — las relativas devuelven NULL.
- Throughput: `Get-NetAdapterStatistics` a 1 Hz (tarea programada — SSH mata procesos hijos).
- Estado de app: `Get-Process SaintV` con `Responding`/CPU a 0.5 Hz.
- `quser` + `HKU\<SID>\Volatile Environment` para identificar sesión/usuario del cajero.

---

## 5. Accesos vigentes

| Máquina | Cómo entrar |
| :--- | :--- |
| SVR-SAINT-AMC (10.147.18.192) | `ssh -i ~/.ssh/farmacia_admin Administrator@10.147.18.192` · SQL: `sa` (creds en archivo) |
| Cajas (10.147.18.69/.99/.123/.170) | `ssh -i ~/.ssh/farmacia_admin SynapseAdmin@<ip>` (clave `Twinc3pt.0` documentada) |
| DARIO-DESKTOP | ZeroTier: `ssh -i ~/.ssh/synapse_windows_ed25519 SynapseAdmin@10.147.18.63` · LAN: `10.200.8.110` · Tailscale intermitente `100.126.220.118` |
| Cuenta de servicio tickera | `DARIO-DESKTOP\Impresora` (ver `synapse.credentials`) |
| Usuario visible en cajas | `farmacia americana` (SynapseAdmin oculto via `SpecialAccounts\UserList`) |

Secretos: **siempre** en `source/N8N/synapse.credentials` (nunca en este documento).

---

## 6. Pendientes de mantenimiento

1. **Limpiar instrumentación:** sesiones XE (`XE_C4/C5/C6/XE_ALL_CAJAS` + `.xel` en
   `MSSQL\Log`), tareas `MON_*` en servidor/cajas, log PrintService/Operational de
   CAJA004 (`wevtutil sl .../Operational /e:false`), scripts en `C:\Windows\Temp`.
2. **CAJA001 y CAJA002** son las cajas más frágiles (caídas totales, almacenes corruptos):
   vigilarlas; considerar reacondicionarlas.
3. Tailscale en DARIO-DESKTOP se desloguea solo — si se usa, re-autenticar; las configs
   de impresión **ya no dependen de él**.
4. La tarea `ConectarImpresoraLAN` dispara en cada logon del cajero — es el seguro de
   auto-reparación del parque; no borrarla.
5. Si cambia la contraseña de `Impresora`: actualizarla en `synapse.credentials` y en la
   tarea (`cmdkey`) de las 4 cajas.

---

## 7. Línea de tiempo resumida

| Fecha | Hito |
| :--- | :--- |
| 8/8 | Mudanza a cloud + VPN → comienzan los cuelgues |
| 15/8 | Diagnóstico instrumental: SFTITM 4.13MB × 3-5 por factura vía ASYNC_NETWORK_IO |
| 15/8 | Packet size 2400→8000→**32767**: factura 105–175 s → **11 s** |
| 16/8 | MTU de DARIO-DESKTOP 2800→1280 (a mano); tickera 004 viaja por SMB |
| 17/8 | Tickeras: puerto UNC + drivers; colas purgadas; tarea al logon (ventana visible → la cierran) |
| 18-19/8 | Redirect LPT por sesión del cajero; cuenta `Impresora` creada; permisos Everyone |
| 20/8 | **Descubrimiento LAN**: cajas y Darío en el mismo switch (10.200.8.0/24, 0 ms). Conexión por IP pura, driver x64 trasplantado, MagicDNS neutralizado usando solo IPs |
| 20/8 (final) | **Parque completo**: 4 cajas con conexión única `\\10.200.8.110\XP-80C (copy 1)`, predeterminada, driver local — "todas listas" ✅ |

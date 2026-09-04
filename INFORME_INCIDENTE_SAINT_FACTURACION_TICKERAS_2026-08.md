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
| **"La configuración para obtener acceso a la impresora 'X' no es válida"** con la conexión visible (`Get-Printer` la lista, hive OK) | **driver envenenado client-side**: los archivos locales del driver son MÁS NUEVOS que el paquete del servidor → Point&Print rechaza silenciosamente el "downgrade" al conectar → cola viva pero sin DEVMODE (víctimas: XP-80C en 004, POS-80C en 003, ambos del 17-20/8) | cura en 5 pasos (ver §8.2): purgar conexión **en la sesión del usuario** → `Remove-PrinterDriver` → reconectar `printui /in` (re-baja Point&Print) → probar → predeterminar |
| "Windows no se pudo conectar a la impresora" al reconectar tras caída | cola del SERVIDOR tapada con job retenido `[Error, Printing, Retained]` (p. ej. página de prueba del 28/08 en ADM-3) | purgar cola + reiniciar spooler **en el host que comparte**; sin eso, todo cliente recibe el error genérico |
| Tarea por-usuario no arranca desde SSH (`0xFFFD0000`, sin log) | script en `C:\Windows\Temp` (los usuarios estándar no pueden leer/ejecutar de ahí) o LogonType mal registrado por cmdlet | script y log en `C:\Users\Public`; registrar con **XML UTF-16** (`LogonType InteractiveToken` en XML siempre funciona; el cmdlet `-LogonType` varía por versión); lanzar con `schtasks /run /tn` |
| **Todas las cajas pierden tickera de golpe sin cambio aparente** | **reinicio del adaptador Ethernet de DARIO-DESKTOP** (fix de DAD): el adaptador bajó y subió → todas las sesiones SMB a `\\10.200.8.110\XP-80` se rompieron silenciosamente. Las tareas de logón ya habían corrido antes del cambio y no se re-ejecutaron | reconexión remota vía tarea por-usuario + `schtasks /run`; **lección: SIEMPRE reiniciar las tareas de logón después de tocar el adaptador de red del servidor de tickera** |
| IP estática sin DNS | `netsh set address` solo fija la IP, NO los DNS | **SIEMPRE** `netsh interface ip set dnsservers` después de `set address` |
| DAD false positive al reasignar IP estática | la tabla ARP del switch/router tiene entrada vieja de la IP anterior (DHCP) | `netsh interface ipv4 set interface Ethernet dadtransmits=0` + reiniciar adaptador; **mejor usar DHCP binding en el router** |
| **DHCP binding en router vs IP estática** | IP estática: manual, se pierde al reimagear, DAD, DNS manual | **reservar en el router** (DHCP Binding): IP fija + DNS/GW automáticos, sin DAD, sobrevive reimageados |

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
| DARIO-DESKTOP | ZeroTier: `ssh -i ~/.ssh/farmacia_admin "dario lubisco@10.147.18.63"` (**usuario con espacio**, token admin pleno por SSH) · LAN: `10.200.8.110` (puerto 22 cerrado ahí) |
| Cuenta de servicio tickera | `DARIO-DESKTOP\Impresora` (ver `synapse.credentials`) |
| Usuario visible en cajas | `farmacia americana` (SynapseAdmin oculto via `SpecialAccounts\UserList`) |

Secretos: **siempre** en `source/N8N/synapse.credentials` (nunca en este documento).

### Canales de reporte (cuando haya inconvenientes)
- **Telegram (automático):** bot `TELEGRAM_AMC_NOTIFICACION_BOT` → chat `ERROR_CHAT_ID` (alertas del sistema)
- **Telegram (admin):** bot `TELEGRAM_AMC_ADMIN_BOT` → chat `AMC_ADMINISTRATIVO_CHAT_ID` (pedidos/bandeja)
- **WhatsApp Dario (admin):** 0412-0430029
- **Llamada directa:** Dario (admin) / Willy (técnico)

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
| 28/8 | Página de prueba queda retenida `[Error]` en la cola de POS-80C (ADM-3) — queda tapando en silencio |
| 1/9 | DHCP muda DARIO-DESKTOP a .119 → flota entera "sin tickera". Usuario fija **IP estática .110** (ARP verificado, sin conflicto) |
| 1/9 | Cura del **driver envenenado** (§8.2): 004 y 003 re-bajan XP-80C/POS-80C por Point&Print. Flota 100% operativa: 001/002/003/004 ✅ (devolución real impresa en 003 como validación de negocio) |
| 1/9 (tarde) | **DNS + DAD** en DARIO-DESKTOP: fix DNS (8.8.8.8) + DAD false positive (dadtransmits=0). DHCP binding en router ACLF625: MAC D4:3D:7E:21:29:DF → .110 |
| 1/9 (tarde) | **Flota despuée del reinicio del adaptador Ethernet**: todas las conexiones SMB se rompieron silenciosamente (el adaptador bajó y subió → sesiones SMB muertas). Reconexión remota de las 4 cajas |

---

## 8. Sesión 2026-09-01 — rematerialización de la flota y cura del driver envenenado

### 8.1 Qué pasó
Tras el flapping de DHCP (DARIO-DESKTOP .110→.119→.110 estático) toda caja perdió la
tickera. Al reconectar apareció un error NUEVO que no respondía a los remedios del
cookbook: la conexión existía y se enumeraba (`Get-Printer` la listaba como
`Connection`, hive con la entrada `,,10.200.8.110,XP-80C (copy 1)`), pero **cualquier
impresión fallaba** con `InvalidPrinterException` ("La configuración para obtener acceso
a la impresora no es válida"). El DEVMODE no se podía abrir.

**Causa raíz:** los archivos del driver en la caja eran más nuevos (`.BUD` del 17/8, de
nuestros transplantes) que el paquete que ofrece DARIO-DESKTOP (14/8). Point&Print
rechaza actualizar un driver a una versión *menor* (evento PrintService id=232 demuestra
el mecanismo de rechazo) y deja la cola conectada con el driver en estado no utilizable.

Hallazgos accesorios de la sesión:
- La cola fiscal de **ADM-3** (`\\10.200.8.145\POS-80C`) seguía tapada desde el 28/8 con
  una página de prueba `[Error, Printing, Retained]` + 2 "Report": eso producía el
  "Windows no se pudo conectar" genérico en cualquier cliente. Purga + reinicio → Normal.
- `C:\Windows\Temp` **no es legible/ejecutable** por usuarios estándar: las tareas
  por-usuario deben apuntar a scripts en `C:\Users\Public` (y loguear ahí mismo).
- `Register-ScheduledTask -LogonType InteractiveToken` falla en algunas versiones de PS
  (enum `Interactive`); el valor **en el XML** (`<LogonType>InteractiveToken</LogonType>`)
  funciona siempre. Clonar el XML de una tarea que sí funciona es la vía rápida.
- `Start-ScheduledTask` a veces no arranca (0xFFFD0000); `schtasks /run /tn <tarea>` sí.
- En 002 la tarea de logón apuntaba a otro usuario → la conexión no se recreaba al
  re-loguear la cajera. Recrearla con el **SID del usuario real de consola**.

### 8.2 La cura del driver envenenado (5 pasos, probada en 004 y 003)
1. **Purgar la conexión EN la sesión del usuario afectado** (tarea por-usuario con su SID):
   `(New-Object -ComObject WScript.Network).RemovePrinterConnection('\\10.200.8.110\XP-80C (copy 1)')`
2. `Remove-PrinterDriver -Name 'XP-80C'` (SSH como admin). Si dice "está siendo usado":
   revisar conexiones residuales en otras sesiones; el reinicio de spooler NO siempre la
   libera (quedó pendiente en 003 para XP-80C, que al final no hizo falta tocar).
3. Reconectar con re-descarga: tarea por-usuario con
   `rundll32 printui.dll,PrintUIEntry /in /n"\\10.200.8.110\XP-80"` (2–4 min: baja el
   driver limpio del servidor).
4. Probar en su sesión: `"prueba" | Out-Printer -Name '\\10.200.8.110\XP-80C (copy 1)'`
   → `OK` = imprimió físicamente en la tickera de Darío.
5. `(New-Object -ComObject WScript.Network).SetDefaultPrinter(...)` + registrar tarea de
   **logón** (XML con SID del usuario de consola) para que sobreviva re-logueos.

### 8.3 Estado final de la flota (validado 1/9 por la tarde)

| Caja | Usuario consola | Tickera | Validación |
| :--- | :--- | :--- | :--- |
| CAJA001 | `Caja03` | ✅ | impresión real confirmada por el usuario (va por LPT2→SMB, su arquitectura propia) |
| CAJA002 | `Caja02` | ✅ | `PRINT OK` técnico + predeterminada; tarea de logón recreada con su SID |
| CAJA003 | `Dario` | ✅ | **devolución real impresa** + `PRINT OK` técnico; predeterminada fijada |
| CAJA004 | `farmacia americana` | ✅ | `PRINT OK` técnico tras cura de driver + facturación real del usuario |

### 8.4 Pendientes surgidos en esta sesión
1. **Fiscal en 003** (`\\10.200.8.145\POS-80C`): la conexión quedó purgada y el driver
   POS-80C eliminado; ADM-3 accesible (ping/SMB OK). Al próximo inicio de sesión de la
   cajera la tarea `ConectarFiscalADM3` (ya probada, 0x0) lo reconecta. Falta además que
   **Willy asigne el canal fiscal en el Configurador de Saint** de la 003 hacia esa cola.
   *(El síntoma histórico "la fiscal imprime en la tickera" era esto: sin destino fiscal
   vivo, Saint cae al predeterminado.)*
2. ~~**SSH a DARIO-DESKTOP**: ambas claves rechazadas~~ **RESUELTO 1/9**: el usuario
   correcto es `dario lubisco` (con espacio, ver `synapse.credentials`) y la sesión SSH
   tiene token admin pleno (netsh funciona sin elevación). Puerto 22 solo accesible por
   ZeroTier (10.147.18.63), no por LAN.
3. **CAJA001**: mapeo viejo `LPT1: → \\10.147.18.63\XP-80` (servidor muerto) marcado
   "No disponible". No estorba, pero conviene `net use LPT1 /delete` en la próxima visita.
4. **ADM-3**: trabajos "Report" cada ~20 min hacia POS-80C — identificar el origen (¿algún
   reporte programado de Saint?) para que no vuelvan a tapar la cola fiscal.
5. **DNS de DARIO-DESKTOP (resuelto 1/9)**: al fijar la IP estática con `netsh set address`
   NO se asignaron servidores DNS → Windows usaba placeholders `fec0:0:0:ffff::` → sin
   navegación (ping IP OK, resolución timeout). Fix: `netsh interface ip set dns
   name="Ethernet" static 8.8.8.8 primary` + 1.1.1.1/8.8.4.4.
6. **DAD false positive en DARIO-DESKTOP (resuelto 1/9)**: tras el fix DNS, Windows
   detectó la IP `.110` como "Duplicate" (DAD) y la marcó APIPA. Fix: `netsh interface
   ipv4 set interface Ethernet dadtransmits=0` + reinicio del adaptador (sin tocar la
   configuración estática). **Lección: cuando se fija IP estática a mano con `netsh`,**
   **fijar SIEMPRE también `set dnsservers` Y desactivar DAD si es necesario.**
7. **Flota rota post-fix de DAD (resuelto 1/9)**: el reinicio del adaptador Ethernet de
   DARIO-DESKTOP (necesario para el fix de DAD) bajó la interfaz por unos segundos →
   todas las sesiones SMB de las 4 cajas se rompieron silenciosamente. Las tareas de
   logón ya habían corrido antes del cambio y no se re-ejecutaron. Las 4 cajas quedaron
   "vivas pero sin tickera". Fix: reconexión remota vía `schtasks /run` de la tarea
   `ReconNow` (creada dinámicamente con el SID del usuario de consola de cada caja).
   **Lección crítica: SIEMPRE reiniciar las tareas de logón de impresora después de
   tocar el adaptador de red del servidor de tickera (DARIO-DESKTOP).**
8. **Router Huawei ACLF625 (configurado 1/9)**: DHCP Binding en el router con MAC
   `D4:3D:7E-21:29:DF` → IP `10.200.8.110`. Login: admin/admin. Ruta: Network → LAN →
   DHCP Configuration → DHCP Binding. **Dario ahora recibe `.110` por DHCP** — sin IP
   estática, sin DAD, sin DNS manual. La IP estática fue revertida a DHCP tras la
   configuración del binding. Credenciales del router documentadas en `synapse.credentials`.

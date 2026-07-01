---
name: monitor-system-pro
description: Expert in managing and maintaining the MonitorSystem infrastructure, including PowerShell monitoring scripts and server orchestration.
---

# Monitor System Pro Skill

Este skill define los protocolos para el mantenimiento y la operación del sistema de monitoreo centralizado en `C:\source\MonitorSystem`.

## Arquitectura del Sistema

El sistema utiliza PowerShell y el Programador de Tareas de Windows para asegurar que los servicios críticos (Producción y Desarrollo) estén siempre activos.

### Componentes Clave
1. **MonitorServicios.ps1**: Lógica central que verifica puertos (8000, 8080, 8001, 8081).
2. **FixTaskScheduler.ps1**: Gestión de la tarea programada "Start All Server".
3. **run_all_servers.bat**: Punto de entrada para ejecución oculta.
4. **out.log**: Registro histórico de actividad.

## Protocolo de Operación y Seguridad

### 1. Desarrollo Local Primero
> [!IMPORTANT]
> **REGLA DE ORO**: No inyectar código directamente a la rama `main` ni realizar cambios en producción sin validación previa. Trabaja siempre localmente a menos que recibas el comando explícito del usuario.

### 2. Mantenimiento de Servicios
Para agregar un nuevo servicio:
1. Localizar el array `$services` en `MonitorServicios.ps1`.
2. Añadir un nuevo objeto con `Port`, `Path` y `Name`.
3. Validar la ruta del ejecutable/entorno virtual.

### 3. Gestión de Tareas Programadas
Cualquier cambio en la frecuencia o triggers de monitoreo debe realizarse a través de `FixTaskScheduler.ps1`. 
- Se requiere ejecución con privilegios de Administrador.
- El trigger estándar es al Inicio de Sesión (Logon) y diariamente a las 00:00.

## Solución de Problemas
- **Servidor no inicia**: Verificar logs en `out.log`.
- **Tarea programada falla**: Ejecutar `run_all_servers.bat` manualmente para verificar errores visuales en la consola (si se quita el flag de oculto temporalmente).
- **Puerto ocupado**: Identificar procesos con `netstat -ano | findstr :<PUERTO>`.

## ⚙️ Orquestación y Herramientas (n8n)
Al integrar este sistema con flujos de n8n, se debe seguir el protocolo de prioridad:
1. **n8n-arquitectura (MCP)**: Mandatorio para lógica y nodos.
2. **n8n-mcp (MCP)**: Respaldo.
3. **Navegador**: Solo para UI o como último recurso.

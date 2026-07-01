# Antigravity Skills - Sincronización

Este directorio contiene todos los Skills globales de Antigravity sincronizados.

## Ubicación Original

`~/.gemini/config/skills/`

## Contenido

- **56 skills** instalados
- **140 MB** total
- Skills globales de Antigravity v2 Hub

## Estructura

Cada skill está en su propio directorio con un archivo `SKILL.md` obligatorio.

## Aplicar Configuración

Para aplicar estos skills en otra computadora:

```bash
cp -r antigravity-skills/* ~/.gemini/config/skills/
```

## Actualizar Sincronización

Para actualizar este directorio con cambios locales:

```bash
cp -r ~/.gemini/config/skills/* antigravity-skills/
```

## Notas

- Estos son skills globales, disponibles en todos los proyectos de Antigravity
- Algunos skills pueden ser symlinks a otras ubicaciones
- Asegúrate de mantener la estructura de directorios al sincronizar
# Cumbre Digital Peru 2026 — Proyecto de Práctica

## Sobre este proyecto
App web de registro de asistentes para "Cumbre Digital Peru 2026".

## Stack tecnológico
- Fase 1: HTML + CSS + JavaScript (sin servidor)
- Fase 2: Python 3 + Flask + PostgreSQL en Supabase (psycopg v3, `psycopg[binary]`; no usar psycopg2)
- Despliegue: Render.com (opcional)

## Reglas de trabajo
- Todo el contenido y comentarios en español
- Sin frameworks CSS externos (solo CSS puro)
- Diseño responsivo, tema oscuro, moderno
- La base de datos es PostgreSQL en Supabase; la conexión se lee de la variable DATABASE_URL
  (en local desde .env, en Render desde el panel). Usar el "Session pooler" (IPv4)
- Si la contraseña tiene caracteres especiales (@, $, :, /, #...), codificarlos en la URL (%40, %24...)
- Nunca subir .env al repositorio
- Sin autenticación ni login de momento
- Mensajes de error claros en español

## Estructura del proyecto (Fase 2)
- app.py → servidor Flask principal
- templates/ → páginas HTML (index, confirmacion, admin, 404)
- requirements.txt → dependencias Python
- Procfile → configuración para Render

## Tabla asistentes (Supabase)
- id (serial), nombre, email (único), empresa, area_interes,
  numero_registro (único, formato REG-0001), fecha_registro (default now())

## Contexto del evento
- Nombre: Cumbre Digital Peru 2026
- Tema: Transformación digital para PyMEs
- Campos del formulario: nombre completo, email, empresa, área de interés
- Áreas: Tecnología / Marketing / Negocios / Emprendimiento

## Servidores MCP disponibles (alcance proyecto)
- github: para subir el código al repositorio
- supabase: para consultar la base de datos PostgreSQL del proyecto
- sqlite: solo para consultar el evento.db antiguo (versión SQLite anterior)
- playwright: para pruebas automáticas (Fase 3)
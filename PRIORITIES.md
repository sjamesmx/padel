# Priorización de Endpoints Críticos para Padelyzer

## Endpoints Críticos Identificados
Los siguientes endpoints son esenciales para los flujos de usuario principales y deben priorizarse en la siguiente iteración:

### Autenticación
- **/api/v1/auth/signup**
  - **Descripción**: Permite a los usuarios registrarse en la plataforma.
  - **Importancia**: Flujo inicial para nuevos usuarios; sin esto, no pueden acceder a la app.
- **/api/v1/auth/login**
  - **Descripción**: Permite a los usuarios iniciar sesión.
  - **Importancia**: Flujo esencial para usuarios existentes; sin esto, no pueden usar la app.

### Gestión de Usuarios
- **/api/v1/users/me**
  - **Descripción**: Devuelve el perfil del usuario autenticado.
  - **Importancia**: Permite a los usuarios ver su información; esencial para la experiencia del usuario.
- **/api/v1/users/{user_id}/profile**
  - **Descripción**: Devuelve el perfil público de un usuario específico.
  - **Importancia**: Necesario para funcionalidades sociales (ver perfiles de otros usuarios).

### Análisis de Videos
- **/api/v1/video/upload**
  - **Descripción**: Permite a los usuarios subir videos para análisis.
  - **Importancia**: Funcionalidad core de Padelyzer; sin esto, la app no cumple su propósito principal.

## Justificación
Estos endpoints cubren los flujos principales de usuario:
- Registro e inicio de sesión (autenticación).
- Gestión del perfil (ver y actualizar datos del usuario).
- Subida y análisis de videos (funcionalidad core).
Priorizar estos endpoints asegura que los usuarios puedan interactuar con la app de manera básica mientras se implementan otras funcionalidades (como social wall o matchmaking) en iteraciones futuras. 
# Historias de Usuario para Endpoints Críticos de Padelyzer

## Autenticación

### /api/v1/auth/signup
- **Historia**: Como usuario nuevo, quiero registrarme con mi email y contraseña, para poder acceder a las funcionalidades de Padelyzer.
- **Criterios de Aceptación**:
  - Dado que ingreso un email y contraseña válidos, cuando me registro, entonces recibo un mensaje de éxito.
  - Dado que ingreso un email ya registrado, cuando intento registrarme, entonces recibo un error 400.
- **Prioridad**: Alta
- **Vinculación**: Ver criterios en `ACCEPTANCE_CRITERIA.md`.

### /api/v1/auth/login
- **Historia**: Como usuario registrado, quiero iniciar sesión con mi email y contraseña, para acceder a mi cuenta y usar la app.
- **Criterios de Aceptación**:
  - Dado que ingreso credenciales válidas, cuando inicio sesión, entonces recibo un token de acceso.
  - Dado que ingreso credenciales incorrectas, cuando intento iniciar sesión, entonces recibo un error 401.
- **Prioridad**: Alta
- **Vinculación**: Ver criterios en `ACCEPTANCE_CRITERIA.md`.

## Gestión de Usuarios

### /api/v1/users/me
- **Historia**: Como usuario autenticado, quiero ver mi perfil, para conocer mi información y nivel actual.
- **Criterios de Aceptación**:
  - Dado que estoy autenticado, cuando solicito mi perfil, entonces recibo mis datos (email, nivel, etc.).
  - Dado que no estoy autenticado, cuando solicito mi perfil, entonces recibo un error 401.
- **Prioridad**: Alta
- **Vinculación**: Ver criterios en `ACCEPTANCE_CRITERIA.md`.

### /api/v1/users/{user_id}/profile
- **Historia**: Como usuario, quiero ver el perfil público de otro usuario, para conocer su nivel y estadísticas.
- **Criterios de Aceptación**:
  - Dado un ID de usuario válido, cuando solicito su perfil, entonces recibo sus datos públicos.
  - Dado un ID de usuario inexistente, cuando solicito su perfil, entonces recibo un error 404.
- **Prioridad**: Media
- **Vinculación**: Ver criterios en `ACCEPTANCE_CRITERIA.md`.

## Análisis de Videos

### /api/v1/video/upload
- **Historia**: Como usuario autenticado, quiero subir un video para análisis, para obtener estadísticas de mi juego.
- **Criterios de Aceptación**:
  - Dado que estoy autenticado y subo un video válido, cuando envío el video, entonces recibo un mensaje de éxito y el ID del video.
  - Dado que subo un archivo no válido, cuando envío el video, entonces recibo un error 400.
  - Dado que no estoy autenticado, cuando intento subir un video, entonces recibo un error 401.
- **Prioridad**: Alta
- **Vinculación**: Ver criterios en `ACCEPTANCE_CRITERIA.md`. 
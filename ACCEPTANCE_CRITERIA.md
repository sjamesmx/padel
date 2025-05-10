# Criterios de Aceptación para Endpoints Críticos de Padelyzer

## Autenticación

### /api/v1/auth/signup
- **Funcionalidad Esperada**:
  - Registrar un nuevo usuario con email y contraseña.
  - Almacenar el usuario en Firestore con email, contraseña hasheada, y un ID único.
- **Criterios**:
  - **200 OK**: Si el registro es exitoso, devuelve un mensaje de éxito (por ejemplo, `{"message": "User registered successfully"}`).
  - **400 Bad Request**: Si el email ya existe o faltan campos requeridos (email, contraseña).
  - **500 Internal Server Error**: Si hay un error al conectar con Firestore o al hashear la contraseña.
- **Manejo de Errores**:
  - Validar que el email sea único en Firestore antes de registrar.
  - Asegurar que la contraseña se hashee correctamente antes de almacenarla.

### /api/v1/auth/login
- **Funcionalidad Esperada**:
  - Autenticar un usuario con email y contraseña.
  - Generar y devolver un token JWT si las credenciales son válidas.
- **Criterios**:
  - **200 OK**: Si las credenciales son válidas, devuelve `{"access_token": "token", "token_type": "bearer"}`.
  - **401 Unauthorized**: Si el email no existe o la contraseña es incorrecta.
  - **500 Internal Server Error**: Si hay un error al conectar con Firestore o al generar el token.
- **Manejo de Errores**:
  - Validar las credenciales contra Firestore.
  - Asegurar que el token JWT se genere con un tiempo de expiración adecuado (por ejemplo, 1 hora).

## Gestión de Usuarios

### /api/v1/users/me
- **Funcionalidad Esperada**:
  - Devolver el perfil del usuario autenticado (email, nivel, posición preferida, etc.).
- **Criterios**:
  - **200 OK**: Devuelve los datos del usuario (por ejemplo, `{"email": "test@example.com", "level": "intermediate"}`).
  - **401 Unauthorized**: Si el usuario no está autenticado (falta o es inválido el token JWT).
  - **500 Internal Server Error**: Si hay un error al conectar con Firestore.
- **Manejo de Errores**:
  - Validar el token JWT para obtener el ID del usuario.
  - Consultar Firestore para obtener los datos del usuario.

### /api/v1/users/{user_id}/profile
- **Funcionalidad Esperada**:
  - Devolver el perfil público de un usuario específico (email, nivel, etc.).
- **Criterios**:
  - **200 OK**: Devuelve los datos públicos del usuario (por ejemplo, `{"email": "user@example.com", "level": "advanced"}`).
  - **404 Not Found**: Si el usuario no existe en Firestore.
  - **500 Internal Server Error**: Si hay un error al conectar con Firestore.
- **Manejo de Errores**:
  - Consultar Firestore para obtener los datos del usuario especificado.
  - Asegurar que solo se devuelvan datos públicos (por ejemplo, no incluir contraseña).

## Análisis de Videos

### /api/v1/video/upload
- **Funcionalidad Esperada**:
  - Permitir a los usuarios subir un video para análisis.
  - Almacenar el video en un sistema de almacenamiento (por ejemplo, Google Cloud Storage) y registrar metadata en Firestore.
- **Criterios**:
  - **200 OK**: Si la subida es exitosa, devuelve un mensaje de éxito (por ejemplo, `{"message": "Video uploaded successfully", "video_id": "123"}`).
  - **400 Bad Request**: Si el archivo no es un video válido o excede el tamaño máximo permitido.
  - **401 Unauthorized**: Si el usuario no está autenticado.
  - **500 Internal Server Error**: Si hay un error al conectar con el sistema de almacenamiento o Firestore.
- **Manejo de Errores**:
  - Validar el formato y tamaño del video antes de procesarlo.
  - Asegurar que el usuario esté autenticado.
  - Almacenar metadata en Firestore (por ejemplo, ID del video, ID del usuario, fecha de subida). 
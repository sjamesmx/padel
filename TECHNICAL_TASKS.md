# Desglose de Tareas Técnicas para Endpoints Críticos de Padelyzer

## Autenticación

### /api/v1/auth/signup
- **Tareas Técnicas**:
  1. **Validaciones de Entrada**:
     - Verificar que el email y la contraseña estén presentes en el body.
     - Validar el formato del email (usar una expresión regular o una biblioteca como `email-validator`).
     - Asegurar que la contraseña tenga al menos 8 caracteres.
  2. **Consulta a Firestore**:
     - Consultar Firestore para verificar que el email no exista en la colección `users`.
     - Usar `db.collection("users").where("email", "==", email).get()` para la consulta.
  3. **Hasheo de Contraseña**:
     - Usar `passlib` para hashear la contraseña con bcrypt.
  4. **Almacenamiento**:
     - Crear un documento en la colección `users` con `db.collection("users").add({"email": email, "password": hashed_password})`.
     - Registrar un ID único para el usuario.
  5. **Respuesta**:
     - Devolver `{"message": "User registered successfully"}` con código 200.
  6. **Manejo de Errores**:
     - Devolver 400 si el email ya existe o faltan campos.
     - Devolver 500 si hay un error al conectar con Firestore.

### /api/v1/auth/login
- **Tareas Técnicas**:
  1. **Validaciones de Entrada**:
     - Verificar que el email y la contraseña estén presentes en el body.
  2. **Consulta a Firestore**:
     - Buscar el usuario en la colección `users` con `db.collection("users").where("email", "==", email).get()`.
  3. **Verificación de Contraseña**:
     - Usar `passlib` para verificar la contraseña ingresada contra la hasheada.
  4. **Generación de Token JWT**:
     - Usar `python-jose` para generar un token JWT con el ID del usuario y un tiempo de expiración de 1 hora.
  5. **Respuesta**:
     - Devolver `{"access_token": token, "token_type": "bearer"}` con código 200.
  6. **Manejo de Errores**:
     - Devolver 401 si el email no existe o la contraseña es incorrecta.
     - Devolver 500 si hay un error al conectar con Firestore o al generar el token.

## Gestión de Usuarios

### /api/v1/users/me
- **Tareas Técnicas**:
  1. **Autenticación**:
     - Validar el token JWT usando `python-jose`.
     - Extraer el ID del usuario del token.
  2. **Consulta a Firestore**:
     - Obtener los datos del usuario con `db.collection("users").document(user_id).get()`.
  3. **Respuesta**:
     - Devolver los datos del usuario (por ejemplo, `{"email": "test@example.com", "level": "intermediate"}`) con código 200.
  4. **Manejo de Errores**:
     - Devolver 401 si el token es inválido o falta.
     - Devolver 500 si hay un error al conectar con Firestore.

### /api/v1/users/{user_id}/profile
- **Tareas Técnicas**:
  1. **Consulta a Firestore**:
     - Obtener los datos del usuario con `db.collection("users").document(user_id).get()`.
  2. **Filtrado de Datos**:
     - Asegurar que solo se devuelvan datos públicos (por ejemplo, email, nivel, pero no contraseña).
  3. **Respuesta**:
     - Devolver datos públicos (por ejemplo, `{"email": "user@example.com", "level": "advanced"}`) con código 200.
  4. **Manejo de Errores**:
     - Devolver 404 si el usuario no existe.
     - Devolver 500 si hay un error al conectar con Firestore.

## Análisis de Videos

### /api/v1/video/upload
- **Tareas Técnicas**:
  1. **Autenticación**:
     - Validar el token JWT para obtener el ID del usuario.
  2. **Validación del Archivo**:
     - Verificar que el archivo sea un video (por ejemplo, `video/mp4`).
     - Asegurar que el tamaño no exceda un límite (por ejemplo, 100 MB).
  3. **Almacenamiento**:
     - Subir el archivo a Google Cloud Storage usando `google-cloud-storage`.
     - Generar un ID único para el video.
  4. **Registro en Firestore**:
     - Almacenar metadata en la colección `videos` con `db.collection("videos").add({"user_id": user_id, "video_id": video_id, "status": "uploaded"})`.
  5. **Respuesta**:
     - Devolver `{"message": "Video uploaded successfully", "video_id": video_id}` con código 200.
  6. **Manejo de Errores**:
     - Devolver 400 si el archivo no es válido o excede el tamaño.
     - Devolver 401 si el usuario no está autenticado.
     - Devolver 500 si hay un error al subir a Google Cloud Storage o al conectar con Firestore. 
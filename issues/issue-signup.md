# Implementar /api/v1/auth/signup

## Historia de Usuario
Como usuario nuevo, quiero registrarme con mi email y contraseña, para poder acceder a las funcionalidades de Padelyzer.

### Criterios de Aceptación
- Dado que ingreso un email y contraseña válidos, cuando me registro, entonces recibo un mensaje de éxito.
- Dado que ingreso un email ya registrado, cuando intento registrarme, entonces recibo un error 400.

## Tareas Técnicas
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

## Prioridad
- Alta

## Vinculación
- Criterios completos en `ACCEPTANCE_CRITERIA.md`.

## Etiquetas Sugeridas
- priority:high
- feature:auth 
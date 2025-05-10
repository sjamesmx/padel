# Implementar /api/v1/auth/login

## Historia de Usuario
Como usuario registrado, quiero iniciar sesión con mi email y contraseña, para acceder a mi cuenta y usar la app.

### Criterios de Aceptación
- Dado que ingreso credenciales válidas, cuando inicio sesión, entonces recibo un token de acceso.
- Dado que ingreso credenciales incorrectas, cuando intento iniciar sesión, entonces recibo un error 401.

## Tareas Técnicas
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

## Prioridad
- Alta

## Vinculación
- Criterios completos en `ACCEPTANCE_CRITERIA.md`.

## Etiquetas Sugeridas
- priority:high
- feature:auth 
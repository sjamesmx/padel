# Implementar /api/v1/users/me

## Historia de Usuario
Como usuario autenticado, quiero ver mi perfil, para conocer mi información y nivel actual.

### Criterios de Aceptación
- Dado que estoy autenticado, cuando solicito mi perfil, entonces recibo mis datos (email, nivel, etc.).
- Dado que no estoy autenticado, cuando solicito mi perfil, entonces recibo un error 401.

## Tareas Técnicas
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

## Prioridad
- Alta

## Vinculación
- Criterios completos en `ACCEPTANCE_CRITERIA.md`.

## Etiquetas Sugeridas
- priority:high
- feature:users 
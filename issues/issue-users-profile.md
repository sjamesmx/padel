# Implementar /api/v1/users/{user_id}/profile

## Historia de Usuario
Como usuario, quiero ver el perfil público de otro usuario, para conocer su nivel y estadísticas.

### Criterios de Aceptación
- Dado un ID de usuario válido, cuando solicito su perfil, entonces recibo sus datos públicos.
- Dado un ID de usuario inexistente, cuando solicito su perfil, entonces recibo un error 404.

## Tareas Técnicas
1. **Consulta a Firestore**:
   - Obtener los datos del usuario con `db.collection("users").document(user_id).get()`.
2. **Filtrado de Datos**:
   - Asegurar que solo se devuelvan datos públicos (por ejemplo, email, nivel, pero no contraseña).
3. **Respuesta**:
   - Devolver datos públicos (por ejemplo, `{"email": "user@example.com", "level": "advanced"}`) con código 200.
4. **Manejo de Errores**:
   - Devolver 404 si el usuario no existe.
   - Devolver 500 si hay un error al conectar con Firestore.

## Prioridad
- Media

## Vinculación
- Criterios completos en `ACCEPTANCE_CRITERIA.md`.

## Etiquetas Sugeridas
- priority:medium
- feature:users 
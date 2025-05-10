# Implementar /api/v1/video/upload

## Historia de Usuario
Como usuario autenticado, quiero subir un video para análisis, para obtener estadísticas de mi juego.

### Criterios de Aceptación
- Dado que estoy autenticado y subo un video válido, cuando envío el video, entonces recibo un mensaje de éxito y el ID del video.
- Dado que subo un archivo no válido, cuando envío el video, entonces recibo un error 400.
- Dado que no estoy autenticado, cuando intento subir un video, entonces recibo un error 401.

## Tareas Técnicas
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

## Prioridad
- Alta

## Vinculación
- Criterios completos en `ACCEPTANCE_CRITERIA.md`.

## Etiquetas Sugeridas
- priority:high
- feature:video-analysis 
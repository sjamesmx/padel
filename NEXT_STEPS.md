# Próximos Pasos para Padelyzer

## Implementación de Lógica Real
- Sustituir los stubs por la lógica de negocio real para los endpoints:
  - /api/v1/users/{user_id}/profile
  - /api/v1/friends/request
  - /api/v1/social_wall
  - /api/v1/matchmaking/find_match
  - /api/v1/video/upload y análisis relacionados
  - /api/v1/auth/signup y /login
- Integrar Firestore para almacenamiento y recuperación de datos.

## Mejora de Mocks
- Revisar y mejorar los mocks para pruebas de integración y autenticación.
- Asegurar que los mocks reflejen casos de uso reales.

## Validación de Integración
- Validar la comunicación con Firestore y otros servicios externos.
- Probar flujos completos con datos reales.

## Optimización de Tests
- Eliminar duplicados en los tests.
- Mejorar la cobertura para incluir más casos de uso.
- Asegurar que los tests reflejen los flujos de usuario reales.

## Actualización de Documentación
- Actualizar la documentación técnica con la nueva arquitectura.
- Documentar los flujos de negocio implementados.
- Actualizar la guía de pruebas con los cambios realizados.

## Cobertura
- Revisar el reporte en htmlcov/index.html y priorizar la cobertura en áreas críticas (<80%).

## Instrucciones para el Equipo
- **Importar Issues**:
  - Los issues están en el directorio `issues/`.
  - Usar el script `import_issues.sh` si `gh` está instalado:
    ```bash
    ./import_issues.sh
    ```
  - Alternativamente, importar manualmente copiando el contenido de cada archivo a GitHub.
- **Asignación**:
  - Asignar los issues a los desarrolladores correspondientes según su área (autenticación, usuarios, análisis de videos).
- **Implementación**:
  - Seguir las tareas técnicas en `TECHNICAL_TASKS.md` y los criterios en `ACCEPTANCE_CRITERIA.md`.

## Áreas con Baja Cobertura
- Consultar `htmlcov/index.html` para identificar archivos con cobertura <80%.

## Resumen de Issues Generados

| Título                          | Endpoint                     | Prioridad | Etiquetas Sugeridas         |
|---------------------------------|------------------------------|-----------|----------------------------|
| Implementar /api/v1/auth/signup | /api/v1/auth/signup          | Alta      | priority:high, feature:auth |
| Implementar /api/v1/auth/login  | /api/v1/auth/login           | Alta      | priority:high, feature:auth |
| Implementar /api/v1/users/me    | /api/v1/users/me             | Alta      | priority:high, feature:users |
| Implementar /api/v1/users/{user_id}/profile | /api/v1/users/{user_id}/profile | Media     | priority:medium, feature:users |
| Implementar /api/v1/video/upload | /api/v1/video/upload         | Alta      | priority:high, feature:video-analysis |

**Notas**:
- Los issues están listos para ser importados a GitHub.
- Seguir las instrucciones en `docs/testing.md` para importar y asignar las tareas.
- Todos los issues han sido verificados y tienen el formato correcto.
- La documentación está actualizada con instrucciones claras para el equipo.

## Confirmación Final (10 mayo 2025)
- **Verificación de Archivos**:
  - Issues: Todos los archivos están presentes en `issues/` con formato correcto.
  - Script: `import_issues.sh` está presente y ejecutable.
  - Documentación: `docs/testing.md` y `NEXT_STEPS.md` incluyen instrucciones y checklist para el equipo.
  - Archivos de Referencia: `PRIORITIES.md`, `ACCEPTANCE_CRITERIA.md`, `TECHNICAL_TASKS.md`, `USER_STORIES.md` están presentes.
- **Estado Final**:
  - El proyecto Padelyzer está completamente preparado para la siguiente iteración.
  - El equipo puede importar los issues, asignarlos, y comenzar la implementación de la lógica real.

## Recordatorio: Revisar Cobertura de Tests
- **Acción**:
  - Antes de comenzar la implementación, revisar `htmlcov/index.html` para identificar áreas con baja cobertura (<80%).
  - Priorizar la mejora de la cobertura en las áreas críticas (autenticación, gestión de usuarios, análisis de videos).
- **Razón**:
  - Una buena cobertura asegura que los flujos principales estén bien probados antes de pasar a producción. 
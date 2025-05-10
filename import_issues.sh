#!/bin/bash

# Verificar si gh está instalado
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) no está instalado. Por favor, instálalo con 'brew install gh'."
    exit 1
fi

# Verificar si estamos autenticados con gh
if ! gh auth status &> /dev/null; then
    echo "Error: No estás autenticado con GitHub CLI. Por favor, autentícate con 'gh auth login'."
    exit 1
fi

# Importar issues con manejo de errores
echo "Importando issues a GitHub..."

gh issue create --title "Implementar /api/v1/auth/signup" --body-file issues/issue-signup.md --label priority:high --label feature:auth || { echo "Error al importar issue-signup.md"; exit 1; }
gh issue create --title "Implementar /api/v1/auth/login" --body-file issues/issue-login.md --label priority:high --label feature:auth || { echo "Error al importar issue-login.md"; exit 1; }
gh issue create --title "Implementar /api/v1/users/me" --body-file issues/issue-users-me.md --label priority:high --label feature:users || { echo "Error al importar issue-users-me.md"; exit 1; }
gh issue create --title "Implementar /api/v1/users/{user_id}/profile" --body-file issues/issue-users-profile.md --label priority:medium --label feature:users || { echo "Error al importar issue-users-profile.md"; exit 1; }
gh issue create --title "Implementar /api/v1/video/upload" --body-file issues/issue-video-upload.md --label priority:high --label feature:video-analysis || { echo "Error al importar issue-video-upload.md"; exit 1; }

echo "Éxito: Todos los issues han sido importados a GitHub." 
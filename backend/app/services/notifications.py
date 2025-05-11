from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.notifications = {}

    def create_notification(
        self,
        user_id: str,
        type: str,
        title: str,
        message: str,
        data: Dict[str, Any] = None
    ) -> None:
        """
        Crea una notificación para un usuario.
        En un entorno de producción, esto enviaría la notificación a través de Firebase Cloud Messaging.
        """
        if user_id not in self.notifications:
            self.notifications[user_id] = []
            
        notification = {
            "type": type,
            "title": title,
            "message": message,
            "data": data or {}
        }
        
        self.notifications[user_id].append(notification)
        logger.info(f"Notificación creada para usuario {user_id}: {notification}")

    def get_user_notifications(self, user_id: str) -> list:
        """
        Obtiene las notificaciones de un usuario.
        """
        return self.notifications.get(user_id, [])

    def clear_user_notifications(self, user_id: str) -> None:
        """
        Limpia las notificaciones de un usuario.
        """
        if user_id in self.notifications:
            self.notifications[user_id] = []

# Instancia global del servicio de notificaciones
notification_service = NotificationService() 
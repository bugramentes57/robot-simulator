from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RobotsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'robots'
    
    def ready(self):
        if settings.DEBUG:
            try:
                from .mqtt_client import MQTTClient
                mqtt_client = MQTTClient()
                mqtt_client.start()
                logger.info("MQTT/Kafka servisleri başlatıldı")
            except Exception as e:
                logger.error(f"Servis başlatma hatası: {str(e)}") 
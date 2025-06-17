import paho.mqtt.client as mqtt
import json
from django.conf import settings
import threading
from .kafka_client import KafkaClient
import logging

logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.kafka_client = KafkaClient()
        
    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"MQTT Broker'a bağlanıldı. Sonuç kodu: {rc}")
        client.subscribe(settings.MQTT_TOPIC)
        
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            # Kafka'ya gönder
            self.kafka_client.produce_message(payload)
        except Exception as e:
            logger.error(f"MQTT mesaj işleme hatası: {str(e)}")
            
    def start(self):
        try:
            # Kafka client'ı başlat
            self.kafka_client.start()
            
            # MQTT broker'a bağlan
            self.client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            
            # MQTT client loop'unu başlat
            mqtt_thread = threading.Thread(target=self.client.loop_forever, daemon=True)
            mqtt_thread.start()
            
            logger.info("MQTT ve Kafka istemcileri başlatıldı")
            
        except Exception as e:
            logger.error(f"MQTT/Kafka başlatma hatası: {str(e)}") 
from kafka import KafkaConsumer, KafkaProducer
import json
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from pymongo import MongoClient
import threading
import logging
from .alarm_manager import AlarmManager

logger = logging.getLogger(__name__)

class KafkaClient:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        self.consumer = KafkaConsumer(
            settings.KAFKA_ROBOT_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        self.channel_layer = get_channel_layer()
        self.alarm_manager = AlarmManager()
        
    def start(self):
        # Consumer thread'ini başlat
        consumer_thread = threading.Thread(target=self._consume, daemon=True)
        consumer_thread.start()
        logger.info("Kafka consumer başlatıldı")
        
    def _consume(self):
        try:
            for message in self.consumer:
                self._process_message(message.value)
        except Exception as e:
            logger.error(f"Kafka consumer hatası: {str(e)}")
            
    def _process_message(self, data):
        try:
            # MongoDB'ye kaydet
            mongo_client = MongoClient(settings.MONGODB_URI)
            db = mongo_client[settings.MONGODB_NAME]
            collection = db['robot_data']
            collection.insert_one(data)
            
            # Alarmları kontrol et
            alarms = self.alarm_manager.check_alarms(data)
            if alarms:
                # Alarm varsa WebSocket'e gönder
                for alarm in alarms:
                    async_to_sync(self.channel_layer.group_send)(
                        "robots",
                        {
                            "type": "alarm_message",
                            "message": alarm
                        }
                    )
                    logger.warning(f"Alarm tetiklendi: {alarm}")
            
            # Normal veri akışı
            if '_id' in data:
                del data['_id']
            
            async_to_sync(self.channel_layer.group_send)(
                "robots",
                {
                    "type": "robot_message",
                    "message": data
                }
            )
            
            mongo_client.close()
            logger.info(f"Kafka mesajı işlendi: {data}")
            
        except Exception as e:
            logger.error(f"Mesaj işleme hatası: {str(e)}")
            
    def produce_message(self, message):
        try:
            self.producer.send(settings.KAFKA_ROBOT_TOPIC, message)
            self.producer.flush()
            logger.info(f"Kafka'ya mesaj gönderildi: {message}")
        except Exception as e:
            logger.error(f"Mesaj gönderme hatası: {str(e)}") 
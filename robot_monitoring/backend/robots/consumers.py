from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging

logger = logging.getLogger(__name__)

class RobotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await self.channel_layer.group_add("robots", self.channel_name)
            await self.accept()
            logger.info("WebSocket bağlantısı başarıyla kuruldu")
        except Exception as e:
            logger.error(f"WebSocket bağlantı hatası: {str(e)}")
            await self.close(code=1011)
            return

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard("robots", self.channel_name)
            logger.info(f"WebSocket bağlantısı kapandı. Kod: {close_code}")
        except Exception as e:
            logger.error(f"WebSocket kapatma hatası: {str(e)}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            await self.channel_layer.group_send(
                "robots",
                {
                    'type': 'robot_message',
                    'message': message
                }
            )
        except Exception as e:
            logger.error(f"Mesaj alma hatası: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def robot_message(self, event):
        try:
            message = event['message']
            await self.send(text_data=json.dumps({
                'message': message
            }))
        except Exception as e:
            logger.error(f"Mesaj gönderme hatası: {str(e)}")

    async def alarm_message(self, event):
        try:
            message = event['message']
            await self.send(text_data=json.dumps({
                'type': 'alarm',
                'message': message
            }))
        except Exception as e:
            logger.error(f"Alarm mesajı gönderme hatası: {str(e)}") 
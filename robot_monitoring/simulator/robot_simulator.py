import random
from datetime import datetime
from pymongo import MongoClient
import time
import logging

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class RobotSimulator:
    def __init__(self, robot_id):
        self.robot_id = robot_id
        self.running = True
        try:
            self.client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
            self.db = self.client['robot_monitoring']
            # Bağlantıyı test et
            self.client.server_info()
            logging.info(f"Robot {robot_id} başlatıldı ve veritabanına bağlandı")
        except Exception as e:
            logging.error(f"Veritabanı bağlantı hatası ({robot_id}): {str(e)}")
            raise
        
        # Başlangıç değerleri - güvenli aralıklar
        self.temperature = self._get_safe_temperature()
        self.battery_level = random.uniform(80, 100)  # Başlangıçta yüksek şarj
        self.speed = 0  # Başlangıçta durgun
        self.position = self._get_initial_position()

    def _get_safe_temperature(self):
        """Güvenli sıcaklık aralığında değer üret"""
        return random.uniform(35, 45)  # Normal çalışma sıcaklığı

    def _get_initial_position(self):
        """Başlangıç pozisyonu belirle"""
        return {
            'x': round(random.uniform(0, 100), 2),
            'y': round(random.uniform(0, 100), 2),
            'z': round(random.uniform(0, 100), 2)
        }

    def _update_values(self):
        """Değerleri kademeli olarak güncelle"""
        # Sıcaklık değişimi (max ±1°C)
        self.temperature = max(20, min(90, self.temperature + random.uniform(-1, 1)))
        
        # Batarya seviyesi azalması (max %0.5)
        self.battery_level = max(0, self.battery_level - random.uniform(0, 0.5))
        
        # Hız değişimi (max ±2 m/s)
        self.speed = max(0, min(50, self.speed + random.uniform(-2, 2)))
        
        # Konum değişimi (hıza bağlı)
        movement = self.speed * 0.1  # Hız faktörü
        self.position = {
            'x': round(self.position['x'] + random.uniform(-movement, movement), 2),
            'y': round(self.position['y'] + random.uniform(-movement, movement), 2),
            'z': round(self.position['z'] + random.uniform(-movement, movement), 2)
        }

    def generate_data(self):
        """Veri üret ve kaydet"""
        try:
            self._update_values()
            
            data = {
                'robot_id': self.robot_id,
                'temperature': round(self.temperature, 2),
                'battery_level': round(self.battery_level, 2),
                'speed': round(self.speed, 2),
                'position': self.position,
                'motor_status': 'running',
                'timestamp': datetime.now()
            }
            
            # Alarm kontrolleri
            self._check_alarms(data)
            
            # Veriyi kaydet
            self.db.robot_data.insert_one(data)
            
        except Exception as e:
            logging.error(f"Veri üretme hatası ({self.robot_id}): {str(e)}")

    def _check_alarms(self, data):
        """Alarm durumlarını kontrol et"""
        try:
            # Yüksek sıcaklık alarmı
            if self.temperature > 75:
                self._create_alarm('high_temperature', 
                                 f'Yüksek sıcaklık: {round(self.temperature, 2)}°C')
            
            # Düşük batarya alarmı
            if self.battery_level < 15:
                self._create_alarm('low_battery',
                                 f'Düşük batarya: %{round(self.battery_level, 2)}')
                
            # Yüksek hız alarmı
            if self.speed > 45:
                self._create_alarm('high_speed',
                                 f'Yüksek hız: {round(self.speed, 2)} m/s')
                
        except Exception as e:
            logging.error(f"Alarm kontrolü hatası ({self.robot_id}): {str(e)}")

    def _create_alarm(self, alarm_type, message):
        """Alarm oluştur"""
        try:
            alarm_data = {
                'robot_id': self.robot_id,
                'alarm_type': alarm_type,
                'message': message,
                'temperature': round(self.temperature, 2),
                'battery_level': round(self.battery_level, 2),
                'timestamp': datetime.now()
            }
            self.db.alarms.insert_one(alarm_data)
        except Exception as e:
            logging.error(f"Alarm oluşturma hatası ({self.robot_id}): {str(e)}")

    def start_simulation(self):
        """Simülasyonu başlat"""
        logging.info(f"Robot {self.robot_id} simülasyonu başladı")
        while self.running:
            try:
                self.generate_data()
                time.sleep(2)
            except Exception as e:
                logging.error(f"Simülasyon döngüsü hatası ({self.robot_id}): {str(e)}")
                time.sleep(5)  # Hata durumunda biraz bekle

    def stop_simulation(self):
        """Simülasyonu durdur"""
        self.running = False
        try:
            self.client.close()
            logging.info(f"Robot {self.robot_id} simülasyonu durduruldu")
        except Exception as e:
            logging.error(f"Simülasyon durdurma hatası ({self.robot_id}): {str(e)}") 
from robot_simulator import RobotSimulator
import threading
from pymongo import MongoClient, errors
import time
from datetime import datetime
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SimulationManager:
    def __init__(self):
        try:
            self.client = MongoClient('mongodb://localhost:27017/', 
                                    serverSelectionTimeoutMS=5000,
                                    connectTimeoutMS=5000,
                                    socketTimeoutMS=5000)
            self.db = self.client['robot_monitoring']
            self.robots_collection = self.db['robots']
            self.active_simulations = {}
            self.lock = threading.Lock()
            logging.info("SimulationManager başlatıldı")
        except errors.ConnectionFailure as e:
            logging.error(f"MongoDB bağlantı hatası: {e}")
            raise

    def start_robot_simulation(self, robot_id):
        with self.lock:
            if robot_id not in self.active_simulations:
                try:
                    simulator = RobotSimulator(robot_id)
                    thread = threading.Thread(target=simulator.start_simulation)
                    thread.daemon = True
                    thread.start()
                    self.active_simulations[robot_id] = (simulator, thread)
                    logging.info(f"Robot {robot_id} simülasyonu başlatıldı")
                except Exception as e:
                    logging.error(f"Robot {robot_id} başlatma hatası: {e}")

    def stop_robot_simulation(self, robot_id):
        with self.lock:
            if robot_id in self.active_simulations:
                try:
                    simulator, _ = self.active_simulations[robot_id]
                    simulator.stop_simulation()
                    self._update_robot_state(robot_id, "idle")
                    del self.active_simulations[robot_id]
                    logging.info(f"Robot {robot_id} simülasyonu durduruldu")
                except Exception as e:
                    logging.error(f"Robot {robot_id} durdurma hatası: {e}")

    def _update_robot_state(self, robot_id, state):
        try:
            self.robots_collection.update_one(
                {"robot_id": robot_id},
                {"$set": {
                    "operation_state": state,
                    "last_active": datetime.now()
                }}
            )
        except Exception as e:
            logging.error(f"Robot {robot_id} durum güncelleme hatası: {e}")

    def update_simulations(self):
        while True:
            try:
                # Bulk işlem için robotları toplu al
                running_robots = list(self.robots_collection.find(
                    {
                        "status": "active",
                        "operation_state": "running"  # Sadece running durumundaki robotları al
                    },
                    {"robot_id": 1}
                ).limit(100))
                
                running_robot_ids = {robot['robot_id'] for robot in running_robots}
                current_robot_ids = set(self.active_simulations.keys())

                # Yeni robotları başlat
                for robot_id in running_robot_ids - current_robot_ids:
                    self.start_robot_simulation(robot_id)

                # Durması gereken robotları durdur (running olmayan veya inactive olan)
                for robot_id in current_robot_ids - running_robot_ids:
                    self.stop_robot_simulation(robot_id)
                    logging.info(f"Robot {robot_id} durumu değiştiği için simülasyon durduruldu")

                # Her 5 saniyede bir güncelle
                time.sleep(5)

            except errors.PyMongoError as e:
                logging.error(f"MongoDB hatası: {e}")
                time.sleep(5)
            except Exception as e:
                logging.error(f"Genel hata: {e}")
                time.sleep(5)

    def cleanup(self):
        logging.info("Simülasyon yöneticisi kapatılıyor...")
        with self.lock:
            for robot_id in list(self.active_simulations.keys()):
                self.stop_robot_simulation(robot_id)
        self.client.close()

if __name__ == "__main__":
    try:
        manager = SimulationManager()
        update_thread = threading.Thread(target=manager.update_simulations)
        update_thread.daemon = True
        update_thread.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Program kapatılıyor...")
        manager.cleanup()
    except Exception as e:
        logging.error(f"Beklenmeyen hata: {e}") 
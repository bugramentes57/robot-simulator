from pymongo import MongoClient
from datetime import datetime

def update_robot_states():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        # Tüm robotları güncelle
        result = db.robots.update_many(
            {},  # Tüm robotları seç
            {
                "$set": {
                    "operation_state": "running",  # Varsayılan olarak running
                    "last_active": datetime.now()
                }
            }
        )
        
        # Güncellenen robotları kontrol et
        robots = list(db.robots.find({}))
        print("\n=== GÜNCEL ROBOT DURUMLARI ===")
        for robot in robots:
            print(f"\nRobot ID: {robot['robot_id']}")
            print(f"Status: {robot.get('status', 'N/A')}")
            print(f"Operation State: {robot.get('operation_state', 'N/A')}")
            print("-" * 30)
        
        print(f"\nToplam {len(robots)} robot güncellendi")
        
    except Exception as e:
        print(f"Hata: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    update_robot_states() 
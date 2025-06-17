from pymongo import MongoClient
from datetime import datetime

def fix_robot_states():
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        # Tüm robotları güncelle
        result = db.robots.update_many(
            {},  # Tüm robotları seç
            {
                "$set": {
                    "status": "active",  # Varsayılan olarak active
                    "operation_state": "running"  # Varsayılan olarak running
                }
            }
        )
        
        # Güncellenen robotları kontrol et
        robots = list(db.robots.find({}))
        print("\n=== GÜNCEL ROBOT DURUMLARI ===")
        for robot in robots:
            print(f"\nRobot ID: {robot['robot_id']}")
            print(f"Status (active/inactive): {robot.get('status', 'N/A')}")
            print(f"Operation State (running/idle/error): {robot.get('operation_state', 'N/A')}")
            print("-" * 30)
        
        print(f"\nToplam {len(robots)} robot güncellendi")
        
    except Exception as e:
        print(f"Hata: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    fix_robot_states() 
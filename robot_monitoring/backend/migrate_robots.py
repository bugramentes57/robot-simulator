from pymongo import MongoClient
from datetime import datetime

def migrate_existing_robots():
    try:
        # MongoDB'ye bağlan
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        # Benzersiz robot ID'lerini robot_data koleksiyonundan al
        unique_robots = db.robot_data.distinct('robot_id')
        print(f"Bulunan benzersiz robot sayısı: {len(unique_robots)}")
        
        # Her robot için robots koleksiyonuna kayıt ekle
        for robot_id in unique_robots:
            # Robot zaten robots koleksiyonunda var mı kontrol et
            existing_robot = db.robots.find_one({"robot_id": robot_id})
            if not existing_robot:
                # Robotun son verisini al
                last_data = db.robot_data.find_one(
                    {"robot_id": robot_id},
                    sort=[("timestamp", -1)]
                )
                
                # Yeni robot kaydı oluştur
                new_robot = {
                    "robot_id": robot_id,
                    "description": f"Robot {robot_id}",
                    "status": "active",
                    "operation_state": "running",
                    "created_at": datetime.now(),
                    "last_active": datetime.now()
                }
                
                # Robots koleksiyonuna ekle
                db.robots.insert_one(new_robot)
                print(f"Robot {robot_id} başarıyla eklendi")
            else:
                print(f"Robot {robot_id} zaten mevcut")
        
        print("\nMigrasyon tamamlandı!")
        print(f"Toplam robot sayısı: {db.robots.count_documents({})}")
        print(f"Aktif robot sayısı: {db.robots.count_documents({'status': 'active'})}")
        
    except Exception as e:
        print(f"Hata: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    migrate_existing_robots() 
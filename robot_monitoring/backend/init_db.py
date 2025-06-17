from pymongo import MongoClient, IndexModel, ASCENDING
from datetime import datetime

def init_database():
    try:
        # MongoDB'ye bağlan
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        # Alarms koleksiyonunu oluştur
        if 'alarms' not in db.list_collection_names():
            alarms = db.create_collection('alarms')
            print("'alarms' koleksiyonu oluşturuldu")
            
            # İndeksleri oluştur
            alarms.create_index([("timestamp", ASCENDING)])
            alarms.create_index([("robot_id", ASCENDING)])
            print("Alarm indeksleri oluşturuldu")
        
        # Koleksiyonları oluştur
        if 'robots' not in db.list_collection_names():
            robots = db.create_collection('robots')
            print("'robots' koleksiyonu oluşturuldu")
            
            # İndeksleri oluştur
            robots.create_index([("robot_id", ASCENDING)], unique=True)
            print("İndeksler oluşturuldu")
            
            # Test robotu ekle
            test_robot = {
                "robot_id": "TEST_ROBOT",
                "description": "Test Robotu",
                "status": "active",
                "operation_state": "running",
                "created_at": datetime.now(),
                "last_active": datetime.now()
            }
            robots.insert_one(test_robot)
            print("Test robot eklendi")
        else:
            print("'robots' koleksiyonu zaten mevcut")
            
        if 'robot_data' not in db.list_collection_names():
            robot_data = db.create_collection('robot_data')
            print("'robot_data' koleksiyonu oluşturuldu")
            
            # İndeksleri oluştur
            robot_data.create_index([("timestamp", ASCENDING)])
            robot_data.create_index([("robot_id", ASCENDING)])
            print("İndeksler oluşturuldu")
        else:
            print("'robot_data' koleksiyonu zaten mevcut")
            
        print("\nVeritabanı başarıyla hazırlandı!")
        
    except Exception as e:
        print(f"Hata: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    init_database() 
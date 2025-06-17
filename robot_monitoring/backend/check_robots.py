from pymongo import MongoClient

def check_robots():
    try:
        # MongoDB'ye bağlan
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        # Aktif robotları listele
        print("\n=== AKTİF ROBOTLAR ===")
        active_robots = list(db.robots.find({"status": "active"}))
        for robot in active_robots:
            print(f"\nRobot ID: {robot['robot_id']}")
            print(f"Durum: {robot['status']}")
            print(f"Açıklama: {robot.get('description', 'Açıklama yok')}")
            print(f"Oluşturulma Tarihi: {robot['created_at']}")
            print(f"Son Aktif: {robot['last_active']}")
            print("-" * 30)
        
        # İnaktif robotları listele
        print("\n=== İNAKTİF ROBOTLAR ===")
        inactive_robots = list(db.robots.find({"status": "inactive"}))
        for robot in inactive_robots:
            print(f"\nRobot ID: {robot['robot_id']}")
            print(f"Durum: {robot['status']}")
            print(f"Açıklama: {robot.get('description', 'Açıklama yok')}")
            print(f"Oluşturulma Tarihi: {robot['created_at']}")
            print(f"Son Aktif: {robot['last_active']}")
            print("-" * 30)
        
        print(f"\nToplam robot sayısı: {len(active_robots) + len(inactive_robots)}")
        print(f"Aktif robot sayısı: {len(active_robots)}")
        print(f"İnaktif robot sayısı: {len(inactive_robots)}")
        
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_robots() 
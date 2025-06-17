from pymongo import MongoClient

try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['robot_monitoring']
    print("MongoDB'ye başarıyla bağlanıldı!")
    
    # Test verisi ekleyelim
    collection = db['robot_data']
    test_data = {"test": "veri"}
    collection.insert_one(test_data)
    print("Test verisi başarıyla eklendi!")
    
    client.close()
except Exception as e:
    print(f"Hata: {e}") 
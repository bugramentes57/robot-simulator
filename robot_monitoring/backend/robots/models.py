from pymongo import IndexModel, ASCENDING, DESCENDING, MongoClient
from django.conf import settings
from datetime import datetime

class MongoDBManager:
    def __init__(self):
        self.client = MongoClient(settings.MONGODB_URI)
        self.db = self.client[settings.MONGODB_NAME]
        self.collection = self.db['robot_data']
        self.robots_collection = self.db['robots']
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        # Performans için gerekli indeksler
        indexes = [
            IndexModel([("timestamp", DESCENDING)]),
            IndexModel([("robot_id", ASCENDING)]),
            IndexModel([("motor_status", ASCENDING)]),
            IndexModel([
                ("temperature", ASCENDING),
                ("battery_level", ASCENDING)
            ])
        ]
        self.collection.create_indexes(indexes) 
    
    def get_robot_stats(self, robot_id, time_range=None):
        pipeline = [
            {"$match": {"robot_id": robot_id}},
            {"$group": {
                "_id": None,
                "avg_temp": {"$avg": "$temperature"},
                "avg_battery": {"$avg": "$battery_level"},
                "error_count": {
                    "$sum": {"$cond": [{"$eq": ["$motor_status", "error"]}, 1, 0]}
                }
            }}
        ]
        return list(self.collection.aggregate(pipeline)) 
    
    def add_robot(self, robot_id, description=""):
        try:
            new_robot = {
                "robot_id": robot_id,
                "description": description,
                "status": "active",
                "operation_state": "running",  # Varsayılan olarak running
                "created_at": datetime.now(),
                "last_active": datetime.now()
            }
            result = self.robots_collection.insert_one(new_robot)
            return result
        except Exception as e:
            print(f"Robot eklenirken hata: {str(e)}")
            raise e
    
    def remove_robot(self, robot_id):
        try:
            # Robotu tamamen sil
            result = self.robots_collection.delete_one({"robot_id": robot_id})
            print(f"Robot silindi: {robot_id}")  # Debug için log
            return result
        except Exception as e:
            print(f"Robot silinirken hata: {str(e)}")  # Debug için log
            raise e
    
    def get_active_robots(self):
        return list(self.robots_collection.find(
            {"status": "active"}, 
            {"_id": 0}
        )) 
    
    def update_robot(self, robot_id, description):
        try:
            result = self.robots_collection.update_one(
                {"robot_id": robot_id},
                {
                    "$set": {
                        "description": description,
                        "last_active": datetime.now()
                    }
                }
            )
            return result
        except Exception as e:
            print(f"Robot güncellenirken hata: {str(e)}")
            raise e 
    
    def update_robot_status(self, robot_id, operation_state, description=""):
        try:
            update_data = {
                "operation_state": operation_state,
                "last_active": datetime.now()
            }
            if description:
                update_data["description"] = description

            result = self.robots_collection.update_one(
                {"robot_id": robot_id},
                {"$set": update_data}
            )
            
            # Robot data koleksiyonunda son veriyi güncelle
            if operation_state == "idle":
                self.collection.insert_one({
                    "robot_id": robot_id,
                    "temperature": 0,
                    "speed": 0,
                    "battery_level": 0,
                    "position": {"x": 0, "y": 0, "z": 0},
                    "motor_status": "idle",
                    "timestamp": datetime.now().isoformat()
                })
            
            return result
        except Exception as e:
            print(f"Robot durumu güncellenirken hata: {str(e)}")
            raise e 
    
    def get_latest_robot_data(self, robot_id):
        try:
            latest_data = self.collection.find_one(
                {"robot_id": robot_id},
                sort=[("timestamp", -1)]
            )
            if latest_data:
                latest_data["_id"] = str(latest_data["_id"])
                return latest_data
            return None
        except Exception as e:
            print(f"Robot verisi alınırken hata: {str(e)}")
            raise e 
    
    def update_robot_visibility(self, robot_id, status):
        """Robotun görünürlüğünü güncelle (active/inactive)"""
        try:
            if status not in ["active", "inactive"]:
                raise ValueError("Status sadece 'active' veya 'inactive' olabilir")

            result = self.robots_collection.update_one(
                {"robot_id": robot_id},
                {
                    "$set": {
                        "status": status,
                        "last_active": datetime.now()
                    }
                }
            )
            return result
        except Exception as e:
            print(f"Robot görünürlüğü güncellenirken hata: {str(e)}")
            raise e
    
    def update_robot_operation_state(self, robot_id, operation_state, description=""):
        """Robotun çalışma durumunu güncelle (running/idle/error/maintenance)"""
        try:
            if operation_state not in ["running", "idle", "error", "maintenance"]:
                raise ValueError("Operation state sadece 'running', 'idle', 'error' veya 'maintenance' olabilir")

            update_data = {
                "operation_state": operation_state,
                "last_active": datetime.now()
            }
            if description:
                update_data["description"] = description

            result = self.robots_collection.update_one(
                {"robot_id": robot_id},
                {"$set": update_data}
            )
            return result
        except Exception as e:
            print(f"Robot çalışma durumu güncellenirken hata: {str(e)}")
            raise e
    
    def get_all_robots(self):
        """Tüm robotları getir (active ve inactive)"""
        return list(self.robots_collection.find({}, {"_id": 0}))
    
    def get_active_robots(self):
        """Sadece active robotları getir"""
        return list(self.robots_collection.find(
            {"status": "active"}, 
            {"_id": 0}
        )) 
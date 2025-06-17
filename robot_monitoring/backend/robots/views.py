from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
from django.conf import settings
from datetime import datetime, timedelta
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import MongoDBManager
from bson.objectid import ObjectId

class RobotDataView(APIView):
    def get(self, request):
        try:
            # MongoDB bağlantısı
            client = MongoClient(settings.MONGODB_URI)
            db = client[settings.MONGODB_NAME]
            collection = db['robot_data']
            
            # Son 5 dakikalık verileri getir
            five_minutes_ago = datetime.now() - timedelta(minutes=5)
            
            # MongoDB'den verileri sorgula
            cursor = collection.find(
                {"timestamp": {"$gte": five_minutes_ago.isoformat()}},
                {"_id": 0}  # _id alanını hariç tut
            ).sort("timestamp", -1)
            
            # Cursor'ı listeye çevir
            data = list(cursor)
            
            client.close()
            return Response(data)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 

class TestPageView(TemplateView):
    template_name = "test.html" 

class RobotStatsView(APIView):
    def get(self, request):
        try:
            client = MongoClient(settings.MONGODB_URI)
            db = client[settings.MONGODB_NAME]
            
            # İstatistiksel veriler
            pipeline = [
                {
                    "$group": {
                        "_id": "$robot_id",
                        "avg_temp": {"$avg": "$temperature"},
                        "avg_speed": {"$avg": "$speed"},
                        "error_count": {
                            "$sum": {"$cond": [{"$ne": ["$error_code", None]}, 1, 0]}
                        }
                    }
                }
            ]
            
            stats = list(db.robot_data.aggregate(pipeline))
            return Response(stats)
        except Exception as e:
            return Response({"error": str(e)}, status=500) 

class RobotHistoryView(APIView):
    def get(self, request, robot_id):
        try:
            client = MongoClient(settings.MONGODB_URI)
            db = client[settings.MONGODB_NAME]
            
            # Tarih filtresi
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            query = {"robot_id": robot_id}
            if start_date and end_date:
                query["timestamp"] = {
                    "$gte": start_date,
                    "$lte": end_date
                }
            
            data = list(db.robot_data.find(query, {"_id": 0}))
            return Response(data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class AlarmHistoryView(APIView):
    def get(self, request):
        try:
            client = MongoClient(settings.MONGODB_URI)
            db = client[settings.MONGODB_NAME]
            
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"motor_status": "error"},
                            {"temperature": {"$gt": 75.0}},
                            {"battery_level": {"$lt": 15.0}}
                        ]
                    }
                },
                {
                    "$sort": {"timestamp": -1}
                }
            ]
            
            alarms = list(db.robot_data.aggregate(pipeline))
            return Response(alarms)
        except Exception as e:
            return Response({"error": str(e)}, status=500) 

@require_http_methods(["GET", "POST"])
def manage_robots(request):
    db = MongoDBManager()
    
    if request.method == "GET":
        robots = db.get_active_robots()
        return JsonResponse(robots, safe=False)
    
    elif request.method == "POST":
        data = json.loads(request.body)
        robot_id = data.get('robot_id')
        description = data.get('description', '')
        
        if not robot_id:
            return JsonResponse({"error": "Robot ID gerekli"}, status=400)
        
        db.add_robot(robot_id, description)
        return JsonResponse({"message": "Robot eklendi"}, status=201)

@require_http_methods(["DELETE"])
def remove_robot(request, robot_id):
    db = MongoDBManager()
    db.remove_robot(robot_id)
    return JsonResponse({"message": "Robot silindi"}) 

@require_http_methods(["GET"])
def get_robot_data(request):
    db = MongoDBManager()
    try:
        # Aktif robotların son verilerini getir
        active_robots = db.get_active_robots()
        robot_ids = [robot['robot_id'] for robot in active_robots]
        
        # Her aktif robot için son veriyi al
        latest_data = []
        for robot_id in robot_ids:
            data = db.collection.find_one(
                {"robot_id": robot_id},
                {"_id": 0},
                sort=[("timestamp", -1)]
            )
            if data:
                latest_data.append(data)
        
        return JsonResponse(latest_data, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_robot(request):
    try:
        data = json.loads(request.body)
        robot_id = data.get('robot_id')
        description = data.get('description', '')
        
        if not robot_id:
            return JsonResponse({"error": "Robot ID gerekli"}, status=400)
        
        db = MongoDBManager()
        result = db.add_robot(robot_id, description)
        
        print(f"Robot ekleme sonucu: {result}")  # Debug için log
        return JsonResponse({
            "message": "Robot başarıyla eklendi",
            "robot_id": robot_id
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({"error": "Geçersiz JSON formatı"}, status=400)
    except Exception as e:
        print(f"Robot eklenirken hata: {str(e)}")  # Debug için log
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def remove_robot(request, robot_id):
    db = MongoDBManager()
    try:
        db.remove_robot(robot_id)
        return JsonResponse({"message": "Robot başarıyla silindi"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@require_http_methods(["GET"])
def get_robots(request):
    try:
        db = MongoDBManager()
        robots = db.get_active_robots()
        return JsonResponse(robots, safe=False)
    except Exception as e:
        print(f"Robotlar alınırken hata: {str(e)}")  # Debug için log
        return JsonResponse({"error": str(e)}, status=500) 

@csrf_exempt
@require_http_methods(["PUT"])
def update_robot(request, robot_id):
    try:
        data = json.loads(request.body)
        description = data.get('description', '')
        
        db = MongoDBManager()
        result = db.update_robot(robot_id, description)
        
        return JsonResponse({
            "message": "Robot başarıyla güncellendi",
            "robot_id": robot_id
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@csrf_exempt
@require_http_methods(["PUT"])
def update_robot_status(request, robot_id):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        description = data.get('description', '')
        
        if not status:
            return JsonResponse({"error": "Status gerekli"}, status=400)
            
        if status not in ["running", "idle", "error", "maintenance"]:
            return JsonResponse({"error": "Geçersiz status değeri"}, status=400)
        
        db = MongoDBManager()
        result = db.update_robot_status(robot_id, status, description)
        
        return JsonResponse({
            "message": "Robot durumu başarıyla güncellendi",
            "robot_id": robot_id,
            "status": status
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@require_http_methods(["GET"])
def get_latest_robot_data(request, robot_id):
    try:
        db = MongoDBManager()
        latest_data = db.get_latest_robot_data(robot_id)
        if latest_data:
            return JsonResponse(latest_data, safe=False)
        return JsonResponse({}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@csrf_exempt
@require_http_methods(["PUT"])
def update_robot_visibility(request, robot_id):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        if not status:
            return JsonResponse({"error": "Status gerekli"}, status=400)
            
        if status not in ["active", "inactive"]:
            return JsonResponse({"error": "Status sadece 'active' veya 'inactive' olabilir"}, status=400)
        
        db = MongoDBManager()
        result = db.update_robot_visibility(robot_id, status)
        
        return JsonResponse({
            "message": "Robot görünürlüğü başarıyla güncellendi",
            "robot_id": robot_id,
            "status": status
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PUT"])
def update_robot_operation_state(request, robot_id):
    try:
        data = json.loads(request.body)
        operation_state = data.get('operation_state')
        description = data.get('description', '')
        
        if not operation_state:
            return JsonResponse({"error": "Operation state gerekli"}, status=400)
            
        if operation_state not in ["running", "idle", "error", "maintenance"]:
            return JsonResponse({"error": "Geçersiz operation state değeri"}, status=400)
        
        db = MongoDBManager()
        result = db.update_robot_operation_state(robot_id, operation_state, description)
        
        return JsonResponse({
            "message": "Robot çalışma durumu başarıyla güncellendi",
            "robot_id": robot_id,
            "operation_state": operation_state
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@require_http_methods(["GET"])
def get_all_robots(request):
    """Tüm robotları getir (active ve inactive)"""
    try:
        db = MongoDBManager()
        robots = db.get_all_robots()
        return JsonResponse(robots, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500) 

@require_http_methods(["GET"])
def get_alarms(request):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        # Son 24 saatteki aktif alarmları getir
        start_time = datetime.now() - timedelta(hours=24)
        
        alarms = list(db.alarms.find({
            "timestamp": {"$gte": start_time.isoformat()},
            "status": "active"
        }).sort("timestamp", -1))
        
        # ObjectId'leri string'e çevir
        for alarm in alarms:
            alarm['_id'] = str(alarm['_id'])
            
        return JsonResponse(alarms, safe=False)
        
    except Exception as e:
        print(f"Alarm getirme hatası: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        client.close()

@require_http_methods(["POST"])
def acknowledge_alarm(request, alarm_id):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        # Alarmı pasif yap
        result = db.alarms.update_one(
            {"_id": ObjectId(alarm_id)},
            {"$set": {"status": "acknowledged"}}
        )
        
        if result.modified_count > 0:
            return JsonResponse({"message": "Alarm onaylandı"})
        return JsonResponse({"error": "Alarm bulunamadı"}, status=404)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        client.close() 
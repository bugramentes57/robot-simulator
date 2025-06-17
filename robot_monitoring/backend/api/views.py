from datetime import datetime, timedelta
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
from bson import ObjectId

@api_view(['GET'])
def alarm_list(request):
    client = None
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        after_param = request.GET.get('after')
        
        query = {}
        if after_param:
            after_date = parse_datetime(after_param)
            if after_date:
                query['timestamp'] = {'$gte': after_date}
        
        alarms = list(db.alarms.find(
            query,
            {'_id': {'$toString': '$_id'}, 'robot_id': 1, 'timestamp': 1, 
             'alarm_type': 1, 'message': 1, 'temperature': 1, 'battery_level': 1}
        ).sort('timestamp', -1))
        
        return Response(alarms)
    except Exception as e:
        return Response({'error': str(e)}, status=500) 
    finally:
        if client:
            client.close()

@api_view(['GET'])
def paged_alarm_list(request):
    client = None
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        skip = (page - 1) * per_page
        
        alarms = list(db.alarms.find(
            {},
            {'_id': {'$toString': '$_id'}, 'robot_id': 1, 'timestamp': 1, 
             'alarm_type': 1, 'message': 1, 'temperature': 1, 'battery_level': 1}
        ).sort('timestamp', -1).skip(skip).limit(per_page))
        
        total_count = db.alarms.count_documents({})
        
        return Response({
            'alarms': alarms,
            'total': total_count,
            'page': page,
            'per_page': per_page
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500) 
    finally:
        if client:
            client.close() 

@api_view(['PUT'])
def update_robot_operation_state(request, robot_id):
    client = None
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        operation_state = request.data.get('operation_state')
        if not operation_state:
            return Response({'error': 'operation_state gerekli'}, status=400)
            
        if operation_state not in ["running", "idle", "error", "maintenance"]:
            return Response({'error': 'Geçersiz operation state değeri'}, status=400)
        
        result = db.robots.update_one(
            {"robot_id": robot_id},
            {
                "$set": {
                    "operation_state": operation_state,
                    "last_active": datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return Response({'error': 'Robot bulunamadı'}, status=404)
            
        return Response({'status': 'success'})
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    finally:
        if client:
            client.close()

@api_view(['GET', 'POST'])
def robot_list_create(request):
    client = None
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        if request.method == 'GET':
            robots = list(db.robots.find({}, {'_id': 0}))
            return Response(robots)

        if request.method == 'POST':
            robot_id = request.data.get('robot_id')
            description = request.data.get('description', '')
            
            if not robot_id:
                return Response({'error': 'robot_id gerekli'}, status=400)
                
            if db.robots.find_one({"robot_id": robot_id}):
                return Response({'error': 'Bu ID ile bir robot zaten var'}, status=400)
                
            new_robot = {
                "robot_id": robot_id,
                "description": description,
                "status": "active",
                "operation_state": "idle",
                "created_at": datetime.now(),
                "last_active": datetime.now()
            }
            
            result = db.robots.insert_one(new_robot)
            new_robot['_id'] = str(result.inserted_id)
            
            return Response(new_robot, status=201)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    finally:
        if client:
            client.close()

@api_view(['DELETE'])
def delete_robot(request, robot_id):
    client = None
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        # Önce robotun kendisini sil
        delete_result = db.robots.delete_one({"robot_id": robot_id})
        
        # Silinecek robot bulunamazsa 404 hatası döndür
        if delete_result.deleted_count == 0:
            return Response({'error': 'Robot bulunamadı'}, status=404)
        
        # Silme başarılı olduysa, ilişkili tüm verileri sil
        db.robot_data.delete_many({"robot_id": robot_id})
        db.alarms.delete_many({"robot_id": robot_id})
        
        return Response(status=204) # No Content
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    finally:
        if client:
            client.close()

@api_view(['GET'])
def get_latest_robot_data(request, robot_id):
    client = None
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['robot_monitoring']
        
        latest_data = db.robot_data.find_one(
            {'robot_id': robot_id},
            sort=[('timestamp', -1)],
            projection={'_id': False}
        )
        
        if not latest_data:
            return Response({'error': 'Veri bulunamadı'}, status=404)
            
        return Response(latest_data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)
    finally:
        if client:
            client.close() 
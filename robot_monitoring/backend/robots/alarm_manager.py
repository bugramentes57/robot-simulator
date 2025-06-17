import time

class AlarmManager:
    def __init__(self):
        self.rules = {
            'temperature': {
                'critical': {'max': 75.0, 'min': 60.0},
                'warning': {'max': 70.0, 'min': 65.0}
            },
            'battery_level': {
                'critical': {'min': 10.0},
                'warning': {'min': 20.0}
            },
            'motor_status': {
                'critical': ['error'],
                'warning': ['idle']
            }
        }
        self.alarm_history = []
        
    def check_alarms(self, data):
        robot_id = data['robot_id']
        alarms = []
        
        if data['motor_status'] == "error":
            alarms.append({
                'type': 'CRITICAL',
                'message': f"Motor arızası tespit edildi - Hata Kodu: {data.get('error_code', 'Bilinmiyor')}",
                'robot_id': robot_id
            })
        
        if data['temperature'] > self.rules['temperature']['critical']['max']:
            alarms.append({
                'type': 'CRITICAL',
                'message': f"Yüksek sıcaklık: {data['temperature']}°C (Limit: {self.rules['temperature']['critical']['max']}°C)",
                'robot_id': robot_id
            })
        
        if data['battery_level'] < 10:
            alarms.append({
                'type': 'CRITICAL',
                'message': f"Kritik batarya seviyesi: %{data['battery_level']} (Şarj edilmeli)",
                'robot_id': robot_id
            })
        elif data['battery_level'] < self.rules['battery_level']['warning']['min']:
            alarms.append({
                'type': 'WARNING',
                'message': f"Düşük batarya seviyesi: %{data['battery_level']} (Şarj önerilir)",
                'robot_id': robot_id
            })
        
        return alarms 
from django.urls import path
from . import views

urlpatterns = [
    path('api/robots/data/', views.get_robot_data, name='get_robot_data'),
    path('api/robots/add/', views.add_robot, name='add_robot'),
    path('api/robots/<str:robot_id>/', views.remove_robot, name='remove_robot'),
    path('api/robots/', views.get_robots, name='get_robots'),
    path('api/robots/<str:robot_id>/', views.update_robot, name='update_robot'),
    path('api/robots/<str:robot_id>/status/', views.update_robot_status, name='update_robot_status'),
    path('api/robot-data/<str:robot_id>/latest/', views.get_latest_robot_data, name='get_latest_robot_data'),
    path('api/robots/all/', views.get_all_robots, name='get_all_robots'),
    path('api/robots/<str:robot_id>/visibility/', views.update_robot_visibility, name='update_robot_visibility'),
    path('api/robots/<str:robot_id>/operation/', views.update_robot_operation_state, name='update_robot_operation_state'),
    path('api/alarms/', views.get_alarms, name='get_alarms'),
] 
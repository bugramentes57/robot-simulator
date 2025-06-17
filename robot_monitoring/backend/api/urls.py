from django.urls import path
from . import views

urlpatterns = [
    # More specific robot URLs come first to ensure correct routing
    path('robots/<str:robot_id>/operation/', views.update_robot_operation_state, name='update-robot-operation-state'),
    path('robots/<str:robot_id>/', views.delete_robot, name='robot-delete'),
    
    # General robot URL for listing and creation
    path('robots/', views.robot_list_create, name='robot-list-create'),
    
    # Other data-related URLs
    path('robot-data/<str:robot_id>/latest/', views.get_latest_robot_data, name='get-latest-robot-data'),
    path('alarms/paged/', views.paged_alarm_list, name='paged-alarm-list'),
] 
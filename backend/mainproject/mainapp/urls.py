
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_with_ai_view, name='upload_with_ai'),
    path('apply/', views.apply_selected_operations_view, name='apply_selected_operations'),
    path('download/<str:filename>/', views.download_view, name='download_file'),
    path('preprocess/', views.preprocess_view, name='preprocess'),
   
    path('health/', views.health_check_view, name='health_check'),
    path('analyze-with-mode/', views.analyze_with_mode_view, name='analyze_with_mode'),
]
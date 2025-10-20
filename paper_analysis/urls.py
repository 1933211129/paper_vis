"""
paper_analysis应用的URL配置
"""

from django.urls import path
from . import views

app_name = 'paper_analysis'

urlpatterns = [
    # 分析相关API
    path('start-analysis/', views.start_analysis, name='start_analysis'),
    # PDF文件上传相关API
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('folders/', views.list_uploaded_folders, name='list_folders'),
    
    
    # 其他API - 使用更具体的模式
    path('folders/<str:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    
    # 可视化数据API
    path('visualization-data/<str:folder_id>/image/<str:figure_id>', views.get_visualization_image, name='get_visualization_image'),
    path('visualization-data/<str:folder_id>/', views.get_visualization_data, name='get_visualization_data'),
]


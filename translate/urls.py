from django.urls import path
from translate import views

app_name = 'translate'
urlpatterns = [
    # 書籍
    path('file/', views.translator, name='translator'),   # Translation view
    path('file/tra/<int:file_id>/', views.file_tra, name='file_tra'),  # Translate
    path('file/del/<int:file_id>/', views.file_del, name='file_del'),   # Delete
    path('get_file_list_data/', views.get_file_list_data),
    path('upload_file/', views.upload_file),
    path('translate_text/', views.translate_text),
    path('download/<int:file_id>', views.download),
]

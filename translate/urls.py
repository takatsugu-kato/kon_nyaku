from django.urls import path
from translate import views

app_name = 'translate'
urlpatterns = [
    # 書籍
    path('file/', views.file_list, name='file_list'),   # 一覧
    path('file/tra/<int:file_id>/', views.file_tra, name='file_tra'),  # 翻訳
    path('file/del/<int:file_id>/', views.file_del, name='file_del'),   # 削除
    path('get_file_list_data/', views.get_file_list_data),
]

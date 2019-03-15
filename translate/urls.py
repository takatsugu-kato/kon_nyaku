from django.urls import path
from translate import views

app_name = 'translate'
urlpatterns = [
    # 書籍
    path('file/', views.file_list, name='file_list'),   # 一覧
    path('file/add/', views.file_add, name='file_add'),  # 登録
    path('file/del/<int:file_id>/', views.file_del, name='file_del'),   # 削除
]

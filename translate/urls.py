from django.urls import path
from translate import views
# from translate import cron #only use for debug

app_name = 'translate'
urlpatterns = [
    path('', views.translate_index, name='translate_index'), # Index
    path('translator/', views.translator, name='translator'),   # Translation view
    path('help/', views.help, name='help'),   # Help view
    path('translator/tra/<int:file_id>/', views.file_tra, name='file_tra'),  # Translate
    path('translator/del/<int:file_id>/', views.file_del, name='file_del'),   # Delete
    path('get_file_list_data/', views.get_file_list_data),
    path('upload_file/', views.upload_file),
    path('translate_text/', views.translate_text),
    path('file_download/<int:file_id>', views.file_download),
    # path('set_delete_flag_for_debug/', cron.set_delete_flag_for_debug), #only use for debug
]

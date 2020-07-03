"""
urls
"""
from django.urls import path
from translate import views
# from translate import cron #only use for debug

app_name = 'translate'
urlpatterns = [
    path('', views.translate_index, name='translate_index'), # Index
    path('translator/', views.translator, name='translator'),   # Translation view
    path('glossary/', views.glossary, name='glossary'),   # Glossary view
    path('help/', views.help_index, name='help'),   # Help view
    path('translator/tra/<int:file_id>/', views.file_tra, name='file_tra'),  # Translate
    path('translator/del/<int:file_id>/', views.file_del, name='file_del'),   # Delete
    path('get_file_list_data/', views.get_file_list_data),
    path('get_glossary_list_data_for_glossary_view/', views.get_glossary_list_data_for_glossary_view),
    path('get_glossary_list_data_for_translator_view/', views.get_glossary_list_data_for_translator_view),
    path('glossary/del/<int:glossary_id>/', views.glossary_del, name='glossary_del'),
    path('upload_file/', views.upload_file),
    path('upload_glossary/', views.upload_glossary),
    path('translate_text/', views.translate_text),
    path('file_download/<int:file_id>', views.file_download),
    # path('set_delete_flag_for_debug/', cron.set_delete_flag_for_debug), #only use for debug
]

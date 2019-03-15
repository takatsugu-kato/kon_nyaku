from django.contrib import admin
from translate.models import File

# Register your models here.
class FileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_date', 'modified_date',)  # 一覧に出したい項目
    list_display_links = ('id', 'name',)  # 修正リンクでクリックできる項目
admin.site.register(File, FileAdmin)

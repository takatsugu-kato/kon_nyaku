from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from translate.models import File
from translate.forms import DocumentForm

# Create your views here.
def file_list(request):
    """ファイルの一覧"""

    if request.FILES:
        form = DocumentForm(request.POST, request.FILES)
        form.instance.name = "grjkgorko"
        if form.is_valid():
            form.save()
    else:
        form = DocumentForm()
    files = File.objects.all().order_by('id')
    return render(request,
                  'translate/file_list.html',     # 使用するテンプレート
                  {'files': files,
                   'form': form},
                 )


def file_add(request, file_id=None):
    """ファイルの登録"""
    return HttpResponse('ファイルの登録')


def file_del(request, file_id):
    """ファイルの削除"""
    file = get_object_or_404(File, pk=file_id)
    file.delete()
    return redirect('file:file_list')

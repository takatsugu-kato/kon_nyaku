from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from background_task import background

from translate.models import File
from translate.forms import DocumentForm
from lib.okapi import Okapi
from lib.xlf import Xlf

# Create your views here.
def file_list(request):
    """ファイルの一覧"""
    default_form_value = {'target_lang':'ja'}
    if request.FILES:
        form = DocumentForm(request.POST, request.FILES, initial=default_form_value)
        if form.is_valid():
            form.save()
    else:
        form = DocumentForm(initial=default_form_value)
    # form['initial'] = {'target_lang':'ja'}
    files = File.objects.all().order_by('id')
    return render(request,
                  'translate/file_list.html',     # 使用するテンプレート
                  {'files': files,
                   'form': form},
                 )


def file_tra(request, file_id):
    """ファイルの翻訳"""
    translate_xlf(file_id)
    return HttpResponse('ファイルの翻訳' + str(file_id))


def file_del(request, file_id):
    """ファイルの削除"""
    file = get_object_or_404(File, pk=file_id)
    file.delete()
    return HttpResponseRedirect('/translate/file')

@background(queue='translate_queue', schedule=5)
def translate_xlf(file_id):
    """
    Translate xlf file
    """
    file = File.objects.get(pk=file_id)
    to_trans_file = str(file.document)

    print("Translating {0}".format(to_trans_file))

    source_lang = file.source_lang
    target_lang = file.target_lang
    model = "nmt"
    # to_trans_file = "./sample_file/test.docx"

    okapi_obj = Okapi(source_lang, target_lang)
    okapi_obj.create_xlf(to_trans_file)


    xlf_obj = Xlf(to_trans_file + ".xlf")
    xlf_obj.translate(model, delete_format_tag=False, pseudo=True)
    xlf_obj.back_to_xlf()

    okapi_obj.create_transled_file(to_trans_file + ".xlf")

    file.status = 100
    file.save()

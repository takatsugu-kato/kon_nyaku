import json
import mimetypes
import os
import io
import urllib.parse
import pytz
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from background_task import background
from django.core import serializers
from django.utils import dateformat

from translate.models import File
from translate.forms import DocumentForm
from lib.okapi import Okapi
from lib.xlf import Xlf

from .consts import STATUS

# Create your views here.
def file_list(request):
    """ファイルの一覧"""
    default_form_value = {'target_lang':'ja'}
    form = DocumentForm(initial=default_form_value)

    return render(request,
                  'translate/file_list.html',     # 使用するテンプレート
                  {'file_list_data': create_file_list_tbody_html(request),
                   'form': form,
                   'STATUS': STATUS},
                 )

def upload_file(request):
    """ファイルのアップロード"""
    default_form_value = {'target_lang':'ja'}
    if request.FILES:
        #Set the session key to POST
        copied_post_data = request.POST.copy()
        copied_post_data['file_session_key'] = request.session.session_key

        form = DocumentForm(copied_post_data, request.FILES, initial=default_form_value)
        if form.is_valid():
            form.save()
    return HttpResponse("upload done")

def file_tra(request, file_id):
    """ファイルの翻訳"""
    file = File.objects.get(pk=file_id)
    file.status = 1
    file.save()
    translate_xlf(file_id)
    return HttpResponse()


def file_del(request, file_id):
    """ファイルの削除"""
    delete_files(file_id)
    return HttpResponse()

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
    translation_model = "nmt"
    # to_trans_file = "./sample_file/test.docx"

    okapi_obj = Okapi(source_lang, target_lang)
    okapi_obj.create_xlf(to_trans_file)


    xlf_obj = Xlf(to_trans_file + ".xlf")
    xlf_obj.translate(translation_model, delete_format_tag=False, pseudo=True, django_file_obj=file)
    xlf_obj.back_to_xlf()

    okapi_obj.create_transled_file(to_trans_file + ".xlf")

    file.status = 2
    file.save()

def get_file_list_data(request):
    return JsonResponse(create_file_list_tbody_html(request))

def create_file_list_tbody_html(request):

    jst = pytz.timezone('Asia/Tokyo')

    files = File.objects.filter(file_session_key=request.session.session_key).order_by('id').reverse()
    html = ""
    done_flag = 1
    for file in files:
        created_date = file.created_date.astimezone(jst)
        created_date_str = created_date.strftime('%Y-%m-%d %H:%M')
        modified_date = file.modified_date.astimezone(jst)
        modified_date_str = modified_date.strftime('%Y-%m-%d %H:%M')

        translate_button_html = '<a href="tra/' + str(file.id) + '" class="tra btn btn-outline-primary btn-sm">翻訳</a>\n'
        if file.status == 1:
            done_flag = 0
        if file.progress == 100:
            progress_html = '<div class="progress"><div class="progress-bar progress-bar-striped bg-success" role="progressbar" style="width:100%">'\
                            '<a class="progress_a" href="/translate/download/' + str(file.id) + '" download>download</a></div></div>'
            translate_button_html = '<a href="tra/' + str(file.id) + '" class="tra btn btn-outline-primary btn-sm disabled">翻訳</a>\n'
        elif file.status == 0:
            progress_html = "not start"
        else:
            progress_html = '<div class="progress"><div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: '+str(file.progress)+'%"></div></div>'

        html = html + '        <tr>\n'\
            '          <th scope="row">' + str(file.id) + '</th>\n'\
            '          <td>' + file.name + '</td>\n'\
            '          <td>' + file.source_lang + '</td>\n'\
            '          <td>' + file.target_lang + '</td>\n'\
            '          <td>' + progress_html + '</td>\n'\
            '          <td>' + created_date_str + '</td>\n'\
            '          <td>' + modified_date_str + '</td>\n'\
            '          <td>\n'\
            '            ' + translate_button_html + \
            '            <button class="btn btn-outline-danger btn-sm del_confirm" data-toggle="modal" data-target="#deleteModal" data-pk="' + str(file.id) + '">削除</button>\n'\
            '          </td>\n'\
            '        </tr>\n'
    return_json = {"html": html, "done_flag": done_flag}
    return return_json

def download(request, file_id):
    file = File.objects.get(pk=file_id)

    root, ext = os.path.splitext(str(file.document))
    translated_file_path = root + ".out" + ext

    with open(translated_file_path, 'rb') as in_file:
        binary = io.BytesIO(in_file.read())

    mime = mimetypes.guess_type(translated_file_path)
    response = HttpResponse(binary, content_type=mime[0])
    response["Content-Disposition"] = 'filename=' + urllib.parse.quote(str(file))
    return response

def delete_files(file_id):
    file = get_object_or_404(File, pk=file_id)

    root, ext = os.path.splitext(str(file.document))
    translated_file_path = root + ".out" + ext
    xlf_file_path = str(file.document) + ".xlf"

    if os.path.exists(translated_file_path):
        os.remove(translated_file_path)
    if os.path.exists(xlf_file_path):
        os.remove(xlf_file_path)
    if os.path.exists(str(file.document)):
        os.remove(str(file.document))
    file.delete()

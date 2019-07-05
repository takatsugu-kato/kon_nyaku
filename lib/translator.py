"""
This modules is related to translator
"""
import os
import pytz
from django.shortcuts import get_object_or_404

from background_task import background
from google.cloud import translate
from translate.models import File
from lib.okapi import Okapi
from lib.xlf import Xlf
from .xlf import PseudoClient

def translate_text_by_google(string, source_language, target_language, model="nmt", pseudo=False):
    """Translate using google translate

    Args:
        string (str): to transalte string
        source_language (str): source language code
        target_language (str): target language code
        model (str, optional): language model. Defaults to "nmt".
        pseudo (bool, optional): pseudo flag. Defaults to False.

    Returns:
        str: translated string
    """
    if pseudo:
        translate_client = PseudoClient()
    else:
        translate_client = translate.Client()
    translation = translate_client.translate(
        lf2br(string),
        model=model,
        source_language=source_language,
        target_language=target_language)
    translated_text = translation['translatedText']
    return translated_text

def lf2br(string):
    """change lf to br

    Args:
        string (str): to change string

    Returns:
        str: changed string
    """
    string_new = '<br>'.join(string.splitlines())
    return string_new

@background(queue='translate_queue', schedule=5)
def translate_file(file_id):
    """translate file

    Args:
        file_id (int): to translate file id
    """
    file = File.objects.get(pk=file_id)
    to_trans_file = str(file.document)

    print("Translating {0}".format(to_trans_file))

    source_lang = file.source_lang
    target_lang = file.target_lang
    translation_model = "nmt"
    # to_trans_file = "./sample_file/test.docx"

    okapi_obj = Okapi(source_lang, target_lang)
    res = okapi_obj.create_xlf(to_trans_file)
    if not res:
        file.status = 101
        file.save()
        return

    xlf_obj = Xlf(to_trans_file + ".xlf")
    xlf_obj.translate(translation_model, delete_format_tag=file.delete_format_tag, pseudo=False, django_file_obj=file)

    res = xlf_obj.back_to_xlf()
    if not res:
        file.status = 201
        file.save()
        return

    res = okapi_obj.create_transled_file(to_trans_file + ".xlf")
    if not res:
        file.status = 102
        file.save()
        return
    file.chara_count = xlf_obj.charactor_count
    file.status = 2
    file.save()

def get_ip_address(request):
    """Get client ip address

    Args:
        request (obj): http request

    Returns:
        str: client ip address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    return ip_address

def create_file_list_tbody_html(request, STATUS):
    """Create file list as html

    Args:
        request (obj): http request
        STATUS (cons): status cons

    Returns:
        json: html and done flag
    """
    jst = pytz.timezone('Asia/Tokyo')

    files = File.objects.filter(file_session_key=request.session.session_key).filter(delete_flag=False).order_by('id').reverse()
    html = ""
    done_flag = 1
    for file in files:
        created_date = file.created_date.astimezone(jst)
        created_date_str = created_date.strftime('%Y-%m-%d %H:%M')

        translate_button_html = '<a href="tra/' + str(file.id) + '" class="tra btn btn-primary btn-mergen-sm disabled"><i class="fas fa-language"></i></a>\n'
        delete_button_html = '<a href="" class="btn btn-danger btn-mergen-sm del_confirm" data-toggle="modal" data-target="#deleteModal" data-pk="' + str(file.id) + '"><i class="fas fa-trash-alt"></i></a>\n'

        #set done flag
        if file.status == 1:
            done_flag = 0
            delete_button_html = '<a href="" class="btn btn-danger btn-mergen-sm del_confirm disabled" data-toggle="modal" data-target="#deleteModal" data-pk="' + str(file.id) + '"><i class="fas fa-trash-alt"></i></a>\n'

        if file.progress == 100:
            progress_html = '<div class="progress"><div class="progress-bar progress-bar-striped bg-success" role="progressbar" style="width:100%">'\
                            '<a class="progress_a" href="/translate/file_download/' + str(file.id) + '" download><i class="fas fa-download"></i> Download</a></div></div>'
        elif file.status == 0:
            progress_html = STATUS[file.status]
            translate_button_html = '<a href="tra/' + str(file.id) + '" class="tra btn btn-primary btn-mergen-sm"><i class="fas fa-language"></i></a>\n'
        elif file.status > 100:
            progress_html = '<div class="progress"><div class="progress-bar progress-bar-striped bg-danger" role="progressbar" style="width: 100%">' + STATUS[file.status] + '</div></div>'
        else:
            progress_html = '<div class="progress"><div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: '+str(file.progress)+'%"></div></div>'

        if file.delete_format_tag:
            delete_format_tag_html = '<i class="fas fa-eraser"></i>'
        else:
            delete_format_tag_html = ""
        html = html + '        <tr>\n'\
            '          <th scope="row">' + str(file.id) + '</th>\n'\
            '          <td>' + file.name + '</td>\n'\
            '          <td>' + file.source_lang + '</td>\n'\
            '          <td>' + file.target_lang + '</td>\n'\
            '          <td class="text-center">' + delete_format_tag_html + '</td>\n'\
            '          <td>' + progress_html + '</td>\n'\
            '          <td>' + created_date_str + '</td>\n'\
            '          <td class="text-center">\n'\
            '            ' + translate_button_html + \
            '            ' + delete_button_html + \
            '          </td>\n'\
            '        </tr>\n'
    return_json = {"html": html, "done_flag": done_flag}
    return return_json

def set_delete_flag(file_id):
    """Delete file

    Args:
        file_id (int): to delete file id
    """
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
    file.delete_flag = True
    file.save()
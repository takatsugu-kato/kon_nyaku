"""
This modules is related to translator
"""
import os
import html
import pytz
from django.shortcuts import get_object_or_404
from django.conf import settings

from background_task import background
from google.cloud import translate
from translate.models import File
from translate.models import Glossary
from lib.okapi import Okapi
from lib.xlf import Xlf
from .xlf import PseudoClient
from MasuDa import Converter

def translate_text_by_google(string, source_language, target_language, jotai=False, pseudo=False):
    """Translate using google translate

    Args:
        string (str): to transalte string
        source_language (str): source language code
        target_language (str): target language code
        jotai (bool, optional): Change to jotai for japanese text
        model (str, optional): language model. Defaults to "nmt".
        pseudo (bool, optional): pseudo flag. Defaults to False.

    Returns:
        str: translated string
    """
    if pseudo:
        translate_client = PseudoClient()
    else:
        translate_client = translate.TranslationServiceClient()

    parent = translate_client.location_path(
        os.getenv("GOOGLE_PROJECT_ID"),
        os.getenv("GOOGLE_LOCATION")
    )

    translation = translate_client.translate_text(
        contents=[lf2br(string)],
        parent=parent,
        mime_type='text/html',
        source_language_code=source_language,
        target_language_code=target_language)
    print(translation)
    translated_text = translation.translations[0].translated_text
    if jotai:
        masuda = Converter()
        translated_text = masuda.keitai2jotai(translated_text)
    return br2lf(html.unescape(translated_text))

def lf2br(string):
    """change lf to br

    Args:
        string (str): to change string

    Returns:
        str: changed string
    """
    string_new = '<br>'.join(string.splitlines())
    return string_new

def br2lf(string):
    """change br to lf

    Args:
        string (str): to change string

    Returns:
        str: changed string
    """
    string_new = string.replace('<br>', '\n')
    return string_new

@background(queue='translate_queue', schedule=5)
def translate_file(file_id):
    """translate file

    Args:
        file_id (int): to translate file id
    """
    file = File.objects.get(pk=file_id)
    to_trans_file = str(file.document)
    to_trans_file = os.path.join(settings.MEDIA_ROOT, to_trans_file)

    print("Translating {0}".format(to_trans_file))

    source_lang = file.source_lang
    target_lang = file.target_lang
    # to_trans_file = "./sample_file/test.docx"

    okapi_obj = Okapi(source_lang, target_lang)
    res = okapi_obj.create_xlf(to_trans_file)
    if not res:
        file.status = 101
        file.save()
        return

    xlf_obj = Xlf(to_trans_file + ".xlf")
    xlf_obj.translate(delete_format_tag=file.delete_format_tag, change_to_jotai=file.change_to_jotai, pseudo=False, django_file_obj=file)

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

def create_glossary_list_tbody_html(request, status_cons):
    """Create glossary list as html

    Args:
        request (obj): http request
        STATUS (cons): status cons

    Returns:
        json: html
    """
    jst = pytz.timezone('Asia/Tokyo')

    glossaries = Glossary.objects.all().order_by('id').reverse()
    html_string = ""
    for glossary in glossaries:
        created_date = glossary.created_date.astimezone(jst)
        created_date_str = created_date.strftime('%Y-%m-%d %H:%M')

        delete_button_html = ('<span data-toggle="tooltip" data-placement="top" title="Delete">'
                              '<a href="" class="btn btn-danger btn-mergen-sm del_confirm" data-toggle="modal"'
                              ' data-target="#deleteModal" data-pk="' + str(glossary.id) + '">'
                              '<i class="fas fa-trash-alt"></i></a></span>\n')


        html_string = html_string + '        <tr>\n'\
            '          <th scope="row">' + str(glossary.id) + '</th>\n'\
            '          <td>' + glossary.name + '</td>\n'\
            '          <td>' + glossary.source_lang + '</td>\n'\
            '          <td>' + glossary.target_lang + '</td>\n'\
            '          <td>' + status_cons[glossary.status] + '</td>\n'\
            '          <td>' + created_date_str + '</td>\n'\
            '          <td class="text-center">' + delete_button_html + '</td>\n'\
            '        </tr>\n'
    return_json = {"html": html_string}
    return return_json

def create_file_list_tbody_html(request, status_cons):
    """Create file list as html

    Args:
        request (obj): http request
        STATUS (cons): status cons

    Returns:
        json: html and done flag
    """
    jst = pytz.timezone('Asia/Tokyo')

    files = File.objects.filter(file_session_key=request.session.session_key).filter(delete_flag=False).order_by('id').reverse()
    html_string = ""
    done_flag = 1
    for file in files:
        created_date = file.created_date.astimezone(jst)
        created_date_str = created_date.strftime('%Y-%m-%d %H:%M')

        translate_button_html = ('<a href="tra/' + str(file.id) + '" class="tra btn btn-primary btn-mergen-sm disabled">'
                                 '<i class="fas fa-language"></i></a>\n')
        delete_button_html = ('<span data-toggle="tooltip" data-placement="top" title="Delete">'
                              '<a href="" class="btn btn-danger btn-mergen-sm del_confirm" data-toggle="modal"'
                              ' data-target="#deleteModal" data-pk="' + str(file.id) + '">'
                              '<i class="fas fa-trash-alt"></i></a></span>\n')

        #set done flag
        if file.status == 1:
            done_flag = 0
            delete_button_html = ('<a href="" class="btn btn-danger btn-mergen-sm del_confirm disabled"'
                                  ' data-toggle="modal" data-target="#deleteModal" data-pk="' + str(file.id) + '">'
                                  '<i class="fas fa-trash-alt"></i></a>\n')

        if file.progress == 100:
            progress_html = ('<div class="progress"><div class="progress-bar progress-bar-striped bg-success" role="progressbar" style="width:100%">'
                             '<a class="progress_a download_confirm" href="" data-toggle="modal"'
                             'data-target="#downloadModal" data-pk="' + str(file.id) + '">'
                             '<i class="fas fa-download"></i> Download</a></div></div>')
        elif file.status == 0:
            progress_html = status_cons[file.status]
            translate_button_html = ('<a href="tra/' + str(file.id) + '" class="tra btn btn-primary btn-mergen-sm"'
                                     ' data-toggle="tooltip" data-placement="top" title="Translate with Google"><i class="fas fa-language"></i></a>\n')
        elif file.status > 100:
            progress_html = ('<div class="progress"><div class="progress-bar progress-bar-striped bg-danger"'
                             ' role="progressbar" style="width: 100%">' + status_cons[file.status] + '</div></div>')
        else:
            progress_html = ('<div class="progress"><div class="progress-bar progress-bar-striped progress-bar-animated"'
                             ' role="progressbar" style="width: '+str(file.progress)+'%"></div></div>')

        if file.delete_format_tag:
            delete_format_tag_html = '<i class="fas fa-eraser"></i>'
        else:
            delete_format_tag_html = ""

        if file.target_lang == "ja":
            if file.change_to_jotai:
                style = "である調"
            else:
                style = "ですます調"
        else:
            style = "N/A"


        html_string = html_string + '        <tr>\n'\
            '          <th scope="row">' + str(file.id) + '</th>\n'\
            '          <td>' + file.name + '</td>\n'\
            '          <td>' + file.source_lang + '</td>\n'\
            '          <td>' + file.target_lang + '</td>\n'\
            '          <td class="text-center">' + delete_format_tag_html + '</td>\n'\
            '          <td>' + style + '</td>\n'\
            '          <td>' + progress_html + '</td>\n'\
            '          <td>' + created_date_str + '</td>\n'\
            '          <td class="text-center">\n'\
            '            ' + translate_button_html + \
            '            ' + delete_button_html + \
            '          </td>\n'\
            '        </tr>\n'
    return_json = {"html": html_string, "done_flag": done_flag}
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

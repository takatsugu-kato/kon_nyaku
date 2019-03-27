"""
This is sample program to use xlf and okapi modules
"""

from lib.xlf import Xlf
from lib.okapi import Okapi

def translate_xlf():
    """
    Translate xlf file
    """

    source_lang = "en"
    target_lang = "ja"
    model = "nmt"
    to_trans_file = "./sample_file/test.docx"

    okapi_obj = Okapi(source_lang, target_lang)
    okapi_obj.create_xlf(to_trans_file)


    xlf_obj = Xlf(to_trans_file + ".xlf")
    xlf_obj.translate(model, delete_format_tag=False, pseudo=True)
    xlf_obj.back_to_xlf()

    okapi_obj.create_transled_file(to_trans_file + ".xlf")

translate_xlf()

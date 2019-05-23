"""
This modules is to translate text
"""
from google.cloud import translate
from .xlf import PseudoClient

def translate_by_google(string, source_language, target_language, model="nmt", pseudo=False):
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

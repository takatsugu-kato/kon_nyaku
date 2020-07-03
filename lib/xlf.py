"""
This modules is to handle xlf file
"""

import os
import re
import string as string_module
import random
from lxml import etree
from google.cloud import translate
from MasuDa import Converter

class Xlf():
    """
    Object handling xlf file

    Args:
        path (str): path of the xlf file
    """

    def __init__(self, path):
        self.source_language = ""
        self.target_language = ""
        self.trans_unit_count = 0
        self.charactor_count = 0
        self.path = path
        self.tree = etree.parse(path)
        etree.register_namespace('xliff', 'urn:oasis:names:tc:xliff:document:1.2')
        etree.register_namespace('okp', 'okapi-framework:xliff-extensions')
        etree.register_namespace('its', 'http://www.w3.org/2005/11/its')
        etree.register_namespace('itsxlf', 'http://www.w3.org/ns/its-xliff/')
        self.root = self.tree.getroot()
        self.namespace = {
            'xliff': 'urn:oasis:names:tc:xliff:document:1.2',
        }
        self.files = self.__get_segment()
        self.__set_language()

    def __set_language(self):
        """
        Set language code from xlf file to this class const
        """

        files = self.root.findall('xliff:file', self.namespace)
        self.source_language = files[0].get('source-language')
        self.target_language = files[0].get('target-language')

    def __get_segment(self):
        """
        Create File obcject from xlf file

        Returns:
            File: File objects
        """
        trans_unit_count = 0
        files = []
        for file in self.root.findall('xliff:file', self.namespace):
            file_obj = File(file.get('original'))
            for trans_unit_element in file.findall('xliff:body/xliff:trans-unit', self.namespace):
                trans_unit_obj = TransUnit(trans_unit_element.get('id'))

                trans_unit_obj.source = self.__create_seg_obj(trans_unit_element, "source")

                # create and append seg_source and seg_target if source is not empty
                if trans_unit_obj.source.string != '\n':
                    trans_unit_obj.seg_source = self.__create_seg_obj(trans_unit_element, "seg-source")
                    trans_unit_obj.seg_target = self.__create_seg_obj(trans_unit_element, "target")
                    trans_unit_count = trans_unit_count + 1
                    file_obj.trans_units.append(trans_unit_obj)
            files.append(file_obj)
        self.trans_unit_count = trans_unit_count
        return files

    def translate(self, delete_format_tag=False, google_glossary_id=None, change_to_jotai=False, pseudo=False, django_file_obj=""):
        """
        Transalte the file object

        Args:
            model (str, optional): Defaults to "nmt". Model of Google translate.
                                    If you want to translate by smt, set the model to "base".
            delete_format_tag (bool, optioanl): Defaults to False.
                                    Flag of to delete the format tag when translate.
            google_glossary_id (bool, optional): Defaults to None.
                                                    Glossary id.
            change_to_jotai (bool, optional): Defaults to False.
                                                If you want to change keitai to jotai for Japanese, set to True.
            pseudo (bool, optional): Defaults to False.
                                        If you want to pseudo translate, set to True.
                                        For example, you don't to want to send to Google.
            django_file_obj (django file object, optional): Defaults to null.
                                                                Django file object for setting the progress
        """
        if pseudo:
            translate_client = PseudoClient()
        else:
            translate_client = translate.TranslationServiceClient()

        parent = translate_client.location_path(
            os.getenv("GOOGLE_PROJECT_ID"),
            os.getenv("GOOGLE_LOCATION")
        )

        glossary_config = None
        if google_glossary_id:
            glossary = translate_client.glossary_path(
                os.getenv("GOOGLE_PROJECT_ID"),
                os.getenv("GOOGLE_LOCATION"),  # The location of the glossary
                google_glossary_id)

            glossary_config = translate.types.TranslateTextGlossaryConfig(
                glossary=glossary)

        unit_count = 0
        for file in self.files:
            for trans_unit in file.trans_units:

                unit_count = unit_count + 1
                if django_file_obj:
                    django_file_obj.progress = unit_count/self.trans_unit_count*100
                    django_file_obj.save()

                for segment in trans_unit.seg_target:
                    xlfstring = XlfString(segment.string)
                    if delete_format_tag:
                        xlfstring.delete_inline_tag()
                    else:
                        xlfstring.change_xlf_inline_tag_to_i_tag()
                    self.charactor_count = self.charactor_count + len(xlfstring.string)
                    translation = translate_client.translate_text(
                        contents=[xlfstring.string],
                        parent=parent,
                        mime_type='text/html',
                        source_language_code=self.source_language,
                        target_language_code=self.target_language,
                        glossary_config=glossary_config)
                    if google_glossary_id:
                        translated_text = translation.glossary_translations[0].translated_text
                    else:
                        translated_text = translation.translations[0].translated_text
                    if change_to_jotai:
                        masuda = Converter()
                        translated_text = masuda.keitai2jotai(translated_text)
                    translated_text = xlfstring.change_i_tag_to_xlf_inline_tag(translated_text)
                    segment.string = xlfstring.revert_placeholder(translated_text)

    def back_to_xlf(self):
        """
        Generate to xlf file from File object
        """

        for file in self.files:
            for trans_unit in file.trans_units:
                new_target_element = self.__create_xml_string_for_element(trans_unit.seg_target)
                condition = (
                    'xliff:file[@original="{0}"]/xliff:body/xliff:trans-unit[@id="{1}"]'
                    .format(file.original, trans_unit.trans_unit_id)
                )
                trans_unit = self.root.find(condition, self.namespace)
                target = trans_unit.find('xliff:target', self.namespace)
                trans_unit.remove(target)
                trans_unit.append(new_target_element)
        try:
            self.tree.write(self.path, encoding="utf-8", xml_declaration=True)
            return True
        except: # pylint: disable=W0702
            return False

    def __create_xml_string_for_element(self, segment_obj):
        """
        Create xml string for segment element

        Args:
            segment_obj (Segment): Segment object in this class

        Returns:
            str: xml string
        """

        xml_string = '<target xml:lang="{0}">'.format(self.target_language)
        for mrk in segment_obj:
            xml_string = (
                xml_string +
                '<mrk mid="{0}" mtype="seg">{1}</mrk>'.format(mrk.segment_id, mrk.string)
            )
        xml_string = xml_string + "</target>"
        tree = etree.fromstring(xml_string)
        return tree

    def __create_seg_obj(self, trans_unit_element, tag):
        """
        Creale Segment object from etree.Element

        Args:
            trans_unit_element (etree.Element): Element object of etree
            tag (str): tag name (source, seg-source, target)

        Returns:
            Segment: Segment object in this class
        """

        element = trans_unit_element.find('xliff:'+tag, self.namespace)

        if tag == "source":
            seg_obj = Segment()
            seg_obj.string = self.__convert_element_to_string(element)
            return seg_obj
        else:
            try:
                mrks = []
                for mrk_element in element.findall('xliff:mrk', self.namespace):
                    mrk_seg_obj = Segment(mrk_element.get('mid'))
                    mrk_seg_obj.string = self.__convert_element_to_string(mrk_element)
                    mrks.append(mrk_seg_obj)
                return mrks
            except AttributeError:
                return None

    def __convert_element_to_string(self, element):
        """
        Convert Element object to string

        Args:
            element (etree.Element): Element object of etree

        Returns:
            str: plain text of Element
        """

        string = etree.tostring(element, encoding='unicode')
        return self.__clean_element_string(string)

    @staticmethod
    def __clean_element_string(string):
        """
        Clean the string of Element

        Args:
            string (str): plain text of Element

        Returns:
            str: string of deleted xml tag
        """

        string = re.sub('<ns[0-9]+:', "<", string)
        string = re.sub('</ns[0-9]+:', "</", string)
        string = re.sub('</?source.*?>', "", string)
        string = re.sub('</?mrk.*?>', "", string)
        return string

class PseudoClient():
    """
    Pseudo translate client object
    """
    def __init__(self, target_language='en'):
        self.target_language = target_language

    @staticmethod
    def location_path(project_id, location):
        pass

    @staticmethod
    def translate_text(contents, parent=None, mime_type=None, target_language_code=None, source_language_code=None, glossary_config=None):
        """
        Translate pseudo.

        Args:
            values (str): To pseudo translate string.
            target_language (str, optional): This option is not use at this time.
            source_language (str, optional): This option is not use at this time.
            model (str, optional): This option is not use at this time.

        Returns:
            [dict]: Translations dict based on Google translate class
        """
        punctuation = ['.', ':', ';', ',', '!', '?']

        #Firstry, split by tags
        tag_splitted_list = re.split('(<span translate="no" id="[0-9]+?">.*?</span>|<.*?>)', contents[0])
        words = []

        #Secondry, split by space
        for temp in tag_splitted_list:
            if temp:
                if re.search('<.*?>', temp):
                    words.append(temp)
                else:
                    words.extend(re.split('( )', temp))

        first_word = True
        for i, word in enumerate(words):
            if not re.search('<.*?>', word) and word and word != " ":
                last_chara = word[-1]
                length = len(word)
                pseudo_first_chara = ""
                if first_word:
                    length = length - 1
                    pseudo_first_chara = random.choice(string_module.ascii_uppercase)
                    first_word = False

                if last_chara in punctuation:
                    length = length - 1
                else:
                    last_chara = ""
                words[i] = ''.join(random.choices(string_module.ascii_lowercase, k=length))
                words[i] = pseudo_first_chara + words[i] + last_chara

        translation = "".join(words)
        response = PseudoTranslateTextResponse()
        response.translations = [PseudoResponsedCompositeContainer(translation)]
        return response

class PseudoTranslateTextResponse():
    def __init__(self):
        self.translations = list()

class PseudoResponsedCompositeContainer():
    def __init__(self, text):
        self.translated_text = text

class File():
    """
    Object of <file> tag in xlf
    """

    def __init__(self, original):
        self.original = original
        self.trans_units = []

class TransUnit():
    """
    Object of <trans-unit> tag in xlf
    """

    def __init__(self, trans_unit_id):
        self.trans_unit_id = trans_unit_id
        self.source = ""
        self.seg_source = []
        self.seg_target = []

class Segment():
    """
    Object of <seg-source>, <source>, and <target> tag in xlf
    """

    def __init__(self, segment_id=0):
        self.segment_id = segment_id
        self.string = ""

class XlfString():
    """
    Object handling string with xlf tag

    Args:
        string (str): string with xlf tag
    """

    def __init__(self, string):
        self.string = string
        self.inline_tag_list = ["g"]
        self.ex_tag_ids = list()
        self.bx_tag_ids = list()
        self.__void_paired_placeholder()
        self.__replace_placeholder_to_notran_tag()
        ##TODO:セグメントの最初にgタグがあったかを保持しておいて、
        # 最後に文全体にgタグをもどしてあげると、文頭の書式だけ保持できる？
        # そもそも、書式削除しないでも翻訳品質を維持できるなら書式削除オプション自体をなくすのでこの保持は不要

    def delete_inline_tag(self):
        """
        Delete xlf inline tag from self.string
        """

        for tag in self.inline_tag_list:
            repatter = re.compile(r'<{0} id=".*?">'.format(tag))
            self.string = repatter.sub('', self.string)
            repatter = re.compile(r'</{0}>'.format(tag))
            self.string = repatter.sub('', self.string)

    def change_xlf_inline_tag_to_i_tag(self):
        """
        Change xlf inline tag to i tag from self.string
        """

        for tag in self.inline_tag_list:
            repatter = re.compile(r'<{0} id="(.*?)">'.format(tag))
            self.string = repatter.sub('<i id="\\1">', self.string)
            repatter = re.compile(r'</{0}>'.format(tag))
            self.string = repatter.sub('</i>', self.string)

    @staticmethod
    def change_i_tag_to_xlf_inline_tag(text):
        """
        Change i tag to xlf inline tag

        Args:
            text (str): String of to change i tag to xlf tag

        Returns:
            str: string of changed i tag to xlf tag
        """

        changed_inline_tag_string = text
        repatter = re.compile(r'<{0} id="(.*?)">'.format("i"))
        changed_inline_tag_string = repatter.sub('<g id="\\1">', changed_inline_tag_string)
        repatter = re.compile(r'</{0}>'.format("i"))
        changed_inline_tag_string = repatter.sub('</g>', changed_inline_tag_string)
        return changed_inline_tag_string

    def __void_paired_placeholder(self):
        """
        Void the paird placeholder tag (ex and bx)
        """

        repatter = re.compile(r'<(ex|bx) id="([0-9]+)"/>')
        match = repatter.search(self.string)
        while match:
            self.string = repatter.sub("", self.string, 1)
            if match.group(1) == "ex":
                self.ex_tag_ids.append(match.group(2))
            elif match.group(1) == "bx":
                self.bx_tag_ids.append(match.group(2))
            match = repatter.search(self.string)

    def __replace_placeholder_to_notran_tag(self):
        """
        Replace xlf placeholder tag to no translate tag of google for enhanced translation quality
        """

        repatter = re.compile(r'<x id="([0-9]+)"/>')
        self.string = repatter.sub('<span translate="no" id="\\1">X</span>', self.string)

    def revert_placeholder(self, text):
        """
        Revert placeholder tag

        Args:
            text (str): String of to revert placeholder tag

        Returns:
            str: String of with paired placeholder tag
        """
        repatter = re.compile(r'<span translate="no" id="([0-9]+)">X</span>')
        text = repatter.sub('<x id="\\1"/>', text)
        for bx_tag_id in reversed(self.bx_tag_ids):
            text = '<bx id ="{0}"/>'.format(bx_tag_id) + text
        for ex_tag_id in self.ex_tag_ids:
            text = text + '<ex id ="{0}"/>'.format(ex_tag_id)
        return text

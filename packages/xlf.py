from lxml import etree
import re

class Xlf():
    """
    Object handling xlf file
    
    Args:
        path (str): path of the xlf file
    """

    def __init__(self, path):
        self.source_language = ""
        self.target_language = ""

        self.path = path
        self.tree = etree.parse(path)
        etree.register_namespace('xliff', 'urn:oasis:names:tc:xliff:document:1.2')
        etree.register_namespace('okp', 'okapi-framework:xliff-extensions')
        etree.register_namespace('its', 'http://www.w3.org/2005/11/its')
        etree.register_namespace('itsxlf', 'http://www.w3.org/ns/its-xliff/')
        self.root = self.tree.getroot()
        self.ns = {
            'xliff': 'urn:oasis:names:tc:xliff:document:1.2',
        }
        self.files = self.__Get_segment()
        self.__Set_language()

    def __Set_language(self):
        """
        Set language code from xlf file to this class const
        """

        files = self.root.findall('xliff:file', self.ns)
        self.source_language = files[0].get('source-language')
        self.target_language = files[0].get('target-language')

    def __Get_segment(self):
        """
        Create File obcject from xlf file
        
        Returns:
            File: File objects
        """

        files = []
        for file in self.root.findall('xliff:file', self.ns):
            file_obj = File(file.get('original'))
            for trans_unit_element in file.findall('xliff:body/xliff:trans-unit', self.ns):
                trans_unit_obj = TransUnit(trans_unit_element.get('id'))

                trans_unit_obj.source = self.__Create_seg_obj(trans_unit_element, "source")
                trans_unit_obj.seg_source = self.__Create_seg_obj(trans_unit_element, "seg-source")
                trans_unit_obj.seg_target = self.__Create_seg_obj(trans_unit_element, "target")

                file_obj.trans_units.append(trans_unit_obj)
            files.append(file_obj)
        return files

    def Back_to_xlf(self):
        """
        Generate to xlf file from File object
        """

        for file in self.files:
            for trans_unit in file.trans_units:
                new_target_element = self.__Create_xml_string_for_segment_element(trans_unit.seg_target)
                # string = ET.tostring(new_target_element, encoding='unicode', short_empty_elements=True)
                # print (string)
                condition = 'xliff:file[@original="{0}"]/xliff:body/xliff:trans-unit[@id="{1}"]'.format(file.original, trans_unit.id)
                trans_unit = self.root.find(condition, self.ns)
                target = trans_unit.find('xliff:target', self.ns)
                trans_unit.remove(target)
                trans_unit.append(new_target_element)
        self.tree.write(self.path, encoding="utf-8", xml_declaration=True)

    def __Create_xml_string_for_segment_element(self,segment_obj):
        """
        Create xml string for segment element
        
        Args:
            segment_obj (Segment): Segment object in this class
        
        Returns:
            str: xml string
        """

        xml_string = '<target xml:lang="{0}">'.format(self.target_language)
        for mrk in segment_obj:
            xml_string = xml_string + '<mrk mid="{0}" mtype="seg">{1}</mrk>'.format(mrk.id,mrk.string)
        xml_string = xml_string + "</target>"
        tree = etree.fromstring(xml_string)
        return tree

    def __Create_seg_obj(self, trans_unit_element, tag):
        """
        Creale Segment object from etree.Element
        
        Args:
            trans_unit_element (etree.Element): Element object of etree
            tag (str): tag name (source, seg-source, target)
        
        Returns:
            Segment: Segment object in this class
        """

        element = trans_unit_element.find('xliff:'+tag, self.ns)

        if (tag == "source"):
            seg_obj = Segment()
            seg_obj.string = self.__Element_to_string(element)
            return seg_obj
        else:
            mrks = []
            for mrk_element in element.findall('xliff:mrk', self.ns):
                mrk_seg_obj = Segment(mrk_element.get('mid'))
                mrk_seg_obj.string = self.__Element_to_string(mrk_element)
                mrks.append(mrk_seg_obj)
            return mrks

    def __Element_to_string(self, element):
        """
        Convert Element object to string
        
        Args:
            element (etree.Element): Element object of etree
        
        Returns:
            str: plain text of Element
        """

        string = etree.tostring(element, encoding='unicode')
        return (self.__Clean_element_string(string))

    def __Clean_element_string(self, string):
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

    def __init__(self, id):
        self.id = id
        self.source = ""
        self.seg_source = []
        self.seg_target = []

class Segment():
    """
    Object of <seg-source>, <source>, and <target> tag in xlf
    """

    def __init__(self, id = 0):
        self.id = id
        self.string = ""


import xml.etree.ElementTree as ET
import re

class Xlf():
    def __init__(self, path):
        tree = ET.parse(path)
        self.root = tree.getroot()
        self.ns = {
            'xliff': 'urn:oasis:names:tc:xliff:document:1.2',
            'okp': 'okapi-framework:xliff-extensions',
            'its': 'http://www.w3.org/2005/11/its',
            'itsxlf': 'http://www.w3.org/ns/its-xliff/'
        }
    def get_segment(self):
        files = []
        for file in self.root.findall('xliff:file', self.ns):
            file_obj = File(file.get('original'))
            for trans_unit_element in file.findall('xliff:body/xliff:trans-unit', self.ns):
                trans_unit_obj = TransUnit(trans_unit_element.get('id'))

                trans_unit_obj.source = create_seg_obj(self,trans_unit_element, "source")
                trans_unit_obj.seg_source = create_seg_obj(self, trans_unit_element, "seg-source")
                trans_unit_obj.seg_target = create_seg_obj(self, trans_unit_element, "target")

                file_obj.segments.append(trans_unit_obj)
            files.append(file_obj)
        return files

class File():
    def __init__(self, original):
        self.original = original
        self.segments = []

class TransUnit():
    def __init__(self, id):
        self.id = id
        self.source = ""
        self.seg_source = []
        self.seg_target = []

class Segment():
    def __init__(self, id = 0):
        self.id = id
        self.string = ""

def create_seg_obj(self, trans_unit_element, tag):
    element = trans_unit_element.find('xliff:'+tag, self.ns)

    if (tag == "source"):
        seg_obj = Segment()
        seg_obj.string = Element_to_string(element)
        return seg_obj
    else:
        mrks = []
        for mrk_element in element.findall('xliff:mrk', self.ns):
            mrk_seg_obj = Segment(mrk_element.get('mid'))
            mrk_seg_obj.string = Element_to_string(mrk_element)
            mrks.append(mrk_seg_obj)
        return mrks

def Element_to_string(element):
    string = ET.tostring(element, encoding='unicode', short_empty_elements=True)
    return (Clean_element_string(string))

def Clean_element_string(string):
    string = re.sub('<ns[0-9]+:', "<", string)
    string = re.sub('</ns[0-9]+:', "</", string)
    string = re.sub('</?source.*?>', "", string)
    string = re.sub('</?mrk.*?>', "", string)
    # string = re.sub('</?seg-source.*?>', "", string)
    return string

xlf_obj = Xlf("./sample_file/test.docx.xlf")
files = xlf_obj.get_segment()

# tree = ET.parse("./sample_file/test.docx.xlf")
# root = tree.getroot()
# print(root.tag,root.attrib)


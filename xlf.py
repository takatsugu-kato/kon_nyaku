import xml.etree.ElementTree as ET
import re

class Xlf():
    def __init__(self, path):
        self.source_language = ""
        self.target_language = ""

        self.path = path
        self.tree = ET.parse(path)
        ET.register_namespace('', 'urn:oasis:names:tc:xliff:document:1.2')
        ET.register_namespace('okp', 'okapi-framework:xliff-extensions')
        ET.register_namespace('its', 'http://www.w3.org/2005/11/its')
        ET.register_namespace('itsxlf', 'http://www.w3.org/ns/its-xliff/')
        self.root = self.tree.getroot()
        self.ns = {
            'xliff': 'urn:oasis:names:tc:xliff:document:1.2',
        }
        self.seg_data = self.Get_segment()
        self.Set_language()

    def Set_language(self):
        files = self.root.findall('xliff:file', self.ns)
        self.source_language = files[0].get('source-language')
        self.target_language = files[0].get('target-language')

    def Get_segment(self):
        files = []
        for file in self.root.findall('xliff:file', self.ns):
            file_obj = File(file.get('original'))
            for trans_unit_element in file.findall('xliff:body/xliff:trans-unit', self.ns):
                trans_unit_obj = TransUnit(trans_unit_element.get('id'))

                trans_unit_obj.source = Create_seg_obj(self,trans_unit_element, "source")
                trans_unit_obj.seg_source = Create_seg_obj(self, trans_unit_element, "seg-source")
                trans_unit_obj.seg_target = Create_seg_obj(self, trans_unit_element, "target")

                file_obj.segments.append(trans_unit_obj)
            files.append(file_obj)
        return files

    def Back_to_xlf(self):
        for file in self.seg_data:
            for trans_unit in file.segments:
                new_target_element = Create_segment_element(self, trans_unit.seg_target)
                # string = ET.tostring(new_target_element, encoding='unicode', short_empty_elements=True)
                # print (string)
                condition = 'xliff:file[@original="{0}"]/xliff:body/xliff:trans-unit[@id="{1}"]'.format(file.original, trans_unit.id)
                trans_unit = self.root.find(condition, self.ns)
                target = trans_unit.find('xliff:target', self.ns)
                trans_unit.remove(target)
                trans_unit.append(new_target_element)
        self.tree.write('output.xml', encoding="utf-8")

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

def Create_segment_element(self,segment_obj):
    root = ET.Element('target')
    root.set("xml:lang", self.target_language)
    for mrk in segment_obj:
        mrk_element = ET.SubElement(root, 'mrk')
        mrk_element.set("mid", mrk.id)
        mrk_element.set("mtype", "seg")
        ##ToDO XML文字をでコードして入れる方法を探す
        mrk_element.text = mrk.string
    return root

def Create_seg_obj(self, trans_unit_element, tag):
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
    return string

xlf_obj = Xlf("./sample_file/test.docx.xlf")
xlf_obj.seg_data[1].segments[0].seg_target[0].string = "irekaemasita"

xlf_obj.Back_to_xlf()

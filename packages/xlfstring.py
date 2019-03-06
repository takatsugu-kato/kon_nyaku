import re

class XlfString():
    """
    Object handling string with xlf tag
    
    Args:
        string (str): string with xlf tag
    """

    def __init__(self, string):
        self.string = string
        self.inline_tag_list = ["g"]
        self.exist_ex_tag = False
        self.exist_bx_tag = False
        self.paired_placeholder_id = 0
        self.__void_paired_placeholder()

    def delete_inline_tag(self):
        """
        Delete xlf inline tag
        
        Returns:
            str: strig of deleted xlf inline tag
        """

        deleted_inline_tag_string = self.string
        for tag in self.inline_tag_list:
            repatter = re.compile(r'<{0} id=".*?">(.*?)</{0}>'.format(tag))
            deleted_inline_tag_string = repatter.sub("\\1", deleted_inline_tag_string)
        return deleted_inline_tag_string

    def change_xlf_inline_tag_to_span(self):
        """
        Change xlf inline tag to span tag
        
        Returns:
            str: string of changed xlf tag to span tag
        """

        changed_inline_tag_string = self.string
        for tag in self.inline_tag_list:
            repatter = re.compile(r'<{0} id="(.*?)">'.format(tag))
            changed_inline_tag_string = repatter.sub('<span id="\\1">', changed_inline_tag_string)
            repatter = re.compile(r'</{0}>'.format(tag))
            changed_inline_tag_string = repatter.sub('</span>', changed_inline_tag_string)
        return changed_inline_tag_string

    def change_span_to_xlf_inline_tag(self, text):
        """
        Change span tag to xlf inline tag

        Args:
            text (str): String of to change span tag to xlf tag
        
        Returns:
            str: string of changed span tag to xlf tag
        """

        changed_inline_tag_string = text
        repatter = re.compile(r'<{0} id="(.*?)">'.format("span"))
        changed_inline_tag_string = repatter.sub('<g id="\\1">', changed_inline_tag_string)
        repatter = re.compile(r'</{0}>'.format("span"))
        changed_inline_tag_string = repatter.sub('</g>', changed_inline_tag_string)
        return changed_inline_tag_string

    def __void_paired_placeholder(self):
        """
        Void the paird placeholder tag (ex and bx)
        """

        repatter = re.compile(r'<(ex|bx) id="([0-9]+)"/>')
        m = repatter.match(self.string)
        if m:
            self.paired_placeholder_id = m.group(2)
            self.string = repatter.sub("", self.string)
            if m.group(1) == "ex":
                self.exist_ex_tag = True
            elif m.group(1) == "bx":
                self.exist_bx_tag = True

    def revert_paired_placeholder(self, text):
        """
        Revert paired placeholder tag
        
        Args:
            text (str): String of to revert paired placeholder tag
        
        Returns:
            str: String of with paired placeholder tag
        """

        if self.exist_bx_tag:
            text = '<bx id ="{0}"/>'.format(self.paired_placeholder_id) + text
        if self.exist_ex_tag:
            text = text + '<ex id ="{0}"/>'.format(self.paired_placeholder_id)
        return text

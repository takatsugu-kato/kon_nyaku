import subprocess
import os

class Okapi():
    """
    Excute the tikal via command line
    
    Args:
        sl: Soruce language
        tl: Target Language
    """

    def __init__(self, sl, tl):
        if os.name == "nt":
            self.tikal_name = "tikal.bat"
        elif os.name == "posix":
            self.tikal_name = "tikal.sh"
        self.__en = sl
        self.__tl = tl

    def create_xlf(self, filepath):
        """
        Create xlf file
        
        Args:
            filepath (str): The path want to create xlf file
        
        Returns:
            str or bool(False): Command line output of tikal or False
        """

        cmd = "{0} -x {1} -seg -sl {2} -tl {3} -ie utf8 -oe utf8".format(self.tikal_name, filepath, self.__en, self.__tl)
        try:
            res = subprocess.check_output(cmd, shell=True)
            return res
        except:
            return False

    def create_transled_file(self, filepath):
        """
        Create translated file from xlf file
        
        Args:
            filepath (str): Tha path want to create translatef file
        
        Returns:
            str or bool(False): Command line output of tikal or False
        """

        cmd = self.tikal_name + ' -m "' + filepath
        cmd = "{0} -m {1} -sl {2} -tl {3} -ie utf8 -oe utf8".format(self.tikal_name, filepath, self.__en, self.__tl)
        try:
            res = subprocess.check_output(cmd, shell=True)
            return res
        except:
            return False


# encoding: utf-8
import xml.sax
import os

from Transform import *
from scipy.misc import imread
import numpy as np
from PIL import Image


class xmlReader(xml.sax.ContentHandler):
    def __init__(self):
        self.contents = {}  # all contents in xml
        # self.tmp = {}  # a piece
        self.backend = 0  # postfix
        self.tag = ''  # name of tag
        self.ParentTag = []  # parent tag
        self.backend_str = []  # follow to store the information of backend
        self.useful_now = False
        self.is_common = ''  # the tag has ended,which may bring error in character()

    def startElement(self, name, attrs):
        self.tag = name  # the name of temporal tag
        self.is_common = ''
        if name == "object":  # object tag in xml
            self.useful_now = True  # objects is in the contents now.
        '''
        self.tmp.clear()#slef.tmp is used for common labels
        self.tmp[name] = ''
        self.contents[self.nodes].setdefault(name)#useless
        '''

    def endElement(self, name):
        if len(self.backend_str):
            name += self.backend_str[-1]
        if name in self.ParentTag:  # just suppose all tag is occured didymous or occured as couple
            self.ParentTag.pop()
            self.backend_str.pop()
        if name == "object":
            self.useful_now = False

        self.tag = name  # the name must equal tag now
        self.is_common = name

    def characters(self, content):
        if self.useful_now:
            # useless information or the tag has been ended
            if len(content) > 0 and content[0] == '\t' or self.is_common == self.tag:
                return

            tmp_dict = self.contents
            for i in self.ParentTag:  # to the last level of the dict of contents
                tmp_dict = tmp_dict[i]

            # obtain a name has no conflict
            key_name = self.tag
            if tmp_dict.get(key_name):
                key_name += str(self.backend)

            if content == '\n':  # at least double connect labels
                tmp_dict[key_name] = {}
                self.ParentTag.append(key_name)  # this is very important
                if key_name == self.tag:
                    self.backend_str.append('')
                else:
                    self.backend_str.append(str(self.backend))
                    self.backend += 1  # all name is different
            else:
                tmp_dict[key_name] = content


    '''
    def __del__(self):
        return  self.contents
    '''


def gotXMLInfo(info):
    # creat XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # defined ContextHandler
    Handler = xmlReader()
    parser.setContentHandler(Handler)

    # read xmlAnno
    parser.parse(info)
    return Handler.contents


def mainFunction(image_path, anno_path):
    objects = gotXMLInfo(anno_path)
    image = imread(image_path)
    trans_dict = transform(image, objects)
    keys = trans_dict.keys()
    idx = random.randint(0, len(keys) - 1)
    return trans_dict[keys[idx]]

def test():
    info = "/home/flag54/Documents/dataSetAugument/data/anno/009653.xml"
    photo = "/home/flag54/Documents/dataSetAugument/data/dataSet/009653.jpg"
    print os.curdir

    data, newoj = mainFunction(photo, info)
    print 'o'
    return data,newoj


if __name__ == "__main__":
    test()

    

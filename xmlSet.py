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
        self.tmp = {}  # a piece
        self.nodes = 0  # tree construction
        self.tag = ''  # name of tag
        self.ParentTag = []  # parent tag

    def startElement(self, name, attrs):
        if name == "object":  # object tag in xml
            self.contents.setdefault(self.nodes, {})
            self.ParentTag.append(name)
        elif name == "bndbox":
            self.contents[self.nodes].setdefault(name, {})
            # self.tmp[name]={}
            self.ParentTag.append(name)
            self.tag = name
        elif "object" in self.ParentTag:
            self.tmp.clear()
            self.tmp[name] = ''
            self.contents[self.nodes].setdefault(name)
            self.tag = name

    def endElement(self, name):
        if name == "object":
            self.nodes += 1
            self.ParentTag.pop()
        elif name == "bndbox":
            self.ParentTag.pop()
            # self.contents[self.nodes][name]=self.tmp[name]

        if "bndbox" in self.ParentTag:
            self.contents[self.nodes]["bndbox"][name] = self.tmp[name]
        elif "object" in self.ParentTag and name != "bndbox":
            self.contents[self.nodes][name] = self.tmp[name]

    def characters(self, content):
        self.tmp[self.tag] = content

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


if __name__ == "__main__":
    info = "/home/flag54/Documents/dataSetAugument/data/anno/000001.xml"
    photo = "/home/flag54/Documents/dataSetAugument/data/dataSet/000001.jpg"
    print os.curdir

    data, newoj = mainFunction(photo, info)
    print 'o'

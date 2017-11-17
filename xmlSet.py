# encoding: utf-8
import xml.sax
import os
from jaccardOverlap import *
from scipy.misc import imread
import numpy as np

class xmlReader(xml.sax.ContentHandler):

    def __init__(self):
        self.contents={}    #all contents in xml
        self.tmp={}         #a piece
        self.nodes=0        #tree construction
        self.tag = ''       #name of tag
        self.ParentTag=[]        #parent tag

    def startElement(self, name, attrs):
        if name=="object":#object tag in xml
            self.contents.setdefault(self.nodes,{})
            self.ParentTag.append(name)
        elif name=="bndbox":
            self.contents[self.nodes].setdefault(name,{})
            #self.tmp[name]={}
            self.ParentTag.append(name)
            self.tag=name
        elif "object" in self.ParentTag:
            self.tmp.clear()
            self.tmp[name]=''
            self.contents[self.nodes].setdefault(name)
            self.tag=name


    def endElement(self, name):
        if name=="object":
            self.nodes+=1
            self.ParentTag.pop()
        elif name=="bndbox":
            self.ParentTag.pop()
            #self.contents[self.nodes][name]=self.tmp[name]

        if "bndbox" in self.ParentTag:
            self.contents[self.nodes]["bndbox"][name]=self.tmp[name]
        elif "object" in self.ParentTag and name != "bndbox":
            self.contents[self.nodes][name]=self.tmp[name]

    def characters(self, content):
        self.tmp[self.tag]=content

    '''
    def __del__(self):
        return  self.contents
    '''

class gotInfoofXML:
    def __init__(self):
        pass

    def getInfo(self,info):
        pass

if __name__ == "__main__":
    info="/home/flag54/Documents/dataSetAugument/data/anno/000001.xml"
    print os.curdir

    # 创建一个 XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    # 重写 ContextHandler
    Handler = xmlReader()
    parser.setContentHandler(Handler)
    parser.parse(info)
    image =imread("/home/flag54/Documents/dataSetAugument/data/dataSet/000001.jpg")
    #print "$$$$$$$$$$$", Handler.contents
    jaccard(image,Handler.contents)
    #colors = plt.cm.hsv(np.linspace(0, 1, 21)).tolist()
    #plt.imshow(image)
    #plt.show()
    print 'oo'
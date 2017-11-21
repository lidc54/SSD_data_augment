#
import os
from xmlSet import mainFunction
from Transform import *
from scipy.misc import imread


def linkImgAnn(cp):
    data, ann = cp
    dataDir = '/'.join(data.split('/')[0:2])
    annDir = '/'.join(ann.split('/')[0:2])
    extend = '_Aug'


def readFile():
    testFile = '/home/flag54/Downloads/caffe-ssd/data/VOC0712/trainval.txt'

    for bond in open(testFile):
        both = bond.split()
        yield both
        '''
        if os.path.exists(both[0]) and os.path.exists(both[1]) :
            linkImgANN(both)
        '''


def readAnnoImage():
    prex = "/home/flag54/Downloads/caffe-ssd/data/VOCdevkit/"

    # read xmlAnno
    couples = readFile()
    xx = (1,)
    for cp in couples:
        try:
            img, anno = cp
            print prex + img,
            if img=='VOC2012/JPEGImages/2009_002851.jpg':
                print 'oo'
            data, labels, origin_data = mainFunction(prex + img, prex + anno)
            tmp = []
            for i in labels.keys():
                tmp.append(labels[i]['name'])
            xx += tuple(tmp)
            # print 'o'
            ###deal with data & its labels
            # show_data(data, labels)
        except Exception, e:
            print 'line:', e
    print xx


if __name__ == "__main__":
    readAnnoImage()

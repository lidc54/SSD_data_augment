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
    testFile = 'data/test.txt'

    for bond in open(testFile):
        both = bond.split()
        yield both
        '''
        if os.path.exists(both[0]) and os.path.exists(both[1]) :
            linkImgANN(both)
        '''


def readAnnoImage():
    prex = "/home/flag54/Documents/dataSetAugument/"

    # read xmlAnno
    couples = readFile()
    for cp in couples:
        try:
            img, anno = cp
            data, labels = mainFunction(prex + img, prex + anno)

            ###deal with data & its labels
            show_data(data, labels)
        except Exception, e:
            print e


if __name__ == "__main__":
    readAnnoImage()

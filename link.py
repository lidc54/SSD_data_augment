#
import os
from xmlSet import gotXMLInfo
from Transform import *
from scipy.misc import imread



def linkImgAnn(cp):
    data,ann=cp
    dataDir='/'.join( data.split('/')[0:2] )
    annDir='/'.join( ann.split('/')[0:2] )
    extend='_Aug'


def readFile():
    testFile='data/test.txt'

    for bond in open(testFile):
        both=bond.split()
        yield both
        '''
        if os.path.exists(both[0]) and os.path.exists(both[1]) :
            linkImgANN(both)
        '''

def readAnnoImage():
    info="/home/flag54/Documents/dataSetAugument/data/anno/000001.xml"
    photo = "/home/flag54/Documents/dataSetAugument/data/dataSet/000001.jpg"
    print os.curdir
    #cp = readFile()
    #read xmlAnno
    objects = gotXMLInfo(info)
    #read img
    image =imread(photo)
    #get transformed image
    dict_trans = transform(image,objects)

    return  dict_trans

if __name__ == "__main__":
    readAnnoImage()
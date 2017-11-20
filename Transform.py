'''
mirror:probably is 0.5
distort:color jitter
expand:origin image expand to 4*4
crop:random crop
'''
from jaccard import *


# import random
# from PIL import Image, ImageEnhance, ImageOps, ImageFile
# import matplotlib.pyplot as plt
# import numpy as np
# import copy


def transform(image, objects):
    '''data augment'''
    trans_dict = {}
    sz = (300, 300)  # width & height -- order

    # 1.expand image
    trans_dict['expand'] = expand(image, objects, sz)

    # 2.origin image -- resize
    image, objects = resize_imgAnno(sz, image, objects)
    trans_dict['origin'] = [image.copy(), copy.deepcopy(objects)]

    # 3.mirror
    prob = random.randint(1, 2)
    if prob > 1:
        image = image[:, ::-1]
        mirrot_anno(image, objects)
        trans_dict['mirror'] = [image.copy(), copy.deepcopy(objects)]

    # 4.distort
    image = jitter(image)
    # trans_dict['distort'] = [image.copy(),copy.deepcopy(objects)]

    # 5.jaccard
    try:
        dict_jaccard = corp_image(image, objects, sz)
        trans_dict = dict(trans_dict, **dict_jaccard)
        print 'po'
    except Exception, e:
        print "what's wrong:",e

    return trans_dict


def mirrot_anno(image, objects):
    '''mirror the annoated info at the same time'''
    height, width, channel = image.shape
    coord = ['xmin', 'xmax', 'ymin', 'ymax']
    for i in objects.keys():
        xmin, xmax, ymin, ymax = [int(objects[i]['bndbox'][k]) for k in coord]
        new_xmin = width - xmax
        new_xmax = width - xmin
        objects[i]['bndbox']['xmin'] = new_xmin
        objects[i]['bndbox']['xmax'] = new_xmax


def jitter(data):
    image = Image.fromarray(data)
    random_factor = np.random.randint(0, 31) / 10.
    color_image = ImageEnhance.Color(image).enhance(random_factor)
    random_factor = np.random.randint(5, 11) / 10.
    brightness_image = ImageEnhance.Brightness(color_image).enhance(random_factor)
    random_factor = np.random.randint(10, 21) / 10.
    contrast_image = ImageEnhance.Contrast(brightness_image).enhance(random_factor)
    '''
    plt.subplot(121)
    plt.imshow(image)
    plt.subplot(122)
    plt.imshow(contrast_image)
    '''
    return np.array(contrast_image)


def expand(image, objects, sz, ratio=3):
    '''zoom out'''
    height, width, channel = image.shape
    aug_sz = (sz[0] * ratio, sz[1] * ratio)
    mean_value = [104, 117, 123]
    # build a canvus
    canvus = np.zeros((aug_sz[0], aug_sz[0], channel), dtype="uint8")
    for i in range(channel):
        canvus[:, :, i] = mean_value[i]

    # insert the image
    h_off = random.randint(0, aug_sz[0] - height)
    w_off = random.randint(0, aug_sz[1] - width)
    canvus[h_off:h_off + height, w_off:w_off + width, :] = image

    # adjust the labels
    new_objects = copy.deepcopy(objects)
    coord = ['xmin', 'xmax', 'ymin', 'ymax']
    for i in new_objects.keys():
        coor = new_objects[i]['bndbox']
        xmin, xmax, ymin, ymax = [int(coor[k]) for k in coord]  # coor's coordination is num now,not a string
        newCoor = [xmin + w_off, xmax + w_off, ymin + h_off, ymax + h_off]
        for k, key in enumerate(coord):
            coor[key] = newCoor[k]

    canvus, new_objects = resize_imgAnno(sz, canvus, new_objects)

    return canvus, new_objects

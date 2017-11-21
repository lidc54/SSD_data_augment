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


def transform(origin_image, objects):
    """
    data augment
    :param origin_image:
    :param objects: annoated dict
    :return:
    """
    # whitening
    image = whiter(origin_image)
    # image=origin_image

    trans_dict = {}
    sz = (300, 300)  # width & height -- order

    # 1.expand image$$
    trans_dict['expand'] = expand(image, objects, sz, origin_image)

    # 2.origin image -- resize$$
    image, objects = resize_imgAnno(sz, image, objects)
    origin_image, _ = resize_imgAnno(sz, origin_image, objects)
    trans_dict['origin'] = [image.copy(), copy.deepcopy(objects), origin_image.copy()]

    # 3.mirror$$
    prob = random.randint(1, 2)
    if prob > 1:
        image = image[:, ::-1]
        origin_image = origin_image[:, ::-1]
        mirrot_anno(image, objects)
        trans_dict['mirror'] = [image.copy(), copy.deepcopy(objects), origin_image.copy()]

    # 4.distort$$
    image = jitter(image)
    # trans_dict['distort'] = [image.copy(),copy.deepcopy(objects)]

    # 5.jaccard$$
    try:
        dict_jaccard = corp_image(image, objects, sz, origin_image)
        trans_dict = dict(trans_dict, **dict_jaccard)
        # print 'po'
    except Exception, e:
        print "what's wrong:", e

    return trans_dict


def mirrot_anno(image, objects):
    '''mirror the annoated info at the same time'''
    height, width, channel = image.shape
    coord = ['xmin', 'xmax', 'ymin', 'ymax']
    for i in objects.keys():
        if not (type(objects[i]) == dict and objects[i].has_key('bndbox')):
            continue
        xmin, xmax, ymin, ymax = [int(objects[i]['bndbox'][k]) for k in coord]
        new_xmin = width - xmax
        new_xmax = width - xmin
        objects[i]['bndbox']['xmin'] = new_xmin
        objects[i]['bndbox']['xmax'] = new_xmax


def jitter(data):
    image, min_max = transfer(data)
    image = Image.fromarray(image)
    random_factor = np.random.randint(0, 31) / 10.
    image = ImageEnhance.Color(image).enhance(random_factor)
    random_factor = np.random.randint(5, 11) / 10.
    image = ImageEnhance.Brightness(image).enhance(random_factor)
    random_factor = np.random.randint(10, 21) / 10.
    image = ImageEnhance.Contrast(image).enhance(random_factor)
    '''
    plt.subplot(121)
    plt.imshow(image)
    plt.subplot(122)
    plt.imshow(contrast_image)
    '''
    image = np.array(image)
    image = re_transfer(image, min_max)
    return image


def expand(image, objects, sz, origin_image, ratio=3):
    """
    zoom out
    :param image:
    :param objects:
    :param sz:
    :param ratio:
    :return:
    """
    height, width, channel = image.shape
    aug_sz = (sz[0] * ratio, sz[1] * ratio)
    mean_value = [104, 117, 123]
    # build a canvus
    canvus = np.zeros((aug_sz[0], aug_sz[0], channel), dtype="uint8")
    canvus_origin = np.zeros((aug_sz[0], aug_sz[0], channel), dtype="uint8")  # origin image for show
    for i in range(channel):
        canvus[:, :, i] = mean_value[i]
        canvus_origin[:, :, i] = mean_value[i]  # origin image for show

    # insert the image
    h_off = random.randint(0, aug_sz[0] - height)
    w_off = random.randint(0, aug_sz[1] - width)
    canvus[h_off:h_off + height, w_off:w_off + width, :] = image
    canvus_origin[h_off:h_off + height, w_off:w_off + width, :] = origin_image  # origin image for show
    # adjust the labels
    new_objects = copy.deepcopy(objects)
    coord = ['xmin', 'xmax', 'ymin', 'ymax']
    for i in new_objects.keys():
        if not (type(new_objects[i]) == dict and new_objects[i].has_key('bndbox')):
            continue
        coor = new_objects[i]['bndbox']
        xmin, xmax, ymin, ymax = [int(coor[k]) for k in coord]  # coor's coordination is num now,not a string
        newCoor = [xmin + w_off, xmax + w_off, ymin + h_off, ymax + h_off]
        for k, key in enumerate(coord):
            coor[key] = newCoor[k]

    canvus, new_objects = resize_imgAnno(sz, canvus, new_objects)
    canvus_origin, _ = resize_imgAnno(sz, canvus_origin, new_objects)
    return [canvus, new_objects, canvus_origin]  # image,lables,origin_image


def whiter(image):
    """

    :param image: image.shape=[300,300,3];height,width,channel
    :return: the data after whitering
    """
    data = np.zeros(image.shape).astype('float16')
    w, h, c = image.shape
    for i in range(c):
        data[:, :, i] = (image[:, :, i] - np.mean(image[:, :, i])) / np.std(image[:, :, i])
    return data

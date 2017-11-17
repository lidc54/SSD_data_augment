# encoding : utf-8
import random
import matplotlib.pyplot as plt
import numpy as np
import copy
from PIL import Image, ImageEnhance, ImageOps, ImageFile


def show_data(data, label):
    colors = plt.cm.hsv(np.linspace(0, 1, 21)).tolist()
    print colors[1]
    plt.imshow(data)

    AX = plt.gca()
    coord = ['xmin', 'xmax', 'ymin', 'ymax']
    for i in label.keys():
        coor = label[i]['bndbox']
        xmin, xmax, ymin, ymax = [int(coor[k]) for k in coord]  # coor's coordination is num now,not a string
        newCoor = (xmin + 1, ymin + 1), xmax - xmin - 2, ymax - ymin - 2
        AX.add_patch(plt.Rectangle(*newCoor, fill=False, edgecolor=colors[random.randint(0, 20)], linewidth=2))
    plt.show()


def resize_imgAnno(sz, data, oj):
    '''resize the image & annotated info'''
    objects = copy.deepcopy(oj)
    height, width, channel = data.shape
    coord = ['xmin', 'xmax', 'ymin', 'ymax']
    hw = [width, width, height, height]
    top_width, top_height = sz
    top_hw = [top_width, top_width, top_height, top_height]
    for i in range(len(objects)):
        coor = [int(objects[i]['bndbox'][k]) for k in coord]
        coor = [1.0 * x / y for x, y in zip(coor, hw)]
        coor = [int(x * y) for x, y in zip(coor, top_hw)]
        for k in range(len(coord)):
            objects[i]['bndbox'][coord[k]] = coor[k]
    # image --
    image = Image.fromarray(data)
    image = image.resize(sz)
    image = np.array(image)
    return image, objects
    # show_data(image,objects)


def lap(coor_random, coor):
    lap_xmin = coor_random[0] if (coor[0] < coor_random[0]) else coor[0]
    lap_ymin = coor_random[2] if (coor[2] < coor_random[2]) else coor[2]
    lap_xmax = coor_random[1] if (coor[1] > coor_random[1]) else coor[1]
    lap_ymax = coor_random[3] if (coor[3] > coor_random[3]) else coor[3]
    return [lap_xmin, lap_xmax, lap_ymin, lap_ymax]


# coordination order is :['xmin','xmax','ymin','ymax']
# to find out the jaccard overlap ratio between box & ground truth
def overlap(coor_random, coor):
    width_random = coor_random[1] - coor_random[0]
    height_random = coor_random[3] - coor_random[2]
    width = coor[1] - coor[0]
    height = coor[3] - coor[2]
    lap_xmin, lap_xmax, lap_ymin, lap_ymax = lap(coor_random, coor)
    s_random = width_random * height_random
    s = width * height
    s_lap = (lap_xmax - lap_xmin) * (lap_ymax - lap_ymin)
    ratio = 1.0 * s_lap / (s_random + s - s_lap)
    return ratio, [lap_xmin, lap_xmax, lap_ymin, lap_ymax]


def random_box():
    '''the width & height will be genenered randomly at first according to sacle & aspect ratio
       then the w_h_off
    '''
    aspcect_constraint = [0.5, 2.0]  # width/height
    scale_constraint = [0.3, 1.0]  # random box vs. origin
    aspect_zone = aspcect_constraint[1] - aspcect_constraint[0] - 0.01
    aspect = random.random() * aspect_zone + aspcect_constraint[0]
    scale = random.uniform(scale_constraint[0], scale_constraint[1])

    aspect = max(aspect, scale ** 2)
    aspect = min(aspect, scale ** 0.5)

    box_width = scale * aspect ** 0.5
    box_height = scale / aspect ** 0.5

    w_off = random.uniform(0.0, 1 - box_width)
    h_off = random.uniform(0.0, 1 - box_height)

    return w_off, w_off + box_width, h_off, h_off + box_height


def satisfy_constraint(objects, coord_random, min_jaccard):  # ,keep
    '''random box shoulr meet the constraint need;ie.min_jaccard_overlap: 0.10000000149'''
    xmin, xmax, ymin, ymax = coord_random
    found = False
    coord = ['xmin', 'xmax', 'ymin', 'ymax']
    for i in range(len(objects)):
        object_box = [int(objects[i]['bndbox'][k]) for k in coord]
        # center of object box should located in the random box
        ixmin, ixmax, iymin, iymax = object_box
        meanx = (ixmax + ixmin) / 2
        meany = (iymax + iymin) / 2
        if not xmin < meanx < xmax and ymin < meany < ymax:
            continue
        # satisfy the jaccard overlap threhold constratint
        ratio, lap_coord = overlap(coord_random, object_box)  #
        if not ratio > min_jaccard:
            continue
        found = True
        # keep[i]=lap_coord[:]
        if found:
            return found
    return found


def corp(image, objects_origin, coor):
    '''crop image & labels according coor which is random box'''
    objects = copy.deepcopy(objects_origin)
    xmin, xmax, ymin, ymax = coor
    if 3 == image.ndim:
        data = image[ymin:ymax, xmin:xmax, :]
    if 2 == image.ndim:
        data = image[ymin:ymax, xmin:xmax]

    # crop annoated info
    Anno = ['xmin', 'xmax', 'ymin', 'ymax']
    topLeft = [coor[0], coor[0], coor[2], coor[2]]  # coordination of top left
    keep = []
    for i in objects.keys():
        object_box = [int(objects[i]['bndbox'][k]) for k in Anno]

        # center of object box should located in the random box
        ixmin, ixmax, iymin, iymax = object_box
        meanx = (ixmax + ixmin) / 2
        meany = (iymax + iymin) / 2
        if not xmin < meanx < xmax and ymin < meany < ymax:
            continue

        overlap_coor = lap(coor, object_box)
        for k, anno in enumerate(Anno):
            objects[i]['bndbox'][anno] = overlap_coor[k] - topLeft[k]
            overlap_coor[k] -= topLeft[k]  # change the values in patch
        keep.append(i)
    for key in objects.keys():
        if not key in keep:
            objects.pop(key)

    return data, objects


'''
image is a photo/graph
objects store its annotated information
min_jaccard is its minmum overlap between random box &  
'''


def generate_batch_samples(image, objects, min_jaccard, max_trials=50):
    '''generate random crop sample for input data'''
    height, width, channel = image.shape
    trials = []
    for i in range(max_trials):
        # keep = {}#store jaccard overlap coordinate
        # xmin, xmax, ymin, ymax
        if min_jaccard < 0.05:
            coor_ = [0.0, 1.0, 0.0, 1.0]
        else:
            coor_ = random_box()
        size_img = [width, width, height, height]
        coor_random = [int(x * y) for x, y in zip(coor_, size_img)]
        if min_jaccard < 0.05:
            return coor_random[:]
        # rectify the random box is legal
        if satisfy_constraint(objects, coor_random, min_jaccard):  # ,keep
            # satisfied = coor_random[:]
            # satisfied.append(copy.deepcopy(keep))#first 4 is coor ,the last one is ovelap objects
            trials.append(coor_random[:])  # satisfied[:]

    return trials


def corp_image(image, objects, sz):
    min_jaccard = [0, 1, 3, 5, 7, 9]
    all_crop = {}
    for i in range(len(min_jaccard)):
        if 0 != min_jaccard[i]:
            if i == 6:
                print i
            jaccard = min_jaccard[i] / 10.0

            trials = generate_batch_samples(image, objects, jaccard)
            if len(trials) > 4:
                randidx = random.randint(0, len(trials) - 1)
                print jaccard, randidx, len(trials)
                lt = len(trials)
                coorAnno = trials[randidx]  # coordination & annotated
            elif len(trials) == 4:
                coorAnno = trials
            else:
                continue

            crop_imageAnno = corp(image, objects, coorAnno)
            all_crop[i] = resize_imgAnno(sz, *crop_imageAnno)
        else:
            all_crop[i] = image, copy.deepcopy(objects)

    return all_crop

#!/usr/bin/python3
import PIL.Image
import sys
import cv2
from pilgram import css
from pilgram import util

def normalize(image):
    return cv2.normalize(image, None, 25, 255, cv2.NORM_MINMAX)

def black_white_process(image):
    cb = util.or_convert(image, 'RGB')

    cs1 = util.radial_gradient(
            cb.size,
            [(212, 169, 175), (0, 0, 0)],
            [.55, 1.5])
    cm1 = css.blending.overlay(cb, cs1)

    cs2 = util.fill(cb.size, [216, 205, 203])
    cr = css.blending.color(cm1, cs2)

    cr = css.grayscale(cr, .5)
    cr = css.contrast(cr, .8)
    cr = css.brightness(cr, .9)
    return cr

def color_process(image):
    cb = util.or_convert(image, 'RGB')

    cs1 = util.fill(cb.size, [236, 205, 169, .15])
    cm1 = css.blending.multiply(cb, cs1)

    cs2 = util.fill(cb.size, [50, 30, 7, .4])
    cm2 = css.blending.multiply(cb, cs2)

    gradient_mask1 = util.radial_gradient_mask(cb.size, length=.55)
    cm = PIL.Image.composite(cm1, cm2, gradient_mask1)

    cs3 = util.fill(cb.size, [232, 197, 152, .8])
    cm3 = css.blending.overlay(cm, cs3)

    gradient_mask2 = util.radial_gradient_mask(cb.size, scale=.9)
    cm_ = PIL.Image.composite(cm3, cm, gradient_mask2)
    cr = PIL.Image.blend(cm, cm_, .6)  # opacity

    cr = css.brightness(cr, 1.05)
    cr = css.sepia(cr, .2)
    cr = css.contrast(cr, .9)
    cr = css.saturate(cr, .9)
    return cr
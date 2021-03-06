import time
from glob import glob
import tensorflow_datasets as tfds
import datetime
import os
import numpy as np
import tensorflow as tf
from matplotlib.pyplot import imsave


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def ad_loss(y_pred, y_true):
    return tf.reduce_mean(tf.math.squared_difference(y_pred, y_true))


def bce_loss(y_pred, y_true):
    return tf.keras.losses.BinaryCrossentropy(from_logits=True)(y_true, y_pred)


def id_loss(y_pred, y_true):
    return tf.reduce_mean(tf.abs(y_pred - y_true))


def cam_loss(source, non_source):
    identity_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.ones_like(source), logits=source))
    non_identity_loss = tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(labels=tf.zeros_like(non_source), logits=non_source))
    return identity_loss + non_identity_loss


def recon_loss(y_pred, y_true):
    return tf.reduce_mean(tf.abs(y_pred - y_true))


def normalize(image):
    image = tf.cast(image, tf.float32)
    image = (image / 127.5) - 1   # [-1,1]
    return image


def train_augment_horse2zebra(image, label, img_size):
    image = tf.image.resize(image, [img_size+30, img_size+30], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    image = tf.image.random_crop(image, size=[img_size, img_size, 3])
    image = tf.image.random_flip_left_right(image)
    image = tf.cast(image, dtype=tf.float32)
    image = normalize(image)
    return image


def test_augment_horse2zebra(image, label, img_size):
    image = tf.image.resize(image, [img_size, img_size])
    image = tf.cast(image, dtype=tf.float32)
    image = normalize(image)
    return image


def train_augment(image, img_size):
    image = tf.io.read_file(image)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [img_size+30, img_size+30], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    image = tf.image.random_crop(image, size=[img_size, img_size, 3])
    image = tf.image.random_flip_left_right(image)
    image = tf.cast(image, dtype=tf.float32)
    image = normalize(image)
    return image


def test_augment(image, img_size):
    image = tf.io.read_file(image)
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [img_size, img_size])
    image = tf.cast(image, dtype=tf.float32)
    image = normalize(image)
    return image


def image_save(real_images, fake_images, path, iter):
    assert real_images.shape == fake_images.shape
    real_images = real_images * 0.5 + 0.5  # [-1,1 -> 0,1]
    fake_images = fake_images * 0.5 + 0.5
    batch_size, h, w, c = real_images.shape
    figure = np.zeros((batch_size * h, w*2, c))
    suffix = '.jpg'
    idx = 0
    for real_img, fake_img in zip(real_images, fake_images):
        figure[h*idx:h*(idx+1), 0:w, ...] = real_img  # loc [0-255, 0-255, ...]
        figure[h*idx:h*(idx+1), w:, ...] = fake_img  # loc [0-255, 256-, ...]
        idx += 1
    path = os.path.join(path, 'iter_' + str(iter) + suffix)
    imsave(path, figure)

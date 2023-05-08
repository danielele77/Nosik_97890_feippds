"""
This module implements conversion of images from RGB to grayscale using two methods.
There are two methods:
1, CUDA (GPU),
2, HOST (CPU)
The main goal is make comparison of these two methods based on average time.
"""

__author__ = "Daniel Nošík"
__email__ = "xnosik@stuba.sk"
__license__ = "MIT"

import os
import cv2
import time
from numba import cuda
import numpy as np

PATH_TO_IMAGES = 'images_for_conversion'
CONVERTED_HOST = 'host_grayscale_images'
CONVERTED_DEVICE = 'device_grayscale_images'


@cuda.jit
def convert_img_to_grayscale(img_):
    """
    Converts the input image to grayscale using GPU.

    Arguments:
        img_ - image for conversion
    """
    img_height, img_width, _ = img_.shape
    row, col = cuda.grid(2)
    if row < img_height and col < img_width:
        r, g, b = img_[row, col]
        gray = 0.299 * r + 0.587 * g + 0.114 * b
        img_[row, col][0] = gray
        img_[row, col][1] = gray
        img_[row, col][2] = gray


def convert_img_to_grayscale_cpu(img_):
    """
    Converts the input image to grayscale using CPU.

    Arguments:
        img_ - image for conversion

    Return:
        converted image in grayscale
    """
    img_height, img_width, _ = img_.shape
    for x in range(img_height):
        for y in range(img_width):
            R, G, B = img_[x, y]
            gray_value = int(0.3 * R + 0.59 * G + 0.11 * B)
            img_[x, y] = gray_value

    return img_


if __name__ == '__main__':
    times_host = []  # times of conversions using CPU
    times_device = []  # times of conversions using GPU
    for file in os.listdir(PATH_TO_IMAGES):
        img = cv2.imread(PATH_TO_IMAGES + '/' + file, cv2.IMREAD_COLOR)  # load the image
        img_height, img_width, _ = img.shape  # retrieve height and width
        device_data = cuda.to_device(
            np.zeros((img_height, img_width, 3), dtype=np.uint8))  # allocate memory on GPU for the image
        device_data.copy_to_device(img)  # copy image to allocate memory on the GPU

        # calculations of the blocks count in the grid, based on the height and width of the image
        threads_per_block = (16, 16)
        blocks_per_grid_x = (img_height + threads_per_block[0] - 1) // threads_per_block[0]
        blocks_per_grid_y = (img_width + threads_per_block[1] - 1) // threads_per_block[1]
        blocks_per_grid = (blocks_per_grid_x, blocks_per_grid_y)
        start_time_cuda = time.time()
        convert_img_to_grayscale[blocks_per_grid, threads_per_block](
            device_data)  # calling device kernel, conversion of the image using
        end_time_cuda = time.time()
        conversion_time_device = end_time_cuda - start_time_cuda  # calculate time of GPU conversion
        times_device.append(conversion_time_device)

        start_time_host = time.time()
        img_from_host = convert_img_to_grayscale_cpu(img)  # conversion of the image using CPU
        end_time_host = time.time()
        conversion_time_host = end_time_host - start_time_host  # calculate time of CPU conversion
        times_host.append(conversion_time_host)

        img_from_device = device_data.copy_to_host(img)  # copy converted image from device memory to host
        cv2.imwrite(CONVERTED_HOST + '/gray_host_' + file, img_from_host)  # save converted image using CPU
        cv2.imwrite(CONVERTED_DEVICE + '/gray_device_' + file, img_from_device)  # save converted image using GPU

    # CALCULATE AND PRINT AVERAGE TIME FOR EACH METHOD
    print(f'Average time for conversion of images to grayscale using GPU: {np.array(times_device).mean()}')
    print(f'Average time for conversion of images to grayscale using CPU: {np.array(times_host).mean()}')

# CUDA

This module contains the implementation of two image conversion approaches from RGB to grayscale. The first approach is
to make conversions on the GPU (device), and the second is to use the CPU (host). The main goal is to compare these two
approaches based on the average conversion time of our image dataset. The image dataset consists of 16 color images with
different resolutions (e.g., 200 px x 200 px, 4288 px x 2848 px).

## Execution

The execution of this code is straightforward; just run it. The images from the images_for_conversion directory will be
converted to grayscale using the GPU and afterwards using the CPU. The conversion is realized by multiplying each pixel
of the color channels, RGB, by the **formula 0.299 * R + 0.587 * G + 0.114 * B**. This formula calculates the luminance,
or grayscale value, of a color represented by its RGB (red, green, and blue) values. The final result of the GPU and CPU
conversions is stored in device_grayscale_images, respectively, in the host_grayscale_images directory.

## The results

The average times of conversion images from our dataset are: **CPU: 10.1980s**, and **GPU: 0.0392**. As we see, the
approach to conversion using the GPU is significantly faster.

Below is an example of conversion with both approaches. The first image is the original, the second was converted using
a GPU, and the last one was converted using a CPU.

**The original one**

![](https://github.com/danielele77/Nosik_97890_feippds/blob/05/images_for_conversion/f16.jpg)

 

**Converted using GPU**

![](https://github.com/danielele77/Nosik_97890_feippds/blob/05/device_grayscale_images/gray_device_f16.jpg)

**Converted using CPU**

![](https://github.com/danielele77/Nosik_97890_feippds/tree/05/images_for_conversion)

import numpy as np
import argparse
import json
from PIL import Image
from os.path import join
import cv2
from matplotlib import pyplot as plt
import os
from scipy import ndimage
from skimage import morphology
from skimage.feature import peak_local_max
from skimage.morphology import watershed



DATA_DIRECTORY = '/media/chen/data/Lung_project/dataset/selected_labelID_2/'
SAVE_DIRECTORY = '/media/chen/data/Lung_project/dataset/test/'
SAVE_RGB_DIRECTORY = '/media/chen/data/Lung_project/dataset/test_rgb/'

# build Lookup table
num_class = 3
label_colours = [(224, 224, 224), (178, 102, 255), (255, 0, 0)]
table_R = np.zeros(256, np.uint8)
table_G = np.zeros(256, np.uint8)
table_B = np.zeros(256, np.uint8)

for i in range(num_class):
    table_R[i] = label_colours[i][0]
    table_G[i] = label_colours[i][1]
    table_B[i] = label_colours[i][2]


def decode_labels(mask):


    h, w = mask.shape
    mask_R = np.zeros((h, w), np.uint8)
    mask_G = np.zeros((h, w), np.uint8)
    mask_B = np.zeros((h, w), np.uint8)
    im = np.zeros((h, w, 3), np.uint8)

    cv2.LUT(mask, table_R, mask_R)
    cv2.LUT(mask, table_G, mask_G)
    cv2.LUT(mask, table_B, mask_B)

    im[:,:,2] = mask_R
    im[:,:,1] = mask_G
    im[:,:,0] = mask_B

    return im  

# def generate_tumor(hsv):
#     # class 2: Tumor : (255, 0, 0)
#     lower_red = np.array([20,90,30])
#     upper_red = np.array([255,255,240])
#     mask = cv2.inRange(hsv, lower_red, upper_red)
#     contours,hier = cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    
#     for cnt in contours:
#         cv2.drawContours(mask,[cnt],0,255,-1)

#     mask = cv2.bitwise_not(mask)
#     mask = np.divide(mask, 255).astype(np.bool)
    
#     mask = morphology.remove_small_holes(mask, min_size=500, connectivity=8, in_place=False)
    
#     mask = np.subtract(np.uint8(1), mask)


#     return mask

# def generate_background(hsv):
#     # class 1: Tissue : (224, 224, 224)
#     lower_red = np.array([0, 0, 210])
#     upper_red = np.array([255, 130, 255])
#     mask = cv2.inRange(hsv, lower_red, upper_red)

#     mask = cv2.bitwise_not(mask)

#     contours,hier = cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    
#     for cnt in contours:
#         cv2.drawContours(mask,[cnt],0,255,-1)
#     mask = cv2.bitwise_not(mask)
#     mask = np.divide(mask, 255).astype(np.bool)
#     mask = morphology.remove_small_holes(mask, min_size=500, connectivity=8, in_place=False).astype(np.uint8)


#     return mask

def remove_isolate_tumor(img):
  inverse_mask = (img != 2)
  inverse_mask = morphology.remove_small_holes(inverse_mask, min_size = 800, connectivity=8, in_place=False).astype(np.uint8)
  
  mask = np.subtract(np.uint8(1), inverse_mask)
  mask = morphology.remove_small_holes(mask, min_size = 1200, connectivity=8, in_place=False).astype(np.uint8)


  return mask

def remove_isolate_tissue(img):
  inverse_mask = (img != 1)
  inverse_mask = morphology.remove_small_holes(inverse_mask, min_size = 800, connectivity=8, in_place=False).astype(np.uint8)
  
  mask = np.subtract(np.uint8(1), inverse_mask)
  mask = morphology.remove_small_holes(mask, min_size = 1200, connectivity=8, in_place=False).astype(np.uint8)

  return mask
  


def select(data_dir, save_dir, save_rgb_dir):
    """
    Compute IoU given the predicted colorized images and 
    """
    image_path_list = 'label_to_select.txt'
    imgs = open(image_path_list, 'rb').read().splitlines()

    for ind in range(len(imgs)):
          img = cv2.imread(join(data_dir, imgs[ind].split('/')[-1]), cv2.CV_LOAD_IMAGE_GRAYSCALE)


          mask_tumor = remove_isolate_tumor(img)
          mask_tissue = remove_isolate_tissue(img)
          #cv2.imwrite(join(save_dir, imgs[ind].split('/')[-1]),diff*255)

          
          final_mask = np.zeros(mask_tumor.shape, np.uint8)
          final_mask = final_mask + mask_tissue + 2 * mask_tumor
          super_threshold_indices = (final_mask > 2)
          final_mask[super_threshold_indices] = 2
          

          final_mask_RGB = decode_labels(final_mask)
          cv2.imwrite(join(save_dir, imgs[ind].split('/')[-1]),final_mask)
          cv2.imwrite(join(save_rgb_dir, imgs[ind].split('/')[-1]),final_mask_RGB)

          print(join(save_dir, imgs[ind].split('/')[-1]))



def main(args):
    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir)
    if not os.path.exists(args.save_rgb_dir):
        os.makedirs(args.save_rgb_dir)
    select(args.data_dir, args.save_dir, args.save_rgb_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, default = DATA_DIRECTORY, help='directory which stores CityScapes val gt images')
    parser.add_argument('--save_dir', type=str, default = SAVE_DIRECTORY, help='directory which stores CityScapes val gt images')
    parser.add_argument('--save_rgb_dir', type=str, default = SAVE_RGB_DIRECTORY, help='directory which stores CityScapes val gt images')

    args = parser.parse_args()
    main(args)
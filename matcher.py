"""matcher.py

Functions in this file allows the user to match 2 images 
and get the fraction match between 2 images

Accepts only Mat (The Basic Image Container) format images
"""

import cv2
import numpy as np

def SURF_match(img1 , img2, hessianThreshold: int = 400, ratio_thresh: float = 0.7):
    """Give fraction match between 2 images using SURF and FLANN

    Parameters
    ----------
    img1 : Open CV image format,
    img2 : Open CV image format,
    hessianThreshold: Number of ORB points to consider in a image,
    ratio_thresh: (b/w 0 to 1) lower the number more serious the matching

    Returns
    -------
    float,
        returns a number from 0 to 1 depending on percentage match and returns -1 if any of the parameter is None
    """
    if img1 is None or img2 is None:
        raise Exception("img1 or img2 can't be none")
        return -1

    if ratio_thresh>1 or ratio_thresh<0:
        raise Exception("ratio_thresh not between 0 to 1")
        return -1


    detector = cv2.xfeatures2d.SURF_create(hessianThreshold)
    keypoints1, descriptors1 = detector.detectAndCompute(img1, None)
    keypoints2, descriptors2 = detector.detectAndCompute(img2, None)

    a1 = len(keypoints1)
    b1 = len(keypoints2)

    matcher = cv2.DescriptorMatcher_create(cv2.DescriptorMatcher_FLANNBASED)
    knn_matches = matcher.knnMatch(descriptors1, descriptors2, 2)

    good_matches = []
    for m, n in knn_matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append(m)

    c1 = len(good_matches)

    return ((2.0*c1)/(a1+b1))

def ORB_match(img1 , img2, hessianThreshold: int = 400, ratio_thresh: float = 0.7):
    """Give fraction match between 2 images using ORB and Brute Force Matching

    Parameters
    ----------
    img1 : Open CV image format,
    img2 : Open CV image format,
    hessianThreshold: Number of ORB points to consider in a image,
    ratio_thresh: (b/w 0 to 1) lower the number more serious the matching

    Returns
    -------
    float,
        returns a number from 0 to 1 depending on percentage match and returns -1 if any of the parameter is None
    """
    if img1 is None or img2 is None:
        raise Exception("img1 or img2 can't be none")
        return -1

    if ratio_thresh>1 or ratio_thresh<0:
        raise Exception("ratio_thresh not between 0 to 1")
        return -1

    orb = cv2.ORB_create(hessianThreshold)
    keypoints1, descriptors1 = orb.detectAndCompute(img1, None)
    keypoints2, descriptors2 = orb.detectAndCompute(img2, None)

    a1 = len(keypoints1)
    b1 = len(keypoints2)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches= bf.knnMatch(descriptors1,trainDescriptors=descriptors2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < ratio_thresh * n.distance:
            good_matches.append([m])

    c1 = len(good_matches)

    return ((2.0*c1)/(a1+b1))

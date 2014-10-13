#!/usr/bin/env python2


"""
Copyright (c) 2014, Patrick Louis <patrick at iotek do org>
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    1.  The author is informed of the use of his/her code. The author does not
        have to consent to the use; however he/she must be informed.
    2.  If the author wishes to know when his/her code is being used, it the
        duty of the author to provide a current email address at the top of
        his/her code, above or included in the copyright statement.
    3.  The author can opt out of being contacted, by not providing a form of
        contact in the copyright statement.
    4.  If any portion of the author's code is used, credit must be given.
            a. For example, if the author's code is being modified and/or
               redistributed in the form of a closed-source binary program,
               then the end user must still be made somehow aware that the
               author's work has contributed to that program.
            b. If the code is being modified and/or redistributed in the form
               of code to be compiled, then the author's name in the copyright
               statement is sufficient.
    5.  The following copyright statement must be included at the beginning of
        the code, regardless of binary form or source code form.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Except as contained in this notice, the name of a copyright holder shall not
be used in advertising or otherwise to promote the sale, use or other dealings
in this Software without prior written authorization of the copyright holder.

----

A mini-wrapper used to do perceptual hash comparison of JPEG images with the
same name but in different directories or to get a matrix of the distance from
the JPEG images in the same directory

"""

import glob
import os
import pHash
import itertools


def get_jpeg_files(directory):
    """
    get_jpeg_files :: String -> [String]

    Takes a directory
    Returns all files that ends in .jpeg
    """
    return map(
        lambda x: x.replace(directory+"/", ""),
        glob.glob(directory+"/*.jpeg")
    )


def get_files_in_dir(dir1, dir2):
    """
    get_files_in_dir :: String -> String -> ([String],[String])

    Takes 2 directory
    Returns all the files in those dirs that matches '*.jpeg'

    It is done this way because only jpeg and bmp images can be use with pHash
    """
    return (get_jpeg_files(dir1), get_jpeg_files(dir2))


def get_same_name_files(list_of_files1, list_of_files2):
    """
    get_same_name_files :: [String] -> [String] -> [String]

    Takes 2 lists of strings and returns the common names between them
    """
    return list(set(list_of_files1) & set(list_of_files2))


def get_all_common_files(dir1, dir2):
    """
    get_all_common_files :: String -> String -> [String]

    Takes 2 directory and return the list of common jpeg file
    names found in the two of them.
    """
    (all_files1, all_files2) = get_files_in_dir(dir1, dir2)
    return get_same_name_files(all_files1, all_files2)


def prepare_dir_input(directory):
    """
    prepare_dir_input :: String -> String

    Takes a directory as input and returns a well written directory string to
    be used latter on (absolute path and doesn't end with '/')
    It also checks if the directory exists
    """
    # removes the '/' at the end
    if (directory.endswith("/")):
        directory = directory.rstrip("/")
    # check if it's a dir & make sure it really exists
    if (not os.path.isdir(directory)) or (not os.path.exists(directory)):
        raise Exception("Problem accessing directory")
    # wrap it up with the absolute path
    return os.path.abspath(directory)


def get_hash_distance(image1, image2):
    """
    get_hash_distance :: String -> String -> Float

    Takes the 2 absolute location of 2 jpeg files
    Returns the perceptual hash distance between the images in percentage
    The lesser this value the greater the images ressembles
    """
    return (1-pHash.compare_images(image1, image2))*100


def calculate_distance_images(dir1, dir2):
    """
    calculate_distance_images :: String -> String -> { String : Float,.. }

    Takes 2 directories (should be prepared with the prepare_dir_input)
    Returns a dictionary associating the common jpeg image names with the
    perceptual hash distance calculated
    """
    common_image_names = get_all_common_files(dir1, dir2)
    images_dico = {}
    for image in common_image_names:
        images_dico[image] = get_hash_distance(dir1+"/"+image, dir2+"/"+image)
    return images_dico


def get_all_combinations(list_of_strings):
    """
    get_all_combinations :: [String] -> [(String,String)]

    Takes a list of strings
    Returns all the possible combinations of 2 elements (no repetition, no
    order)
    """
    return reduce(
        lambda c, y: c+[y],
        itertools.combinations(list_of_strings, 2),
        []
    )


def get_same_dir_distance(directory):
    """
    get_same_dir_distance :: String -> {(String, String) : Float}

    Takes a directory
    Returns the perceptual hash distance of all the jpeg files from one to the
    others
    """
    all_combinations = get_all_combinations(get_jpeg_files(directory))
    images_dico = {}
    for combination in all_combinations:
        images_dico[combination] = get_hash_distance(
            directory+"/"+combination[0],
            directory+"/"+combination[1]
        )
    return images_dico


def compare_same_dir(directory):
    """
    compare_same_dir :: String -> {(String, String) : Float,... }

    Takes a directory
    Returns a dictionary of the perceptual has distance between the combination
    of all jpeg files
    """
    return get_same_dir_distance(
        prepare_dir_input(directory)
    )


def compare_dirs(dir1, dir2):
    """
    compare_dirs :: String -> String -> { String : Float,... }

    Takes 2 directory
    Returns a dictionary of the common jpeg images perceptual hash distance
    """
    return calculate_distance_images(
        prepare_dir_input(dir1),
        prepare_dir_input(dir2)
    )

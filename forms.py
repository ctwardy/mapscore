# -*- coding: utf-8 -*-
"""
This module contains the zip file upload form, which takes zip archives of png
files, validates them, and uploads the contained pngs.

TODO::

    The current coding style being used is both inefficient and confusing. Error
    checking should be exchanged for try/except blocks with a custom
    InvalidImageError being raised to pass the reason for invalidity around.
    Additionally, a generator pipeline would be a clearer and more efficient way
    to extract, check, and process files from a zip archive.

"""
import re
import os
import sys
import logging
import zipfile
import tempfile

from django import forms
from PIL import Image, ImageOps

from mapscore.framework.models import Test
from mapscore.framework.models import Case
from mapscore.framework.models import Model


DIR_BIT = 16
KB64 = 1024 * 64


def zipped_file_isdir(info):
    """Takes info object for a file in a zip archive and checks if it is a
    directory.

    :type  info: zipfile.ZipInfo
    :param info: The information object for a file in a zip archive.
    :rtype:  bool
    :return: True if the file is a directory else False.

    """
    return info.external_attr & DIR_BIT


class ZipUploadForm(forms.Form):
    zipfile = forms.FileField(
        label='Select a zip file from your system',
        help_text=' '
    )

    def clean_zip_file(self):
        """ Checks if zip file is not corrupted, stores in-memory uploaded file
        to disk and returns path to stored file.

        """
        path = _file_path(self.cleaned_data['zipfile'])
        try:
            zf = ZipFile(path)
            bad_file = zf.testzip()
            if bad_file:
                raise forms.ValidationError(_('"%s" in the .zip archive is corrupt.') % bad_file)
            zf.close()
        except BadZipfile:
            raise forms.ValidationError(_('Uploaded file is not a zip file.'))

        return path

    def needs_unpacking(self, name, info):
        """ Returns True is file should be extracted from zip and False
        otherwise. Override in subclass to customize behaviour.  Default is to
        unpack all files except directories and meta files (names starts with
        '__') .

        """
        # skip directory entries
        if zipped_file_isdir(info):
            return False

        # skip meta files
        if name.startswith('__'):
            return False

        for ext in ['.png']:  # might also consider .jpeg, .jpg, and .gif
            if name.lower().endswith(ext):
                return True

        return False

    def is_valid_image(self, path):
        # TODO: return booleans and raise errors for invalid images

        try:
            # check if file is readable by PIL
            trial_image = Image.open(path)
            trial_image.verify()

            if trial_image.size[0] != 5001 or trial_image.size[1] != 5001:
                return "image wrong dimensions"

            bands = trial_image.getbands()
            if bands[:3] == ('R','G','B'):
                # it's an RGP, lets just convert it to grayscale
                # output_gr = trial_image.convert("LP")
                # trial_image.convert("LP")
                output_gr = ImageOps.grayscale(trial_image)
                output_gr.save(path,"PNG")
                return "ok"
            elif bands[0] in 'LP':  # actual lgrayscale
                 return "ok"
            else:  # image not grayscale
                 return "image is not a grayscale or RGB (?)"

        except ImportError:
            # Under PyPy, it is possible to import PIL. However, the underlying
            # _imaging C module isn't available, so an ImportError will be
            # raised. Catch and re-raise.
            # TODO: why catch only to reraise? Seems goofy.
            raise
        # Python Imaging Library doesn't recognize it as an image
        except Exception, valerror:
            return "image verification failed" + str(valerror)

        return "ok"

    def process_zip_file(self, chunksize=KB64):
        """Extract all files to temporary place and call process_file for each.

        :param int chunksize: The size of block in which compressed files are
            read.  Default is 64k. Do not set it below 64k because data from
            compressed files will be read in blocks >= 64k anyway.

        """
        # should contain zip file path
        zip_filename = self.cleaned_data['zipfile']
        zf = zipfile.ZipFile(zip_filename)
        names = zf.namelist()
        infos = zf.infolist()

        files_to_unpack = []
        for name, info in zip(names, infos):
            if self.needs_unpacking(name, info):
                files_to_unpack.append((name, info))

        case_list = []
        for counter, (name, info,) in enumerate(files_to_unpack):

            # extract file to temporary place
            fileno, path = tempfile.mkstemp()
            outfile = os.fdopen(fileno,'w+b')
            stream = zf.open(info)

            hunk = stream.read(chunksize)
            while hunk:
                outfile.write(hunk)
                hunk = stream.read(chunksize)

            outfile.close()

            # do something with extracted file
            case_list = self.process_file(
                case_list, path, name, info, counter, len(files_to_unpack))

        zf.close()
        good_count = 0
        bad_count = 0
        for index, (path, fname, file_size, model, case, status) in enumerate(case_list):
            if status != "ready":
                bad_count += 1
            else:
                good_count += 1
        return case_list
        #os.unlink(str(zip_filename))

    def process_file(self, case_list, path, name, info, file_num, files_count):

        # flatten directories
        fname = os.path.split(name)[1]
        status = "ready"

        # TODO: move this to `is_valid_image` method
        # only process valid images
        if re.match(r'^[A-Za-z0-9]+_[A-Za-z0-9]+\.png$', fname):
            temp = os.path.splitext(fname)[0]
            model, case = temp.split("_",2)
        else:
            model = "?"
            case = "?"
            status = "bad file name format"

        imagecheck = self.is_valid_image(path)
        if imagecheck != "ok":  # invalid image; should delete temp file
            status = imagecheck
            # os.unlink(path)  < -- but we're not going to?

        case_list.append((path, fname, str(info.file_size), model, case, status))
        is_last = (file_num == (files_count-1))
        return case_list

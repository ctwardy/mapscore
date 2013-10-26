# -*- coding: utf-8 -*-
from django import forms
import zipfile
import tempfile
import os
import sys
import logging
from mapscore.framework.models import Test
from mapscore.framework.models import Case
from mapscore.framework.models import Model

DIR_BIT = 16

class ZipUploadForm(forms.Form):
    zipfile = forms.FileField(
        label='Select a zip file from your system',
        help_text=' '
    )
    
    def clean_zip_file(self):
        ''' Checks if zip file is not corrupted, stores in-memory uploaded file
            to disk and returns path to stored file.
        '''
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
        ''' Returns True is file should be extracted from zip and
            False otherwise. Override in subclass to customize behaviour.
            Default is to unpack all files except directories and meta files
            (names starts with '__') .
        '''
        #skip directory entries
        isdir = info.external_attr & DIR_BIT
        if isdir:
            return False

        # skip meta files
        if name.startswith('__'):
            return False
            
#        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
        for ext in ['.png']:
            if name.lower().endswith(ext):
                return True
        return False            

    def is_valid_image(self, path):
        ''' Check if file is readable by PIL. '''
        from PIL import Image

        try:
            trial_image = Image.open(path)
            trial_image.verify()
            if trial_image.size[0] != 5001 or trial_image.size[1] != 5001:
                return "image wrong dimensions"
            bands = trial_image.getbands()
            if bands[:3] == ('R','G','B'):
                # it's an RGP, lets just convert it to grayscale
                output_gr = true_image.convert("LP")
                output_gr.save(path)            
            elif bands[0] in 'LP':
                 #actual lgrayscale
                 return "ok"
            # Image not grayscale
            else:
                 return "image is not a grayscale or RGB (?)"            
        except ImportError:
            # Under PyPy, it is possible to import PIL. However, the underlying
            # _imaging C module isn't available, so an ImportError will be
            # raised. Catch and re-raise.
            raise
        except Exception: # Python Imaging Library doesn't recognize it as an image
            return "image verification failed"
         # Check dimensions

        return "ok"

    def process_zip_file(self, chunksize=1024*64):
        '''
            Extract all files to temporary place and call process_file method
            for each.

            ``chunksize`` is the size of block in which compressed files are
            read. Default is 64k. Do not set it below 64k because data from
            compressed files will be read in blocks >= 64k anyway.
        '''

        zip_filename = self.cleaned_data['zipfile'] #should contain zip file path

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
            while True:
                hunk = stream.read(chunksize)
                if not hunk:
                    break
                outfile.write(hunk)

            outfile.close()
            
            # do something with extracted file
            case_list = self.process_file(case_list, path, name, info, counter, len(files_to_unpack))

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
        # only process valid images

        #parse the name
        import re
        if re.match(r'^[A-Za-z0-9]+_[A-Za-z0-9]+\.png$', fname):

            temp = os.path.splitext(fname)[0]
            model, case = temp.split("_",2)

        else:
            model = "?"
            case = "?"
            status="bad file name format"
        
        
        imagecheck = self.is_valid_image(path)
        if imagecheck != "ok":
            # image is invalid, we should delete temp file
            status = imagecheck       
            #os.unlink(path)
            
        case_list.append((path, fname, str(info.file_size), model, case, status))
        is_last = (file_num == (files_count-1))
      
        return case_list
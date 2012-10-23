#!/usr/bin/env python

NEW_DIR = './new/'

import sys, os, shutil
import hashlib

def are_identical(filename1, filename2):
    import hashlib

    file1 = open(filename1, 'r').read()
    file2 = open(filename2, 'r').read()

    if hashlib.sha512(file1).hexdigest() == hashlib.sha512(file2).hexdigest():
        return True
    else:
        return False

dir1 = sys.argv[1]
if not dir1.endswith('/'):
    dir1 += '/'
dir2 = sys.argv[2]
if not dir2.endswith('/'):
    dir2 += '/'

dir1_files = list(os.walk(dir1))[0][2]
dir2_files = list(os.walk(dir2))[0][2]

for f in dir2_files:
    if os.path.exists(dir1 + f):
        if not are_identical(dir1 + f, dir2 + f):
            # new photo for existing MP, copy to new/ dir
            if not os.path.exists(NEW_DIR):
                os.mkdir(NEW_DIR)
            shutil.copy(dir2 + f, NEW_DIR + f)
    else:
        # new photo
        if not os.path.exists(NEW_DIR):
            os.mkdir(NEW_DIR)
        shutil.copy(dir2 + f, NEW_DIR + f)


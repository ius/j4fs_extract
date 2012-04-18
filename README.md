Description
-----------
j4fs_extract.py extracts Samsung j4fs/lfs images (eg. param.lfs)

Requirements
------------

* python v2.7+

Usage example
-------------

Extract all files from param.lfs

    python j4fs_extract.py param.lfs

Extract files from image using alternate flash page (2048) and block (128k) size:

    python j4fs_extract.py -p 2048 -b 131072 param.lfs

Limitations
-----------

Input filesystem image is assumed to be clean


#!/usr/bin/python

import hashlib
import binascii

def hashfile(theFile, hasher, blocksize=65536):
	buf = theFile.read(blocksize);
	while(len(buf) > 0):
		hasher.update(buf);
		buf = theFile.read(blocksize);
	return binascii.hexlify(hasher.digest()).upper();


fileList = {'README.md', 'hashfiles.py'};
print [(fname, hashfile(file(fname, 'r'), hashlib.md5())) for fname in fileList];


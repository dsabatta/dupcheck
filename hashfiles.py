#!/usr/bin/python

import hashlib
import binascii
import os
import sys

def hashFile(theFile, hasher, blockSize=65536):
	buf = theFile.read(blockSize);
	while(len(buf) > 0):
		hasher.update(buf);
		buf = theFile.read(blockSize);
	return binascii.hexlify(hasher.digest()).upper();

def mergeHash(hash1, hash2):
	return binascii.hexlify(''.join(chr(ord(a) ^ ord(b)) for a,b in zip(binascii.unhexlify(hash1), binascii.unhexlify(hash2)))).upper();

if __name__ == "__main__":
#	fileList = {'README.md', 'hashfiles.py'};
#	print [(fname, hashFile(file(fname, 'r'), hashlib.md5())) for fname in fileList];

	for root, dirnames, filenames in os.walk('/tmp', topdown=False):
		for fname in filenames:
			fullpath = os.path.join(root, fname);
			try:
				sz = os.path.getsize(fullpath);
				if(sz > 0):
					print (fname, sz, hashFile(file(fullpath, 'r'), hashlib.md5()));
			except Exception as e:
				print "Failed on", fullpath, "with error", e;

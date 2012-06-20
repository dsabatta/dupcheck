#!/usr/bin/python

import hashlib
import binascii
import os
import sys
import sqlite3 as sql

def hashFile(theFile, hasher, blockSize=65536):
	buf = theFile.read(blockSize);
	while(len(buf) > 0):
		hasher.update(buf);
		buf = theFile.read(blockSize);
	return binascii.hexlify(hasher.digest()).upper();

def mergeHash(hash1, hash2):
	return binascii.hexlify(''.join(chr(ord(a) ^ ord(b)) for a,b in zip(binascii.unhexlify(hash1), binascii.unhexlify(hash2)))).upper();

def initDB(dbName):
	conn = sql.connect(dbName);
	
	c = conn.cursor();
	c.executescript("""
		DROP TABLE IF EXISTS Files;
		CREATE TABLE Files(Id INTEGER PRIMARY KEY AUTOINCREMENT, MD5Sum TEXT, Filename TEXT, Path TEXT, Size INT);
		""");
	c.close();
	
	return conn;

#def useDB():
#	c = conn.cursor();
#	c.execute("INSERT INTO Files(MD5Sum, Filename, Path, Size) VALUES('ABCDEF', 'aaa.ddd', '/abc/def/ghi', 12345);");
#	c.close();

def populateDB(db, rootPath):
	c = db.cursor();
	
	for root, dirnames, filenames in os.walk(rootPath, topdown=False):
		jointHash = "";
		for fname in filenames:
			fullpath = os.path.join(root, fname);
			try:
				sz = os.path.getsize(fullpath);
				if(sz > 0):
					fileHash = hashFile(file(fullpath, 'r'), hashlib.md5());
					if len(jointHash) == 0:
						jointHash = ''.join('0' for x in fileHash);
					jointHash = mergeHash(jointHash, fileHash);
					c.execute("INSERT INTO Files(MD5Sum, Filename, Path, Size) VALUES(?, ?, ?, ?);", (fileHash, fname, fullpath, sz));
			except Exception as e:
				print "Failed on", fullpath, "with error", e;
		
		for dname in dirnames:
			fullpath = os.path.join(root, dname);
			print "Looking for:", fullpath;
			c.execute("SELECT MD5Sum FROM Files WHERE Path=:fullpath;", {"fullpath": fullpath});
			row = c.fetchone();
			if not row is None:
				if len(jointHash) == 0:
					jointHash = ''.join('0' for x in row[0]);
				jointHash = mergeHash(jointHash, row[0]);
			else:
				print "Not found!";
		
		c.execute("INSERT INTO Files(MD5Sum, Filename, Path, Size) VALUES(?, ?, ?, ?);", (jointHash, os.path.split(root)[1], root, 0));
	
	c.close();

if __name__ == "__main__":
	# Check for arguments
	if len(sys.argv) != 2:
		print "Missing arguments...";
		sys.exit(-1);
		
	# Get root path
	rootPath = sys.argv[1];
	print "Root path:", rootPath;
	
	# Create database
	db = initDB(":memory:");
	populateDB(db, rootPath);
	
	c = db.cursor();
	c.execute("SELECT * FROM Files");
	rows = c.fetchall();
	for row in rows:
		print row;


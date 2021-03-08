import random
import string
import base64
import sys
from pwn import *

key = "sup3rs3cur3h4drc0d3dk3yt0x0r3v3ryth1ng"

def decoder(s):
	std_base64chars  = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
	my_base64chars = "ZYXWVUTSRQPONMLKJIHGFEDCBAabcdefghijklmnopqrstuvwxyz0123456789+/"
	return dxor(s.translate(string.maketrans(my_base64chars, std_base64chars)),key)

def dxor(d,k = key):
	r = ""
	d = base64.b64decode(d);
	for x in range(len(d)):
		r += chr(ord(d[x]) ^ ord(k[x]))
	return r

p = process(["./leeTarjeta",sys.argv[1],sys.argv[2],"dump"])

cards = []

for _ in range(100):
	cards.append(p.recvline())

clean = []

for c in cards:
	clean.append(c.split("\t"))

fortress = ''

for c in clean[2:]:
	x = [i for i in c if i]
	if "87" in x[0]:
		fortress = decoder(x[2])

p.close()

x = process(["./leeTarjeta",sys.argv[1],sys.argv[2],"validate",fortress])

print(x.recvall())

x.close()
# from pytessosx.pytesser import *

# im = Image.open('pytessosx/test2.jpg')
# text = image_to_string(im)
# print text

# import sys

# pdf = file('pytessosx/test.pdf', "rb").read()

# startmark = "\xff\xd8"
# startfix = 0
# endmark = "\xff\xd9"
# endfix = 2
# i = 0

# print 'here'

# njpg = 0
# while True:
# 	istream = pdf.find("stream", i)
# 	print istream
# 	if istream < 0:
# 	    break
# 	istart = pdf.find(startmark, istream, istream+20)
# 	print istart
# 	if istart < 0:
# 	    i = istream+20
# 	    continue
# 	iend = pdf.find("endstream", istart)
# 	if iend < 0:
# 	    raise Exception("Didn't find end of stream!")
# 	iend = pdf.find(endmark, iend-20)
# 	if iend < 0:
# 	    raise Exception("Didn't find end of JPG!")
# 	istart += startfix
# 	iend += endfix
# 	print "JPG %d from %d to %d" % (njpg, istart, iend)
# 	jpg = pdf[istart:iend]
# 	jpgfile = file("jpg%d.jpg" % njpg, "wb")
# 	jpgfile.write(jpg)
# 	jpgfile.close()     
# 	njpg += 1
# 	i = iend
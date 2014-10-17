import sys
import os
import time
from ra_header import *
from ra_format import *

def main(infile):

    i = 0
    total = 0

# open the input file

    fp = open(infile, "r")

    header = ra_header_struct()
    td = ra_td()

# read the first header
    fp.readinto(header)

# Now loop, reading all headers and data

    headers = []
    data = []

# loop, reading headers, until no more are found

    print "reading header"
    while fp.readinto(header) == sizeof(header):

        print "Header ", i
        print "Start time for interval considered in first report: ", header.tvStart.tv_sec, header.tvStart.tv_usec
        print "Period at which this packet is updated: ", header.T0
        print "time is seconds from tvstart to start of this report: ", header.fStart
        print "sequence number: ", header.iSeqNo
        headers.append(header)
        data.append(fp.readinto(td))
        i = i + 1

    print "Read ", i, "Headers + Data"
    fp.close() 

if __name__ == "__main__":
    infile = "/home/scratch/groups/rfi/rprestag/frsc0619.dat"
    main(infile)
 

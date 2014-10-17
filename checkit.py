import mmap
import sys
import os
import time
from ra_header import *
from ra_format import *
from copy import deepcopy 

def read_frsc_data(frscfile):
    doPrint = False
    i = 0
    total = 0

# open the input file

    fp = open(frscfile, "r")

    tempHeader = ra_header_struct()
    td = ra_td()

# read the first header
    fp.readinto(tempHeader)

# Now loop, reading all remaining headers and data

    headers = []
    data = []

# loop, reading headers, until no more are found

    while fp.readinto(tempHeader) == sizeof(tempHeader):
        if doPrint:
            print "Header ", i
            print "Start time for interval considered in first report: ", tempHeader.tvStart.tv_sec, tempHeader.tvStart.tv_usec
            print "Period at which this packet is updated: ", tempHeader.T0
            print "time is seconds from tvstart to start of this report: ", tempHeader.fStart
            print "sequence number: ", tempHeader.iSeqNo
        headers.append(deepcopy(tempHeader))

        fp.readinto(td)
        data.append(deepcopy(td))
        i = i + 1

    print "Read ", i, "Headers + Data"
    fp.close()
    return headers, data

def read_guppi_header(header):

    loc = header.find("BLOCSIZE")
    blocsize = int(header[loc:loc+80].split("=")[1])

    loc = header.find("OBSNCHAN")
    obsnchan = int(header[loc:loc+80].split("=")[1])

    loc = header.find("OVERLAP")
    overlap = int(header[loc:loc+80].split("=")[1])

    loc = header.find("NPOL")
    npol = int(header[loc:loc+80].split("=")[1])

    loc = header.find("NBITS")
    nbits = int(header[loc:loc+80].split("=")[1])

    loc = header.find("TBIN")
    tbin = float(header[loc:loc+80].split("=")[1])

    return blocsize, obsnchan, overlap, npol, nbits, tbin


def main(infile, frscfile):

    Diag = True

# get the frsc information

    print "Reading FRSC Info..."
    print
    headers, frscdata = read_frsc_data(frscfile)
    numFrscHeaders = len(headers)

    for i in range(numFrscHeaders):
        print i, frscdata[i].tdac[256].xi.mean, frscdata[i].tdac[0].xi.rms


    print "Goodbye."

if __name__ == "__main__":
    frscfile = "/home/scratch/groups/rfi/rprestag/frsc0619.dat"
#    infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"
    infile = "/lustre/pulsar/scratch/RFI/richard.raw"

    main(infile, frscfile)

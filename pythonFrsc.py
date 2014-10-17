import mmap
import sys
import os
import time
from ra_header import *
from ra_format import *
from ra_analyze import *
from copy import deepcopy 
import numpy as np

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

    loc = header.find("END     ")
    headerSize = loc + 80

    return headerSize, blocsize, obsnchan, overlap, npol, nbits, tbin

def main(infile,outfile):

    Diag = True

# This number is required to be longer than any GUPPI header
    MAX_HEADER_LEN = 8192

# This number was derived manually, but could have been derived by the code
# it is the number of frsc blocks that fit into a GUPPI block, excluding the overlap region
    FB_PER_GB = 252

# memmap the GUPPI data

    fp = np.memmap(infile,dtype='int8',mode='r')
    fileLen = fp.size

# initialize empty arrays for the results

    xiMean = []
    xqMean = []
    yiMean = []
    yqMean = []
    xxMean = []
    xxRMS  = []
    yyMean = []
    yyRMS  = []

# Now iterate over the GUPPI blocks, one by one

    loc = 0
    guppiHeader = 0
    while (loc < fileLen):
        header = np.copy(fp[loc:loc+MAX_HEADER_LEN]).tostring()
        headerSize, blockSize, obsnchan, overlap, npol, nbits, tbin = read_guppi_header(header)
        if Diag:
            print
            print "Location", loc
            print "Header", guppiHeader
            print "Header size", headerSize
            print "Block size", blockSize

        loc = loc + headerSize
        guppiHeader = guppiHeader + 1

# figure out the basic size of the GUPPI block

        ndim = blockSize / (obsnchan*npol*(nbits/8))
        blockTime = tbin * ndim
        ndim1 = ndim -overlap
        uniqueTime = tbin * ndim1
        frscLength = ndim1 / FB_PER_GB
        #print frscLength, ndim/FB_PER_GB
        #sys.exit()

        if Diag:
            print "Derived Quantities:"
            print "   There are", ndim, "time samples for each frequency channel"
            print "   There are", ndim1, "non-overlap time samples for each frequency channel"
            print "   Block time in seconds is", blockTime
            print "   Block time in seconds is (no overlap)", uniqueTime
            print "   There are", frscLength, "samples per FRSC block"
            print "   TBIN is", tbin

# now iterate over all the FRSC blocks in this guppi block

#        frscLoc = loc
        #print FB_PER_GB = 252
        for i in range(FB_PER_GB):
            #if Diag:
                #print "Processing FRSC block", i, "\r",

# get the data to process. We need obsnchan small chunks of data, selected with the right time offset in each frequency block

            part = []
            for j in range(obsnchan):
                partStart = loc + (j * ndim * npol) + (i * frscLength * npol)
                #if j==0 and i==0: print partStart
                partEnd = partStart + (frscLength * npol)
                #print i, j, partStart, partEnd
                part.append(fp[partStart:partEnd])
                #print partEnd-partStart  = 8192

        #print partEnd
        #print np.array(part).shape
            chunk = np.vstack(part)
            chunk = chunk.reshape((obsnchan,-1,npol))
            print chunk.shape, chunk[20,:10,0]
            sys.exit()

#            if Diag:
#                print "array shape of: ", chunk.shape
#                print "should be: ", obsnchan, frscLength, npol

# get the statistics
#            res = ra_analyze(chunk)
#            xiMean.append(res[0])
#            xqMean.append(res[1])
#            yiMean.append(res[2])
#            yqMean.append(res[3])
#            xxMean.append(res[4])
#            xxRMS.append(res[5])
#            yyMean.append(res[6])
#            yyRMS.append(res[7])

# and increment the locator within this GUPPI block

#            frscLoc = frscLoc + (obsnchan * frscLength * npol)

# Doe with this GUPPI block. Increment locator to end of the block (including overlap)

        loc = loc + blockSize

# all done. Stack the arrays vertically, and write to file

    xiMeanWrite = np.vstack(xiMean)
    xqMeanWrite = np.vstack(xqMean)
    yiMeanWrite = np.vstack(yiMean)
    yqMeanWrite = np.vstack(yqMean)
    xxMeanWrite = np.vstack(xxMean)
    xxRMSWrite  = np.vstack(xxRMS)
    yyMeanWrite = np.vstack(yyMean)
    yyRMSWrite  = np.vstack(yyRMS)

    if Diag:
        print "xxMean is now shaped: ", xxMeanWrite.shape

    np.savez(outfile, xiMean=xiMeanWrite, xqMean=xqMeanWrite,
                         yiMean=yiMeanWrite, yqMean=yqMeanWrite,
                         xxMean=xxMeanWrite, xxRMS=xxRMSWrite,
                         yyMean=yyMeanWrite, yyRMS=yyRMSWrite)
    print "Goodbye."

if __name__ == "__main__":
#    infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"
    infile = "/lustre/pulsar/scratch/RFI/copy.raw"
    outfile = "/lustre/pulsar/scratch/RFI/copy.npz"

    main(infile,outfile)

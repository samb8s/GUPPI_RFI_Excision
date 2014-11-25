import mmap
import sys
import os
import time
from ra_header import *
from ra_format import *
from ra_analyze import *
from copy import deepcopy 
import numpy as np

import robust_stats as rs

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
        frscLength = ndim / FB_PER_GB

        if Diag:
            print "Derived Quantities:"
            print "   There are", ndim, "time samples for each frequency channel"
            print "   There are", ndim1, "non-overlap time samples for each frequency channel"
            print "   Block time in seconds is", blockTime
            print "   Block time in seconds is (no overlap)", uniqueTime
            print "   There are", frscLength, "samples per FRSC block"
            print "   TBIN is", tbin

# get the data from the guppi block
        partStart = loc
        partEnd = loc + obsnchan*ndim*npol

        chunk = np.array(fp[partStart:partEnd])

        # reshape, remove overlap samples, then reshape again
        chunk.shape = (obsnchan, -1)
        chunk = np.delete(chunk, np.s_[-npol*overlap::], 1)
        chunk.shape = (obsnchan,-1,npol)

        #print chunk.shape
        #sys.exit()
        xi = chunk[:,:1024,0]; xq = chunk[:,:1024,1]
        xx = xi.astype(float)*xi.astype(float) + xq.astype(float)*xq.astype(float)
        #rs.plotData(xx)
        #print chunk.mean(axis=1), chunk.mean(axis=2)
        cleaned = rs.hampel_filter_2d(xx, 3.0)
        #cleaned = rs.hampel_2d_fast(xx, 3.0)
        #rs.plotData(cleaned)

        # now need to implement the hempel filter stuff on "chunk"
        
        sys.exit()

# Done with this GUPPI block. Increment locator to end of the block (including overlap)

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

import mmap
import sys
import os
import time
from ra_header import *
from ra_format import *
from ra_analyze import *
from copy import deepcopy 
import numpy as np
from scipy.ndimage.filters import median_filter

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

def main(infile,frscfile):

    Diag = True

# This number is required to be longer than any GUPPI header
    MAX_HEADER_LEN = 8192

# This number was derived manually, but could have been derived by the code
# it is the number of frsc blocks that fit into a GUPPI block, excluding the overlap region
    FB_PER_GB = 252

# This is the threshold at which to apply the statustics (probably should be an input number)

    FRSC_THRESH = 0.2

# memmap the GUPPI data

    fp = np.memmap(infile,dtype='int8',mode='r+')
    fileLen = fp.size

# read in the arrays which have been created by pythonFrsc.py

    npzfile = np.load(frscfile)
    xiMean = npzfile['xiMean']
    xqMean = npzfile['xqMean']
    yiMean = npzfile['yiMean']
    yqMean = npzfile['yqMean']
    xxMean = npzfile['xxMean']
    xxRMS  = npzfile['xxRMS']
    yyMean = npzfile['yyMean']
    yyRMS  = npzfile['yyRMS']

# "blur" the xi, etc values

    xiMean = median_filter(xiMean, size=7,mode="nearest")
    xqMean = median_filter(xqMean, size=7,mode="nearest")
    yiMean = median_filter(yiMean, size=7,mode="nearest")
    yqMean = median_filter(yqMean, size=7,mode="nearest")


    print xiMean.shape

# Now iterate over the GUPPI blocks, one by one

    loc = 0
    guppiHeader = 0
    iFrscArray = 0    # location in the FRSC aray
    iReplaced = 0     # number replaced

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
        for i in range(FB_PER_GB):
            if Diag:
                print "Processing FRSC block", i

 # use the xx statistics as the discriminant

            mean = xxMean[iFrscArray,:]
            rms  = xxRMS[iFrscArray,:]
            ratio = np.absolute((rms/mean)-1.0)

# get the data to process, and replace values by the filtered mean equivalent as necessary

            for j in range(obsnchan):
                if ratio[j] > FRSC_THRESH:
                    if Diag:
                        print "FRSC Block, chan ", iFrscArray, j,  "exceeds threshold"
                    iReplaced = iReplaced + 1
                    partStart = loc + (j * ndim * npol) + (i * frscLength * npol)
                    partEnd = partStart + (frscLength * npol)
                    for rep in range(partStart, partEnd, npol):
                        fp[rep] = np.int8(xiMean[iFrscArray,j])
                        fp[rep+1] = np.int8(xqMean[iFrscArray,j])
                        fp[rep+2] = np.int8(yiMean[iFrscArray,j])
                        fp[rep+3] = np.int8(yqMean[iFrscArray,j])
#                        fp[rep] = 100
#                        fp[rep+1] = 100
#                        fp[rep+2] = 100
#                        fp[rep+3] = 100


# and increment the FRSC block counter

            iFrscArray = iFrscArray + 1

# Doe with this GUPPI block. Increment locator to end of the block (including overlap)

        loc = loc + blockSize

# all done. Flush the changes to disk

    fp.flush()

    print
    print "replaced ", iReplaced, "values"

    print "writing new file..."
    outfile = "/lustre/pulsar/scratch/RFI/copy.raw"
    fpo = np.memmap(outfile,dtype='int8', mode="w+", shape = (fileLen))
    fpo[:] = fp[:]
    fpo.flush()

    print "Goodbye."

if __name__ == "__main__":
#    infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"
    infile = "/lustre/pulsar/scratch/RFI/frsced.raw"
    frscfile = "/lustre/pulsar/scratch/RFI/richard.npz"

    main(infile,frscfile)

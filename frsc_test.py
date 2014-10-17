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
        print td.tdac[1].u.mean
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

    for k in range(numFrscHeaders):
        print frscdata[k].tdac[1].u.mean


# now the GUPPI data

    fin = open(infile,"r+w")
 #   fout = open(outfile,"w")

    mm = mmap.mmap(fin.fileno(), 0)
    filesize = mm.size()
    print "GUPPI file size is ", filesize

    pos = 0
    guppiBlock = -1
    frscBlock = 0
    newGuppiBlock = True
    headerlen = 0
    written = 0

# loop over all FRSC blocks

    while (frscBlock < numFrscHeaders):
        if Diag:
            print "Frsc Block", frscBlock
        frscHeader = headers[frscBlock]
        frscStart = frscHeader.fStart
        frscInterval = frscHeader.T0
        frscEnd = frscStart + frscInterval
        if Diag:
            print "frscStart", frscStart, "frscEnd", frscEnd, "frscInterval", frscInterval

# are we in a new GUPPI block?

        if newGuppiBlock:
            guppiBlock = guppiBlock + 1

# It seems I cannot always find the "END"? Just use the length of the first header block

            if headerlen == 0:
                headerlen  = mm.find("END     ") + 80
                header = mm.read(headerlen)
                blocsize,obsnchan,overlap,npol,nbits,tbin = read_guppi_header(header)

            print "Guppi Block", guppiBlock, "header is bytes", pos, "to", pos+headerlen
            pos = pos + headerlen

            if Diag:
                print
                print "Guppi Block", guppiBlock
                print filesize, pos, headerlen
                print

                print "Basic Quantities for GUPPI block", guppiBlock
                print "   Blocsize is", blocsize
                print "   There are", obsnchan, "frequency channels"
                print "   The overlap is", overlap, "samples"
                print "   There are", npol, "polarizations"
                print "   There are", nbits, "bits per sample"
                print "   Length of bin is", tbin, "seconds"

            ndim = blocsize / (obsnchan*npol*(nbits/8))
            blockTime = tbin * ndim
            ndim1 = blocsize / (obsnchan*npol*(nbits/8))-overlap
            uniqueTime = tbin * ndim1

            if Diag:
                print "Derived Quantities:"
                print "   There are", ndim, "time samples for each frequency channel"
                print "   Block time in seconds is", blockTime
                print "   Block time in seconds is (no overlap)", uniqueTime


            startTime = uniqueTime * guppiBlock
            guppiEnd = startTime + uniqueTime
            print "Guppi Block", guppiBlock, "data is bytes", pos, pos + blocsize
#            pos = pos + blocsize
            newGuppiBlock = False
        else:

# no new GUPPI block needed; start time is just start of this FRSC block

            startTime = frscStart

        if Diag:
            print "guppi block: ", guppiBlock, "end time: ", guppiEnd, "frscBlock: ", frscBlock, "end time ", frscEnd

# FRSC block is inside GUPPI block

        if (frscEnd <= guppiEnd):
            endTime = frscEnd
            if Diag:
                print "using frsc statistics from ", frscBlock
                print "times", startTime, "to ", endTime
                print "do processing based on frsc block", frscBlock
            frscBlock = frscBlock + 1

# FRSC block extends past end of GUPPI block

        else:
            endTime = guppiEnd
            if Diag:
                print "frscBlock extends past end of guppiBlock."
                print "Use frscStatistics from block", frscBlock, "until end of guppi block", guppiBlock
                print "times", startTime, "to ", endTime
                print "do processing based on frsc block", frscBlock
            if ((pos+blocsize) == filesize):
                print "We have reached the end of the GUPPI file"
                print "Guppi Block", guppiBlock, "finished with bytes", pos, "to", pos+blocsize
                break
            else:
                print "Guppi Block", guppiBlock, "finished with bytes", pos, "to", pos+blocsize
                newGuppiBlock = True
                pos = pos + blocsize

# ok, we have the startTime and endTime within the GUPPI block. Now process all frequency channels

        stride = blocsize / obsnchan
        nStart = int((startTime - (uniqueTime*guppiBlock)) / tbin)
        nEnd = nStart + int ((endTime - startTime) / tbin)
        if Diag:
            print "nStart, nEnd = ", nStart, nEnd
        for chan in range(obsnchan):
            for time in range(nStart, nEnd):

# flag every 10th frequency channel, and 1st 100 of every time slice

                    if (not (chan % 10)) or (time < nStart + 500):

                        for pol in range(npol):
                            loc = (chan * stride) + (time * npol) + pol 
                            mm[pos + loc] = "\x00"

    
# all done

    mm.flush()
    fin.close()

    print "Goodbye."

if __name__ == "__main__":
    frscfile = "/home/scratch/groups/rfi/rprestag/frsc0619.dat"
#    infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"
    infile = "/lustre/pulsar/scratch/RFI/richard.raw"

    main(infile, frscfile)

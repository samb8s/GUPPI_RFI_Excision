import mmap


infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"
outfile = "/lustre/pulsar/scratch/RFI/richard.raw"

fin = open(infile,"r")
fout = open(outfile,"w")

frscInterval = 9.999360e-03

mm = mmap.mmap(fin.fileno(), 0, prot=mmap.PROT_READ)
filesize = mm.size()
print "file is ", filesize, "bytes long"

# find the data size from the first header.

pos = mm.find("BLOCSIZE")
mm.seek(pos)
blocsize = int(mm.read(80).split("=")[1])

# find the length in seconds of a data block from the first header

# TBIN is sample period in seconds
# Number of samples per channel in the block is:
#
# BLOCSIZE/(OBSNCHAN*NPOL*(NBITS/8))

pos = mm.find("TBIN")
mm.seek(pos)
tbin = float(mm.read(80).split("=")[1])

pos = mm.find("OBSNCHAN")
mm.seek(pos)
obsnchan = int(mm.read(80).split("=")[1])

pos = mm.find("NPOL")
mm.seek(pos)
npol = int(mm.read(80).split("=")[1])

pos = mm.find("NBITS")
mm.seek(pos)
nbits = int(mm.read(80).split("=")[1])

pos = mm.find("OVERLAP")
mm.seek(pos)
overlap = int(mm.read(80).split("=")[1])

ndim = blocsize / (obsnchan*npol*(nbits/8))
blocktime = tbin * ndim
sampPerFrsc = frscInterval / tbin

print "there are", obsnchan, "frequency channels"
print "there are", npol, "polarizations"
print "there are", ndim, "time samples for each frequency channel"
print "block time in seconds is: ", blocktime
print "there are: ", sampPerFrsc, "time samples per frsc interval"

shortTime = tbin * (ndim - overlap)

frscPerGuppi = shortTime / frscInterval

print "non-overlap time in seconds is: ", shortTime
print "frsc per guppi is: ", frscPerGuppi

# find the length of the first header. The header ends with an 80 char line 
# starting with "END". Can't just search for END on its own, as 
# FRONTEND will count

headerlen  = mm.find("END     ") + 80

# assuming all headers and datablocks are the same size, loop through the 
# data. The last data block may be smaller than the others?

i = 0

frsctime = 0

while True:
    pos = i * (headerlen + blocsize)
    if (pos >= filesize):
        break
    else:
        print i
        mm.seek(pos)
        chunk = mm.read(headerlen+blocsize)
        endOfBlock = blocktime * (i+1)
        samp = 0
        while (frsctime < endOfBlock):
            print endOfBlock, frsctime, samp
            frsctime = frsctime + frscInterval
            samp = samp + 1
        fout.write(chunk)
        i = i + 1

print (filesize - pos), "bytes remain"

fin.close()
fout.close()


import mmap


infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"

fin = open(infile,"r")

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

pos = mm.find("OVERLAP")
mm.seek(pos)
overlap = int(mm.read(80).split("=")[1])

pos = mm.find("NPOL")
mm.seek(pos)
npol = int(mm.read(80).split("=")[1])

pos = mm.find("NBITS")
mm.seek(pos)
nbits = int(mm.read(80).split("=")[1])

ndim = blocsize / (obsnchan*npol*(nbits/8))
blocktime = tbin * ndim

ndim1 = blocsize / (obsnchan*npol*(nbits/8))-overlap
shorttime = tbin * ndim1

sampPerFrsc = frscInterval / tbin
FrscperBlock = shorttime /frscInterval


print "there are", obsnchan, "frequency channels"
print "there are", npol, "polarizations"
print "there are", ndim, "time samples for each frequency channel"
print "block time in seconds is: ", blocktime
print "block time in seconds is (no overlap): ", shorttime
print "there are: ", sampPerFrsc, "time samples per frsc interval"
print "there are: ", FrscperBlock, "frsc samples per guppi block"
fin.close()

# Now simulate how we would step through the file.

guppiBlocks = 10
guppiBlock = 0
frscBlock = 0
newGuppiBlock = True

while True:
    guppiEnd = shorttime * (guppiBlock + 1)

# Loop through all the frsc blocks that fit fully in this guppi block. Don't increment frsc Block for partial times

    while True:
        if newGuppiBlock:
            startTime = shorttime * guppiBlock
            print "Reading Guppi Block", guppiBlock, "starting at:", startTime
            newGuppiBlock = False
        else:
            startTime = frscBlock * frscInterval
            
        frscEnd = frscInterval * (frscBlock+ 1) 
        print "guppi block: ", guppiBlock, "end time: ", guppiEnd, "frscBlock: ", frscBlock, "end time ", frscEnd
        if (frscEnd > guppiEnd):
            print "frscBlock extends past end of guppiBlock."
            print "Use frscStatistics from block", frscBlock, "until end of guppi block", guppiBlock
            print "times", startTime, "to ", guppiEnd
            break
        else:
            print "using frsc statistics from ", frscBlock
            print "times", startTime, "to ", frscEnd
            frscBlock = frscBlock + 1

    guppiBlock = guppiBlock + 1
    newGuppiBlock = True
    if guppiBlock > guppiBlocks:
        print "We have reached the end of the guppi data file."
        break

print "Goodbye."
# all done

import os
import mmap
from subprocess import call

#infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"
infile = "/lustre/pulsar/scratch/RFI/richard.raw"

call(["ls", "-l", infile])

ossize = os.path.getsize(infile)
print "os says file is ", ossize, "bytes long"

fin = open(infile,"r")

mm = mmap.mmap(fin.fileno(), 0, prot=mmap.PROT_READ)
filesize = mm.size()
print "mmap says file is ", filesize, "bytes long"

fin.close()



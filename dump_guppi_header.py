import mmap

infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"

f = open(infile,"r")

mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

headerlen  = mm.find("END     ") + 80

print mm.read(headerlen)

import mmap

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


def main():

    infile = "/lustre/pulsar/scratch/RFI/56827/guppi_56827_NGC6946_0001.0000.raw"
    fin = open(infile,"r")

    mm = mmap.mmap(fin.fileno(), 0, prot=mmap.PROT_READ)
    filesize = mm.size()
    print "file is ", filesize, "bytes long"

    headerNum = 0
    pos = 0

    while True:

# read the header and report...

        headerlen  = mm.find("END     ") + 80
        header = mm.read(headerlen)
        pos = pos + headerlen
        blocsize,obsnchan,overlap,npol,nbits,tbin = read_guppi_header(header)

        print "Basic Quantities:"
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

        print "Derived Quantities:"
        print "   There are", ndim, "time samples for each frequency channel"
        print "   Block time in seconds is", blockTime
        print "   Block time in seconds is (no overlap)", uniqueTime

# read the data

        chunk = mm.read(blocsize)
        pos = pos + blocsize
        if pos >= filesize:
            break
# all done

    fin.close()
    print "Goodbye."

if __name__ == "__main__":
    main()

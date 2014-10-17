"""

frsc_read.py - Show output of frsc when written to file

R. Prestage 04 February 2014

Based on frsc_read.c by S.W. Ellingson, Virginia Tech, 2014 Jan 25

COMMAND LINE SYNTAX, INPUT, OUTPUT: 
> python frsc_read.py <infile> <ch>
  <infile>:  path/name of a frsc output file
  <ch>:      if specified, info specific to channel <ch> contained in eType=1 reports is written to "frsc_read.dat"
             valid values are [1..nCh]; values of 0 or less are ignored

"""


import sys
import os
import time
from ra_header import *
from ra_format import *

RA_MAX_FILENAME_LENGTH = 1024

class Printer():
    """
    A fantastically useful dynamic printer.
    """

    def __init__(self, datum):
        
        sys.stdout.write("\r\x1b[K" + datum.__str__())
        sys.stdout.flush()

def dump(obj):
  for attr in dir(obj):
    print "obj.%s = %s" % (attr, getattr(obj, attr))

class switch(object):
    value = None
    def __new__(class_, value):
        class_.value = value
        return True

def case(*args):
    return any((arg == switch.value for arg in args))


def main(infile, ch):


# open the input file, and output file if necessary

    fp = open(infile, "r")
    print "<infile> = ", infile
    if ch > 0:
        fpo = open("frsc_read.dat", "w")
        print "<outfile> = frsc_read.dat"




    header = ra_header_struct()
    bFirst = 1


# loop, reading headers, until no more are found

    while fp.readinto(header) == sizeof(header):

# if this is the first header we've seen, show it:
        if (bFirst): 
            bFirst = 0

            print "Contents of first report's header:"
            print "  header.eType", header.eType
            print "  header.err=", header.err
            print "  header.iReportVersion=", header.iReportVersion
            print "  header.iRAVersion=", header.iRAVersion
            print "  header.eSource=", header.eSource
            print "  header.sInfo=", header.sInfo       
            print "  header.tvStart=", time.asctime(time.gmtime(header.tvStart.tv_sec))
            print "  header.nCh=", header.nCh
            print "  header.bw=", header.bw
            print "  header.fc=", header.fc
            print "  header.fs=", header.fs
            print "  header.tflags=", hex(0xFF & ord(header.tflags))
            print "  header.fflags=", hex(0xFF & ord(header.fflags))
            print "  header.T0=", header.T0
            print "  header.T1=", header.T1
            print "  header.T2=", header.T2
            print "  header.bChIn: "

            for i in range(RA_MAX_CH_DIV64-1, -1, -1):
                print hex(header.bChIn[i]),
            print

            print "  header.bChInCh: "
            for i in range(RA_MAX_CH_DIV64-1, -1, -1):
                print hex(header.bChInCh[i]),
            print

            print "  header.nSubCh=", header.nSubCh
            print "  header.eSubChMethod=", ord(header.eSubChMethod)
            print "  header.eTBL_Method=", ord(header.eTBL_Method)
            print "  header.nTBL_Order=", header.nTBL_Order
            print "  header.eTBL_Units=", ord(header.eTBL_Units)
            print "  header.nfft=", header.nfft
            print "  header.nfch=", header.nfch
            print "  header.eFBL_Method=", ord(header.eFBL_Method)
            print "  header.nFBL_Order=", header.nFBL_Order
            print "  header.eFBL_Units=", ord(header.eFBL_Units)
            print "  header.iSeqNo=", header.iSeqNo
            print "  header.fStart=", header.fStart

            print "Now summarizing all reports found..."

        oneline = "  header.eType = %d header.err = %d header.iSeqNo = %d header.fStart = %d" % (header.eType, header.err, header.iSeqNo, header.fStart)
        Printer(oneline)

# read rest of report 

        while switch(header.eType):
            if case(RA_H_ETYPE_NULL):
                break

            if case(RA_H_ETYPE_TF0, RA_H_ETYPE_TF1):

#  remaining data is in a "struct ra_td"; read that

                td = ra_td()
                fp.readinto(td)

 # save data to file

                x = '{0:d} {1:f} {2:d} {3:d} '.format(header.iSeqNo, header.fStart, td.clips.x, td.clips.y)
                fpo.write(x)

                if  ch > 0:
                    n = ch-1

                    x = '{0:f} {1:f} {2:f} {3:f} {4:f} {5:f} {6:f} {7:f} {8:f} {9:f} '.format( \
                        td.tdac[n].xi.mean, td.tdac[n].xi.max, td.tdac[n].xi.rms, td.tdac[n].xi.s, td.tdac[n].xi.k,
                        td.tdac[n].xq.mean, td.tdac[n].xq.max, td.tdac[n].xq.rms, td.tdac[n].xq.s, td.tdac[n].xq.k)
                    fpo.write(x)

                    x = '{0:f} {1:f} {2:f} {3:f} {4:f} {5:f} {6:f} {7:f} {8:f} {9:f} '.format( \
                       td.tdac[n].yi.mean, td.tdac[n].yi.max, td.tdac[n].yi.rms, td.tdac[n].yi.s, td.tdac[n].yi.k,
                       td.tdac[n].yq.mean, td.tdac[n].yq.max, td.tdac[n].yq.rms, td.tdac[n].yq.s, td.tdac[n].yq.k)
                    fpo.write(x)

                    x = '{0:f} {1:f} {2:f} {3:f} {4:f} {5:f} {6:f} {7:f} {8:f} {9:f} '.format( \
                       td.tdac[n].xm2.mean, td.tdac[n].xm2.max, td.tdac[n].xm2.rms, td.tdac[n].xm2.s, td.tdac[n].xm2.k,
                       td.tdac[n].ym2.mean, td.tdac[n].ym2.max, td.tdac[n].ym2.rms, td.tdac[n].ym2.s, td.tdac[n].ym2.k)
                    fpo.write(x)

                    x = '{0:f} {1:f} {2:f} {3:f} {4:f} {5:f} {6:f} {7:f} {8:f} {9:f} \n'.format( \
                       td.tdac[n].u.mean, td.tdac[n].u.max, td.tdac[n].u.rms, td.tdac[n].u.s, td.tdac[n].u.k,
                       td.tdac[n].v.mean, td.tdac[n].v.max, td.tdac[n].v.rms, td.tdac[n].v.s, td.tdac[n].v.k)
                    fpo.write(x)

                break

    fp.close() 
    if  ch > 0:
        fpo.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Error: must specify an input file")

    else:
        infile = sys.argv[1]

    if len(sys.argv) == 3:
        ch = int(sys.argv[2])
    else:
        ch = 0

    main(infile, ch) 
# frsc_read.py out.dat 30

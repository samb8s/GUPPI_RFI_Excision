# ra_analyze.py

import sys

import numpy as np
from scipy.stats import skew,kurtosis

import robust_stats as rs

def ra_analyze(chunk):

# check for correct input
    shape = chunk.shape
    if (shape[2] != 4):
        print "Error, not the correct numnber of polarization dimensions"
        return

# form the various quantities we want to do statistics on

    xi = chunk[:,:,0]  ; xq = chunk[:,:,1]  ; yi = chunk[:,:,2]   ; yq = chunk[:,:,3]
    xx =  xi.astype(float)*xi.astype(float) + xq.astype(float)*xq.astype(float)
    yy =  yi.astype(float)*yi.astype(float) + yq.astype(float)*yq.astype(float) 
    xyi = xi.astype(float)*yi.astype(float) + xq.astype(float)*yq.astype(float)
    xyq = xq.astype(float)*yi.astype(float) - xi.astype(float)*yq.astype(float)

    # testing out the MAD algorithm
    #rs.plot_mad_ratios(xx)

    rs.replace_mad_two_pass(xx, threshold=1.0)
    sys.exit()

# and do the statistics - along the time (second) axis
    xiMean = np.mean(xi,axis=1) ; xqMean = np.mean(xq,axis=1) ; yiMean   = np.mean(yi,axis=1)  ; yqMean  = np.mean(yq,axis=1)
    xxMean = np.mean(xx,axis=1) ; yyMean = np.mean(yy,axis=1) ; xyiMean  = np.mean(xyi,axis=1) ; xyqMean = np.mean(xyq,axis=1)
    xiRMS  = np.std(xi,axis=1)  ; xqRMS  = np.std(xq,axis=1)  ; yiRMS    = np.std(yi,axis=1)   ; yqRMS   = np.std(yq,axis=1)
    xxRMS  = np.std(xx,axis=1)  ; yyRMS  = np.std(yy,axis=1)  ; xyiRMS   = np.std(xyi,axis=1)  ; xyqRMS  = np.std(xyq,axis=1)
 
    return xiMean, xqMean, yiMean, yqMean, xxMean, xxRMS, yyMean, yyRMS
    

def main():
    xxMean = []
    xxRMS = []
    yyMean = []
    yyRMS = []
    for i in range(3):
        chunk = np.random.rand(512,512,4)
        res = ra_analyze(chunk)
        xxMean.append(res[0])
        xxRMS.append(res[1])
        yyMean.append(res[2])
        yyRMS.append(res[3])

    xxMeanWrite = np.vstack(xxMean)
    xxRMSWrite  = np.vstack(xxRMS)
    yyMeanWrite = np.vstack(yyMean)
    yyRMSWrite  = np.vstack(yyRMS)
    np.savez("temp.npz", xxMean=xxMeanWrite, xxRMS=xxRMSWrite, 
                         yyMean=yyMeanWrite, yyRMS=yyRMSWrite)

if __name__ == "__main__":
    main()

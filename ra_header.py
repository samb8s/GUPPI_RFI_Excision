""" ra_header.py

R. Prestage 04 February 2014

Python file to define the parameters otherwise defined in ra_format_defines.h
by Steve Ellingson, VT.

This version corresponds to ra_format_defines.h version 2013 Nov 25

"""

# eType 
RA_H_ETYPE_NULL =   0 # RESERVED 
RA_H_ETYPE_TF0  =   1 # time domain analysis, full-bandwidth & channels, period-T0 update 
RA_H_ETYPE_TF1  =   2 # time domain analysis, full-bandwidth & channels, period-T1 update 
RA_H_ETYPE_TS0  =   3 # time domain analysis, subchannels, period-T0 update 
RA_H_ETYPE_TS1  =   4 # time domain analysis, subchannels, period-T1 update 
RA_H_ETYPE_FC0  =   5 # freq domain analysis for specified channel, period-T0 update 
RA_H_ETYPE_FC2  =   6 # freq domain analysis for specified channel, period-T2 update 

# eSource 
RA_H_ESOURCE_GUPPI_FILE = 1 # 1 = GUPPI raw data file 
RA_H_ESOURCE_GUPPI_RT   = 2 # 2 = GUPPI real-time 
# ... future sources identified here ...  

# tflags 
RA_H_TFLAGS_TF  =  1 # b0 (LSB): Do time-domain analysis for entire available bandwidth? (1=Yes). Channels flagged in bChInFull[] will be excluded 
RA_H_TFLAGS_TC  =  2 # b1:       Do time-domain analysis for channels? (1=Yes). Channels flagged in bChIn[] will not be analyzed. 
RA_H_TFLAGS_TS  =  4 # b2:       Do time-domain analysis for subchannels? (1=Yes). Subchannels in channels flagged in bChIn[] will not be analyzed. 
RA_H_TFLAGS_TBF =  8 # b3:       Do baseline cal for full bandwidth? (1=Yes). Channels flagged in bChInFull[] will be excluded. 
                           #           ...applies only to Stokes-I 
RA_H_TFLAGS_TBC = 16 # b4:       Do baseline cal for channels? (1=Yes). Channels flagged in bChIn[] will not be baselined. 
                           #           ...applies only to Stokes-I 
                           # b5-b7:    RESERVED 

# fflags 
RA_H_FFLAGS_FF  =  1 # b0 (LSB): RESERVED. (Some day: Do freq-domain analysis for entire available bandwidth? (1=Yes).) 
RA_H_FFLAGS_FC  =  2 # b1:       Do freq-domain analysis for channels? (1=Yes). Channels flagged in bChIn[] will not be analyzed. 
RA_H_FFLAGS_FS  =  4 # b2:       Do freq-domain analysis for subchannels? (1=Yes). Subchannels in channels flagged bChIn[] will not be analyzed. 
RA_H_FFLAGS_FBC =  8 # b3:       Do baseline cal for channels prior to analysis? (1=Yes). Channels flagged in bChIn[] will not be baselined. 
                            #           ...applies only to Stokes-I 
RA_H_FFLAGS_FBS = 16 # b4:       Do baseline cal for subchannels prior to analysis? (1=Yes). Subchannel flagged in bChIn[] will not be baselined. 
                            #           ...applies only to Stokes-I 
                            # b5-b7:    RESERVED 

# eSubChMethod 
RA_H_ESUBCHMETHOD_FFT  = 0 # FFT, no window 
RA_H_ESUBCHMETHOD_FFTH = 1 # FFT, Hamming window 

# eTBL_Method 
RA_H_ETBL_METHOD_SIMPLE = 1 # Fit polynomial of order nBaselineOrder to last T2-period mean, then divide 

# eTBL_Units 
RA_H_ETBL_UNITS_NATURAL = 0 # Natural units (i.e., no change in units) 
RA_H_ETBL_UNITS_STDDEV  = 1 # Convert to standard deviations 

# eFBL_Method 
RA_H_EFBL_METHOD_SIMPLE = 1 # Fit polynomial of order nBaselineOrder to last T2-period mean, then divide 

# eFBL_Units 
RA_H_EFBL_UNITS_NATURAL = 0 # Natural units (i.e., no change in units) 
RA_H_EFBL_UNITS_STDDEV  = 1 # Convert to standard deviations 





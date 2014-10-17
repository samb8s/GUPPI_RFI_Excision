"""
ra_format.py - specify the "RFI Analysis" (RA) Output format

R. Prestage 04 February 2014

This version based on ra_format.c by Steve Ellingson, version 1, 2014 Jan19
 
RA outputs a "report" whenever new information is available. 
A report consists of a header (struct ra_header_struct), followed by the new information. 
The format of the new information section is one of several possible structures, determined by the "eType" field in the header.
See also file ra_format_defines.h.  (Not part of this specification, but helpful.)  

"""

from ctypes import *


RA_H_REPORT_VERSION  = 0    # iReportVersion
RA_MAX_SINFO_LENGTH  = 80   # length of sInfo field; see below
RA_MAX_CH_DIV64      = 16   #  maximum number of channels supported, divided by 64

# define a structure to hold a Unix timeval

class timeval(Structure):
    _fields_ = [('tv_sec', c_long),
                ('tv_usec', c_long)]

# Here's the standard header that appears at the beginning of all reports: ****/

class ra_header_struct(Structure):

# what type of report is this? 

    _fields_ = [('eType', c_int),

#              =0 header only; e.g., for diagnostic purposes. 
#              =1 time domain analysis, full-bandwidth & channels, period-T0 update 
#              =2 time domain analysis, full-bandwidth & channels, period-T1 update 
#              =3 time domain analysis, subchannels, period-T0 update 
#              =4 time domain analysis, subchannels, period-T1 update 
#              =5 freq domain analysis for specified channel, period-T0 update 
#              =6 freq domain analysis for specified channel, period-T2 update 

        ('err', c_long),  #  long int err; # Bits set to identify error/status; err=0 means all OK. 

# *****************************************
# ** metadata that shouldn't be changing **
# *****************************************

        ('iReportVersion', c_ushort),            # version of this packet format.  Code should set this equal to RA_H_REPORT_VERSION 
        ('iRAVersion',c_ushort),                 # version of RA that is outputting this report.  Code should set this equal to RA_H_RA_VERSION 
        ('eSource', c_ubyte),                    # 1 = GUPPI raw data file, 2 = GUPPI real-time, <future formats added here> 
        ('sInfo', c_char * RA_MAX_SINFO_LENGTH), # human-friendly free-format string 
                                                 # specified at start-up and passed through without modification  

# ********************************************************
# ** metadata extracted from the source data's metadata **
# ********************************************************

        ('tvStart', timeval),  # [unix time] Start time for interval considered in first report. Absolute ("calendar") time 
        ('nCh', c_long),       # Number of channels.  Meaning of "channel" depends on eSource. 
                               # ...Generally, "channels" are defined within the data, as opposed to 
                               # being the result of some additional processing. 
                               # ..."0" means the source data is not divided into channels. nCh=1 is not allowed. 
        ('bw', c_float),       # [Hz] Bandwidth = OBSBW*(1e+6) (may be negative)   
        ('fc', c_double),      # [Hz] Center frequency for "full bandwidth" = OBSFREQ*(1e+6) 
        ('fs', c_double),      # [Hz] Sample rate per-channel = 1/TBIN 

  # note for GUPPI raw data format the center frequency of channel "i" is (fc - bw/2 + (i-0.5)*bw) [Hz] 


# *************************************************************
# ** parameters specified at start-up, describing operation: **
# *************************************************************


# Some flags determining what gets done 

        ('tflags', c_char), # b0 (LSB): Do time-domain analysis for entire available bandwidth? (1=Yes). Channels flagged in bChInFull[] will be excluded 
                            # b1:       Do time-domain analysis for channels? (1=Yes). Channels flagged in bChIn[] will not be analyzed. 
                            # b2:       Do time-domain analysis for subchannels? (1=Yes). Subchannels in channels flagged in bChIn[] will not be analyzed. 
                            # b3:       Do baseline cal for full bandwidth? (1=Yes). Channels flagged in bChInFull[] will be excluded. 
                            #           ...applies only to Stokes-I 
                            # b4:       Do baseline cal for channels? (1=Yes). Channels flagged in bChIn[] will not be baselined. 
                            #           ...applies only to Stokes-I 
                            # b5-b7:    RESERVED 
        ('fflags', c_char), # b0 (LSB): RESERVED. (Some day: Do freq-domain analysis for entire available bandwidth? (1=Yes).) 
                            # b1:       Do freq-domain analysis for channels? (1=Yes). Channels flagged in bChIn[] will not be analyzed. 
                            # b2:       Do freq-domain analysis for subchannels? (1=Yes). Subchannels in channels flagged bChIn[] will not be analyzed. 
                            # b3:       Do baseline cal for channels prior to analysis? (1=Yes). Channels flagged in bChIn[] will not be baselined. 
                            #           ...applies only to Stokes-I 
                            # b4:       Do baseline cal for subchannels prior to analysis? (1=Yes). Subchannel flagged in bChIn[] will not be baselined. 
                            #           ...applies only to Stokes-I 
                            # b5-b7:    RESERVED 

        ('T0', c_double),   # [seconds] period at which this packet is updated/sent 
        ('T1', c_double),   # [seconds] period > T0 at which time-domain info is updated (in addition to updates at packet rate) 
                            # < 0 means don't do this 
        ('T2', c_double),   # [seconds] period > T0 at which freq-domain info is updated (in addition to updates at packet rate) 
                            # < 0 means don't do this 
 
# Channels to consider. These are bit-wise flags indicating channels; e.g., LSB refers to lowest-indexed channel  
        ('bChIn', c_ulong * RA_MAX_CH_DIV64),   # channels to be processed in "channel-by-channel" & "full bandwidth" processing (1=exclude) 
        ('bChInCh', c_ulong * RA_MAX_CH_DIV64), # channels to be processed in "channel-by-channel" processing (overrides bChIn) 

# Subchannel defintion.  "Subchannels" are further divisions within channels for *time-domain* processing. 
        ('nSubCh', c_long),   # number of subchannels per channel 
                              # ..."0" means the source data is not divided into channels. nCh=1 is not allowed.  
        ('eSubChMethod', c_char), # method for creating subchannels. 0=FFT, no window; 1=FFT, Hamming window 

# Time domain processing parameters. 
        ('eTBL_Method', c_char), # When baselining is done, this determines how. Note baselines are updated at the T2 period. 
                                 # ...=1: Fit polynomial of order nBaselineOrder to last T2-period mean, then divide 
        ('nTBL_Order', c_int),   # Order of polynomial used when eBaselineMethod=1 
        ('eTBL_Units', c_char),  # Units in which baselined spectrum are reported 
                                 # ...=0: Natural units (i.e., no change in units)   
                                 # ...=1: Convert to standard deviations, with mean and standard deviation computed using all available bins 

# Frequency domain processing parameters.  Note these apply on a channel-by-channel basis 
        ('nfft', c_int),         # FFT length 
        ('nfch', c_int),         # >=nfft; This is number of channels from center considered in baselining and freq-domain analysis 
        ('eFBL_Method', c_char), # When baselining is done, this determines how. Note baselines are updated at the T2 period. 
                                 # ...=1: Fit polynomial of order nBaselineOrder to last T2-period mean, then divide 
        ('nFBL_Order', c_int),   # Order of polynomial used when eBaselineMethod=1 
        ('eFBL_Units', c_char),  # Units in which baselined spectrum are reported 
                                 # ...=0: Natural units (i.e., no change in units)   
                                 # ...=1: Convert to standard deviations, with mean and standard deviation computed using all available bins   

# **********************************************
# ** some metadata specific to current report **
# **********************************************

        ('iSeqNo', c_long),      # sequence number; = iSeqNo from last report (of any kind) + 1  
        ('fStart', c_double)]   # time in seconds elapsed from tvStart until start of information being described in this report 
  
# end of struct ra_header_struct 


# **********************************************************************************
# **********************************************************************************
# * Structures used to define format of "new information" sections for eType 1..6 **
# **********************************************************************************
# **********************************************************************************

class DAstruct(Structure):
    _fields_ = [('mean', c_float), # mean 
         ('max', c_float),         # maximum value over interval 
#        ('min', c_float),         // future feature - minumum value over interval 
         ('rms', c_float),         # RMS (standard deviation) 
#        ('median', c_float),      // future feature
         ('s', c_float),           # skewness 
         ('k', c_float)]           # excess kurtosis 

class DAPstruct(Structure):
    _fields_ = [ \
        ('xi', DAstruct),  # real component of x 
        ('xq', DAstruct),  # imag component of x 
        ('yi', DAstruct),  # real component of y 
        ('yq', DAstruct),  # imag component of y 
        ('xm2', DAstruct), # X pol magnitude squared  
        ('ym2', DAstruct), # Y pol magnitude squared 
        # note Stokes I is xm2+ym2, and Stokes Q is xm2-ym2 
        # we do xm2 and ym2 as opposed to I and Q to better sense problems specific to X and Y 
        ('u', DAstruct),   # Stokes U 
        ('v', DAstruct)]   # Stokes V 

class clips_struct(Structure): 
    _fields_ = [('x', c_long), # number of times sqrt( xi^2 + xq^2 ) >= max encodable value of xi (or xq) is seen 
                ('y', c_long)] # number of times sqrt( yi^2 + yq^2 ) >= max encodable value of yi (or yq) is seen 


# **************************************************************************************************************
# **************************************************************************************************************
# ** "New Information" section for eType=1: time domain analysis, full-bandwidth & channels, period-T0 update **
# ** "New Information" section for eType=2: time domain analysis, full-bandwidth & channels, period-T1 update **
# **************************************************************************************************************
# **************************************************************************************************************

class ra_td(Structure):
    dim = RA_MAX_CH_DIV64 * 64
    _fields_ = [('clips', clips_struct),                  # clip counters 
                ('tda', DAPstruct),                       # full bandwidth (all channels as one) 
                ('tdac', DAPstruct * dim)] # per channel 


# **************************************************************************************************************
# **************************************************************************************************************
# ** "New Information" section for eType=3: time domain analysis, subchannels, period-T0 update **
# ** "New Information" section for eType=4: time domain analysis, subchannels, period-T1 update **
# **************************************************************************************************************
# **************************************************************************************************************

class ra_tds(Structure):
    dim = RA_MAX_CH_DIV64 * 64
    _fields_ = [('tdas', DAPstruct * dim)] # statistics, per channel & subchannel.  Needs to be allocated [1..nSubCh] 


# *********************************************************************************************************
# *********************************************************************************************************
# ** "New Information" section for eType=5: freq domain analysis for specified channel, period-T0 update **
# ** "New Information" section for eType=6: freq domain analysis for specified channel, period-T2 update **
# *********************************************************************************************************
# *********************************************************************************************************

class ra_fd(Structure): 
    _fields_ = [('ch', c_int), # channel number that this applies to 
                ('fda', DAPstruct)] # statistics. Needs to be allocated [1..nfch]  


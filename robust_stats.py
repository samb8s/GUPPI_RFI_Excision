#!/usr/bin/python

import sys
import math
import random 

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

# hampel filter stuff
def hampel_2d_fast(array2d,
                     threshold,
                     window_size_x=16,
                     window_size_y=16):

    """
    Time and frequency hampel filter, slide window in
    time and frq directions and run the median cut
    """

    # copy of original to make changes to
    #results_array = np.copy(array2d)
    changes = np.zeros_like(array2d)
    n_f_chans = array2d.shape[0]
    n_t_samps = array2d.shape[1]

    #f_array = np.arange(n_f_chans)
    #t_array = np.arange(n_t_samps)
    #ff, tt = np.meshgrid(f_array, t_array)

    
    #for i_chan, j_samp in zip(ff.ravel(), tt.ravel()):
    for (i_chan, j_samp), val in np.ndenumerate(array2d):
        i_min = i_chan - window_size_y
        if i_min < 0:
            i_min = 0
        i_max = i_chan + window_size_y
        if i_max >= n_f_chans:
            i_max = n_f_chans-1

        j_min = j_samp - window_size_x
        if j_min < 0:
            j_min = 0
        j_max = j_samp + window_size_x
        if j_max >= n_t_samps:
            j_max = n_t_samps-1

        window_1d = array2d[i_min:i_max+1,j_min:j_max+1].ravel()

        # find median of all values
        median, med_dev, mad = med_abs_dev(window_1d)
        mad_scale_est = threshold * 1.4826 * mad
        med_dev = med_dev.reshape(i_max - i_min + 1, -1)

        # find values above mad_scale_est and
        # write median fpr the window into "changes" at
        # correct location
        inds = np.where(med_dev>mad_scale_est)
        # have to add i_min and j_min to account for
        # position of the window inside array2d
        changes[inds[0]+i_min, inds[1]+j_min] = median

    # replacing values using a mask
    mask = changes>0
    array2d[mask] = changes[mask]

    return array2d

def hampel_filter_2d(array2d,
                     threshold,
                     window_size_x=16,
                     window_size_y=16):

    """
    Time and frequency hampel filter, slide window in
    time and frq directions and run the median cut
    """

    # changes array - I store median values for samples which need to be changed
    # in here
    changes = np.zeros_like(array2d)
    n_f_chans = array2d.shape[0]
    n_t_samps = array2d.shape[1]

    count = 0
    # loop over frequency channels
    for i_chan in xrange(n_f_chans):
        if count % 50 == 0:
            print "starting freq loop = ", count
        count += 1
        i_min = i_chan - window_size_y
        if i_min < 0:
            i_min = 0
        i_max = i_chan + window_size_y
        if i_max >= n_f_chans:
            i_max = n_f_chans-1

        # now time samples
        for j_samp in xrange(n_t_samps):

            j_min = j_samp - window_size_x
            if j_min < 0:
                j_min = 0
            j_max = j_samp + window_size_x
            if j_max >= n_t_samps:
                j_max = n_t_samps-1

            window_1d = array2d[i_min:i_max+1,j_min:j_max+1].ravel()

            # find median, median deviation, and MAD
            # for all values in window
            median, med_dev, mad = med_abs_dev(window_1d)
            mad_scale_est = threshold * 1.4826 * mad
            med_dev = med_dev.reshape(i_max - i_min + 1, -1)

            # find values above mad_scale_est and
            # write median fpr the window into "changes" at
            # correct location
            inds = np.where(med_dev>mad_scale_est)
            # have to add i_min and j_min to account for
            # position of the window inside array2d
            changes[inds[0]+i_min, inds[1]+j_min] = median


    # replacing values using a mask
    mask = changes>0
    array2d[mask] = changes[mask]

    return array2d

def hampel_filter_1d(array2d, threshold, window_size=16):
    """
    Time-only filter - slide a window along in time, 
    and perform Hampel filtering on it
    """

    # assume first index of the array2d is frequency, 
    # therefore filter in second index
    index_array = form_index_array(array2d)
    # make copy of original. 
    # we modify the values in here
    results_array = np.copy(array2d)
    n_f_chans = array2d.shape[0]
    n_t_samps = array2d.shape[1]

    #for window_size in [4]:#[4,16,32]:
    # use k-K... k+K samples, so take 2K+1 size
    # loop over freq channels
    #for timeseries in array2d:
    # loop over time samples
    #for i, value in enumerate(timeseries):
    for i_samp in xrange(n_t_samps):
        # get range of indices
        i_min = i_samp - window_size
        if i_min<0:
            i_min=0
        i_max = i_samp + window_size

        # make relevant mask
        index1 = index_array>=i_min
        index2 = index_array<=i_max

        # apply mask
        in_window = array2d[index1 & index2].reshape(n_f_chans, -1)
        median_array = np.median(in_window, axis=1).reshape(n_f_chans, -1)
        mad_array = np.array([med_abs_dev_1(row) for row in in_window])
        mad_scale_est = threshold * 1.4826 * mad_array

        # median deviation
        med_dev = np.absolute(in_window - median_array)

        # apply threshold 
        for row, median, tQ, results in zip(med_dev, 
                                            median_array, 
                                            mad_scale_est,
                                            results_array):
            # check each med_dev value against tQ and replace with median
            # if med_dev val > tQ
            for i, val in enumerate(row):
                if val > tQ:
                    # change values in results-array, not in-place
                    results[i_min+i] = median

    return results_array

def form_index_array(array2d):
    
    new_data = np.array([])

    freq_chan = np.arange(0, array2d.shape[1], dtype=int)
    for i in xrange(array2d.shape[0]):
        new_data = np.append(new_data, freq_chan)

    return new_data.reshape(array2d.shape[0], -1)

def form_freq_index_array(array2d):
    new_data = np.array([])

    time_series = np.arange(0, array2d.shape[0], dtype=int)
    for i in xrange(array2d.shape[1]):
        new_data = np.append(new_data, time_series)

    return new_data.reshape(array2d.shape[1], -1).T

# MAD stuff
def med_abs_dev(array1d):
    """
        Perform the MAD algorithm on a 1d array,
        returns a single number denoting the value 
        of the median absolute deviation
    """

    running_med = np.median(array1d)
    abs_dev = np.abs(array1d - running_med)
    mad = np.median(abs_dev)
    return running_med, abs_dev, mad

def med_abs_dev_1(array1d):
    """
        Perform the MAD algorithm on a 1d array,
        returns a single number denoting the value 
        of the median absolute deviation
    """

    running_med = np.median(array1d)
    abs_dev = np.abs(array1d - running_med)
    mad = np.median(abs_dev)
    return mad


def med_abs_dev_ratio(array1d):
    """
    Get the ratio of the absolute deviation to the MAD
    """

    running_med = np.median(array1d)
    abs_dev = np.abs(array1d - running_med)
    mad = np.median(abs_dev)

    return np.nan_to_num(abs_dev/mad)

def mad_ratios_XY(array2d):
    """
    Ratio of each value's median to the MAD value
    """

    return mad_ratio_row(array2d), mad_ratio_col(array2d)


def mad_offsets_XY(array2d):
    """
    My first idea for a way to use MAD on a 2d array...
    to plot an image of the statistic, calculate MAD in 
    x and y directions and take difference of each sample 
    from MAD (do for X and Y seperately)

    After that would be good to combine X,Y offsets somehow 
    """

    #calculate MAD for each row
    mad_rows = np.array([med_abs_dev(row) for row in array2d])
    #med_rows = np.array([np.median(row) for row in array2d])

    # calc MAD for each column
    mad_cols = np.array([med_abs_dev(row) for row in array2d.T])
    #med_cols = np.array([np.median(row) for row in array2d.T])
    #med_rows = np.array([np.median(row) for row in array2d])

    #med_cols = np.array([np.median(row) for row in array2d.T])
    #med_rows = np.array([np.median(row) for row in array2d])

    # calc MAD for each column
    mad_cols = np.array([med_abs_dev(row) for row in array2d.T])
    #med_cols = np.array([np.median(row) for row in array2d.T])

    # calc row offsets
    mad_row_offsets = np.array([row - mad_row for row, mad_row in 
                                    zip(array2d, mad_rows)])

    # calc col offsets
    mad_col_offsets = np.array([col - mad_col for col, mad_col in 
                                    zip(array2d.T, mad_cols)]).T

    return mad_row_offsets, mad_col_offsets


# plotting routines
def plot_mad_offsets(array2d):

    plotData(array2d)
    row_off, col_off = mad_offsets_XY(array2d)

    plotData(row_off)

    plotData(col_off)
    sys.exit()

def plot_mad_ratios(array2d):
    plotData(array2d)
    row_ratio, col_ratio = mad_ratios_XY(array2d)

    plotData(row_ratio)

    plotData(col_ratio)

def replace_mad_ratio(array2d, threshold=5.0):
    """
    Calculate the ratio (abs dev)/MAD
    and then replace any values > threshold with some randomly 
    picked noise
    """

    row_ratios, col_ratios =  mad_ratios_XY(array2d)

    row_mask1 = row_ratios>threshold
    row_mask2 = row_ratios <= threshold

    mu = np.mean(array2d)
    # using the approx that if MAD is a better indication of the 
    # deviation, ignoring outliers, then sigma = 1.4826*MAD
    # so find average MAD....
    mad_row_avrg = np.mean(np.array([med_abs_dev(row) for row in array2d]))
    sigma = 1.4826*mad_row_avrg
    replace_vals = np.random.normal(mu, sigma, np.shape(array2d))

    replaced_by_row = np.zeros_like(array2d)
    replaced_by_row[row_mask1] = replace_vals[row_mask1]
    replaced_by_row[row_mask2] = array2d[row_mask2]

    col_mask1 = col_ratios > threshold
    col_mask2 = col_ratios <= threshold
    mad_col_avg = np.mean(np.array([med_abs_dev(row) for row in array2d.T]))
    sigma = 1.4826*mad_col_avg
    replace_vals = np.random.normal(mu, sigma, np.shape(array2d))

    replaced_by_col = np.zeros_like(array2d)
    replaced_by_col[col_mask1] = replace_vals[col_mask1]
    replaced_by_col[col_mask2] = array2d[col_mask2]

    plotData(replaced_by_row)
    plotData(replaced_by_col)

def mad_ratio_row(array2d):
    mr_rows = np.array([med_abs_dev_ratio(row) for row in array2d])
    return mr_rows

def mad_ratio_col(array2d):
    mr_cols = np.array([med_abs_dev_ratio(row) for row in array2d.T]).T
    return mr_cols

def replace_mad_rows(array2d, threshold=5.0):
    row_ratios = mad_ratio_row(array2d)
    row_mask = row_ratios > threshold

    mu = np.mean(array2d)
    mad_row_avg = np.mean(np.array([med_abs_dev(row) for row in array2d]))
    sigma = 1.4826 * mad_row_avg
    replace_vals = np.random.normal(mu, sigma, np.shape(array2d))

    array2d[row_mask] = replace_vals[row_mask]

    return array2d

def replace_mad_cols(array2d, threshold=5.0):
    col_ratios = mad_ratio_col(array2d)
    col_mask = col_ratios > threshold

    mu = np.mean(array2d)
    mad_col_avg = np.mean(np.array([med_abs_dev(row) for row in array2d.T]))
    sigma = 1.4826*mad_col_avg
    replace_vals = np.random.normal(mu, sigma, np.shape(array2d))
    array2d[col_mask] = replace_vals[col_mask]

    return array2d

def replace_mad_two_pass(array2d, threshold=5.0):
    
    a = replace_mad_rows(array2d, threshold)

    a = replace_mad_cols(a, threshold)

    plotData(a)
    
def plotData(arr):
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_cmap = [left, bottom, width, height]
    rect_x = [left, bottom_h, width, 0.2]
    rect_y = [left_h, bottom, 0.2, height]

    plt.figure(1, figsize=(8,8))

    axCmap = plt.axes(rect_cmap)
    ax_x = plt.axes(rect_x)
    ax_y = plt.axes(rect_y)

    ax_x.xaxis.set_major_formatter(NullFormatter())
    ax_y.yaxis.set_major_formatter(NullFormatter())

    # plot
    vertical_data = arr.mean(axis=1)
    vertical_md = np.median(arr, axis=1)
    horiz_data = arr.mean(axis=0)
    horiz_md = np.median(arr, axis=0)

    aspect = float(len(horiz_data)) / len(vertical_data)

    axCmap.imshow(arr, aspect=aspect, origin='lower')
    axCmap.set_ylabel('Frequency Channel')
    axCmap.set_xlabel('Time Sample')

    ax_x.plot(horiz_data, 'r-', label='mean')
    ax_x.plot(horiz_md, 'b-', label='median')
    ax_x.set_xlim(0, len(horiz_data))

    y_ra = range(len(vertical_data))
    ax_y.plot(vertical_data, y_ra, 'r-')
    ax_y.plot(vertical_md, y_ra, 'b-')
    #ax_y.xaxis.set_major_formatter(NullFormatter())
    ax_y.set_ylim(0, len(vertical_data))

    #axCmap.colorbar()
    plt.show()

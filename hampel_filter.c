#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <omp.h>
#include <string.h>
/*----------------------------------------------------------------------------*/

void hampel_filter_2d(float *inbuffer, 
                      int nchans,
                      int nsamps,
                      float* outbuffer,
                      float threshold, 
                      int window_size_x,
                      int window_size_y);
void mad_replace(float* inbuffer,
                 float *outbuffer,
                 int xlen,
                 int ylen,
                 int imin, int imax, 
                 int jmin, int jmax, 
                 float median,
                 float mad_scale_est);
float mad_of_2d(float *inbuffer,
                int len,
                int imin,
                int imax,
                int jmin,
                int jmax,
                float median);
float median_of_2d(float *inbuffer,
                   int len,
                   int imin,
                   int imax,
                   int jmin,
                   int jmax);
float median_of_1d(float* f_array,
                   int len);

void hampel_filter_2d(float *inbuffer, 
                      int nchans,
                      int nsamps,
                      float* outbuffer,
                      float threshold, 
                      int window_size_x,
                      int window_size_y){

    int i_chan, j_samp, val;
    int i_min, i_max, j_min, j_max;
    float med, mad, mad_scale_est;

    // loop over channels
    for (i_chan=0; i_chan < nchans; i_chan++){

        if (i_chan%50 == 0) printf("Starting channel loop %d\n", i_chan);
        // set channel range
        i_min = i_chan - window_size_y;
        if (i_min < 0){
            i_min = 0;
        }

        i_max = i_chan + window_size_y;
        if (i_max >= nchans){
            i_max = nchans-1;
        }
        
        // loop over samples
        for (j_samp=0; j_samp < nsamps; j_samp++){

            // set sample range
            j_min = j_samp - window_size_x;
            if (j_min < 0) {
                j_min = 0;
            }

            j_max = j_samp + window_size_x;
            if (j_max >= nsamps){
                j_max = nsamps -1;
            }

            
            // calculate median, MAD of the window region
            //printf("calculating MAD, %d %d", i_chan, j_samp);
            med = median_of_2d(inbuffer, nsamps, i_min, i_max, j_min, j_max);
            mad = mad_of_2d(inbuffer, nsamps, i_min, i_max, j_min, j_max, med);
            mad_scale_est = 1.4826 * mad * threshold;

            mad_replace(inbuffer,
                        outbuffer,
                        nsamps,
                        nchans,
                        i_min, i_max, j_min, j_max, 
                        med,
                        mad_scale_est);
        }
    }
}

void mad_replace(float* inbuffer,
                 float *outbuffer,
                 int xlen,
                 int ylen,
                 int imin, int imax, 
                 int jmin, int jmax, 
                 float median,
                 float mad_scale_est){

    // replace values in outbuffer if abs(value - median) > mad_scale_est

    int ii, jj;
    float offset;

    for (ii=imin; ii<=imax; ii++){
        for (jj=jmin; jj<=jmax; jj++){
            
            // find offset of value from the median
            offset = fabsf(inbuffer[(xlen*ii) + jj] - median);

            // compare offset vs. the mad_scale_estimate.
            if (offset > mad_scale_est){

                // replace with median
                outbuffer[(xlen*ii) + jj] = median;
            }
            else{

                // keep the value
                outbuffer[(xlen*ii) + jj] = inbuffer[(xlen*ii) + jj];
            }

        }
    }

 }

float mad_of_2d(float *inbuffer,
                int len,
                int imin,
                int imax,
                int jmin,
                int jmax,
                float median){

    float *f_array, temp, val;
    int ii, jj, irange, jrange, count=0, n;

    irange = imax - imin + 1;
    jrange = jmax - jmin + 1;
    n = irange * jrange;
    // allocate array of jrange*irange elements
    f_array = (float *) malloc(sizeof(float) * n);

    for (ii=imin; ii<=imax; ii++){
        for (jj=jmin; jj<=jmax; jj++){
            // get absolute deviation
            val = fabsf(inbuffer[len*jj + ii] - median);
            // store in f_array
            f_array[count] = val;
            count += 1;
        }
    }

    
    // get median of f_array
    median = median_of_1d(f_array, n);
    free(f_array);

    return median;
}

float median_of_2d(float *inbuffer,
                   int len,
                   int imin,
                   int imax,
                   int jmin,
                   int jmax){

    float median, *f_array, temp;
    int ii, jj, irange, jrange, count=0, n;

    irange = imax - imin + 1;
    jrange = jmax - jmin + 1;
    n = irange * jrange;
    // allocate array of jrange*irange elements
    f_array = (float *) malloc(sizeof(float) * n);
    
    for (ii=imin; ii<=imax; ii++){
        for (jj=jmin; jj<=jmax; jj++){
            // store the values into f_array
            f_array[count] = inbuffer[len*jj + ii];
            count += 1;
        }
    }

    // return median of f_array
    median = median_of_1d(f_array, n);
    free(f_array);

    return median;
}


float median_of_1d(float* f_array,
                   int len){

    int ii, jj;
    float temp;

    // sort f_array 
    for (ii=0; ii<len-1; ii++){
        for (jj=0; jj<len; jj++){
            
            if (f_array[jj] < f_array[ii]) {
    
                // swap elements
                temp = f_array[ii];
                f_array[ii] = f_array[jj];
                f_array[jj] = temp;

            }
        }
    }
    
    // find median
    if (len%2){
        return f_array[len/2];
    } else {
        return ((f_array[len/2] + f_array[len/2 - 1]) / 2.0);
    }
}



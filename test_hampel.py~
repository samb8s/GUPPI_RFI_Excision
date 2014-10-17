#!/usr/bin/python

import numpy as np
import math
import random
import robust_stats as rs

import matplotlib.pyplot as plt


r_array = np.random.rand(2,1000)

for i in xrange(50):

    r_i = random.randint(0,999)

    r_array[0][r_i] = 10.

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax1.plot(r_array[0])

ax2 = fig.add_subplot(212)

# now run hampel filter
r_clean = rs.hampel_filtering_1d(r_array, 2)
ax2.plot(r_clean[0])

plt.show()

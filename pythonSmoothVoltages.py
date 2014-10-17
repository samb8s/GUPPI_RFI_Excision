import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import median_filter
from scipy import *

npzfile = np.load("/lustre/pulsar/scratch/RFI/richard.npz")

img =  npzfile['xiMean']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

blur = median_filter(img, size=3,mode="nearest")
plt.imshow(blur,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

img =  npzfile['xqMean']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

blur = median_filter(img, size=3,mode="nearest")
plt.imshow(blur,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

img =  npzfile['yiMean']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

blur = median_filter(img, size=3,mode="nearest")
plt.imshow(blur,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

img =  npzfile['yqMean']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

blur = median_filter(img, size=3,mode="nearest")
plt.imshow(blur,aspect="auto",origin="lower")
plt.colorbar()
plt.show()



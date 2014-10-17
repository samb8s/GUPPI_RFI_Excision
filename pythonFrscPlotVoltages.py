import numpy as np
import matplotlib.pyplot as plt

npzfile = np.load("/lustre/pulsar/scratch/RFI/copy.npz")

img =  npzfile['xiMean']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

img =  npzfile['xqMean']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

img =  npzfile['yiMean']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

img =  npzfile['yqMean']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()


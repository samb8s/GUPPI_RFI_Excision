import numpy as np
import matplotlib.pyplot as plt

npzfile = np.load("/lustre/pulsar/scratch/RFI/frsced.npz")

img =  npzfile['xxMean']
print img.shape
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

time = np.mean(img, axis = 1)
plt.plot(time)
plt.show()

time256 = img[:,256]
plt.plot(time256)
plt.show()



freq = np.mean(img, axis = 0)
plt.plot(freq)
plt.show()

img =  npzfile['xxRMS']
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

img = (npzfile['xxRMS']/npzfile['xxMean']) - 1
img = img.transpose()
plt.imshow(img,aspect="auto",origin="lower")
plt.colorbar()
plt.show()

img = (npzfile['xxRMS']/npzfile['xxMean']) - 1
img = img.transpose()
imgplot = plt.imshow(img,aspect="auto",origin="lower")
imgplot.set_clim(-0.3,0.3)
plt.colorbar()
plt.show()

img = (npzfile['xxRMS']/npzfile['xxMean']) - 1
img = img.transpose()
imgplot = plt.imshow(img,aspect="auto",origin="lower")
imgplot.set_clim(-0.2,0.2)
plt.colorbar()
plt.show()

img = (npzfile['xxRMS']/npzfile['xxMean']) - 1
img = img.transpose()
imgplot = plt.imshow(img,aspect="auto",origin="lower")
imgplot.set_clim(-0.05,0.05)
plt.colorbar()
plt.show()

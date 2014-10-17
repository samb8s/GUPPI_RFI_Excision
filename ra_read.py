import numpy as np
npzfile = np.load("temp.npz")
print npzfile.files
print npzfile['xxMean'].shape

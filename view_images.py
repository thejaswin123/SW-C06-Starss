
import numpy as np
import matplotlib.pyplot as plt
import random

images = np.load('images.npy')
labels = np.load('labels.npy')

for x in range(10):
    i = random.randint(0, images.shape[0])
    image = np.reshape(images[i], (images[i].shape[0], images[i].shape[1]))
    plt.imshow(image, cmap='binary')
    plt.title('Image #' + str(i) + '   ' + str(labels[i]) + ' knots')
    plt.show()

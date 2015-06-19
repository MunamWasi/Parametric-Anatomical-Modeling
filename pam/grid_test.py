<<<<<<< HEAD
import unittest
import grid
import kernel
import numpy as np
import cProfile

N = 5000

def testGrid():
    np.random.seed(42)
    g = grid.UVGrid(3)
    print("Computing pre mask")
    g.compute_post_mask(kernel.gauss, [1.0, 1.0, 0.0, 0.0])
    print("Inserting post neurons")
    uvs = np.random.rand(N, 2)
    for uv in uvs:
        g.insert_postNeuron(1, uv, (1., 2., 3.), 42)

    print("Computing pre mask")
    g.compute_pre_mask(kernel.gauss, [1.0, 1.0, 0.0, 0.0])
    print("selecting")
    # for i in range(N/10):
    g.select_random((0.0, 0.0), N)

=======
import unittest
import grid
import kernel
import numpy as np
import cProfile
import matplotlib.pyplot as plt

N = 5000

def testGrid():
    np.random.seed(42)
    g = grid.UVGrid(None)
    print("Computing post mask")
    # g.compute_post_mask(kernel.gauss, [1.0, 1.0, 0.0, 0.0])
    g.compute_grid('post', kernel.gauss)
    print("Inserting post neurons")
    uvs = np.random.rand(N, 2)
    for i, uv in enumerate(uvs):
        g.insert_postNeuron(i, uv, (1., 2., 3.), 42)

    print("selecting")
    # for i in range(N/10):
    random_points = g.select_random((0.2, 0.3), N)
    # pdb.set_trace()
    # plt.scatter([p[1][0] for p in random_points], [p[1][1] for p in random_points])
    # plt.hist([p[1][0] for p in random_points], 20)
    # plt.hist([p[1][1] for p in random_points], 20)
    # plt.axis([0, 1, 0, 1])
    # plt.show()

>>>>>>> b3d9f632388f91c16f64425de48de92676d4f63c
cProfile.run('testGrid()')
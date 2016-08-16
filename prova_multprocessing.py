from multiprocessing import Pool
from numpy.random import exponential


def f(arr):
    from mayavi import mlab
    fig = mlab.figure(size=(800,800))
    n_x = arr[0]
    n_y = arr[1]
    n_z = arr[2]
    name = arr[3]
    d = exponential(size=(n_x,n_y,n_z))
    mlab.points3d(d[0], d[1], d[2], figure=fig)
    mlab.savefig(name+'.png', figure=fig)
    mlab.close(fig)
    return name


def start_pool(processes):
    x = [10, 10, 10, 10]
    y = [10, 10, 10, 10]
    z = [10, 10, 10, 10]
    n = ['1', '2', '3', '4']
    i = zip(x,y,x,n)
    p = Pool(processes=processes)
    result = p.map(f, i)
    for elem in result:
        print elem


if __name__ == '__main__':
    start_pool(2)

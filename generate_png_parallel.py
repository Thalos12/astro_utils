import argparse
import sys
import os
from multiprocessing import Pool
import numpy as np
import logging
from mayavi import mlab
import maxmin


t = 0
mfig = mlab.figure(size=(600,600))
dmax, dmin = 0, 0

def gen_png_wrapper(i, f, res, basename, extension='.dat', parallel=False, use_processes=2, folder='.', header_lines=0):
    if parallel:
        f_args = []
        for k in range(i, f):
            f_args.append([res, basename+"%05d"%(k,), extension, header_lines])
        #print f_args
        p = Pool(processes=use_processes)
        try:
            output = p.map(gen_png, f_args)
        except:
            print 'Something went wrong, please do not use multiprocessing.'

    else:
        output = []
        for k in range(i, f):
            filename = basename+"%05d"%(k,)
            output.append(gen_png(res, filename, extension, header_lines))
    print "Result of the operation:"
    for o in output:
        print o


def gen_png(*args):
    if len(args) == 1:
        if len(args[0]) == 4:
            res = args[0][0]
            f_name = args[0][1]
            extension = args[0][2]
            header_lines = args[0][3]
    elif len(args) == 4:
        res = args[0]
        f_name = args[1]
        extension = args[2]
        header_lines = args[3]
    else:
        print "Wrong number or type of arguments, aborting"
        return (-1)

    global mfig
    mfig.scene.disable_render = True

    data = np.loadtxt(f_name+extension, skiprows=header_lines)
    header = np.genfromtxt(f_name+extension, max_rows=4)

    global t
    t += header[-1]
    dt = header[-1]
    to_delete = []
    for i in range(0, data.shape[0]):
        if (data[i,1] < 0 and data[i,0] >0):
            to_delete.append(i)
    data = np.delete(data, to_delete, axis=0)
    rho = data[::res,-2]

    mfig.scene.disable_render = False

    global dmax
    global dmin
    p = mlab.points3d(data[::res,0], data[::res,1], data[::res,2], rho, colormap='hot', mode='sphere', vmax=dmax, vmin=dmin)
    mlab.view(-45.0, 90.0)
    mlab.colorbar()
    if '/' in f_name: # ottengo il titolo
        base = f_name.split('/')[-1]
    title = base.split('.')[0]
    print "Title: ", title
    mlab.title(title)
    # mlab.show()
    mlab.savefig(f_name+'.png')
    mlab.clf(mfig)

    return (f_name, 0)


def gen_multiple_data(start_n_file, end_n_file, n_particles, basename):
    for i in range(start_n_file, end_n_file):
        gen_data(n_particles, basename+"%05d"%(i,)+'.dat')


def gen_data(particles, filename):
    d = np.zeros((particles, 4))
    for i in range(particles):
        d[i, 0] = round(np.random.rand()*10, 4)
        d[i, 1] = round(np.random.rand()*10, 4)
        d[i, 2] = round(np.random.rand()*10, 4)
        d[i, 3] = round(np.random.rand()*10, 4)
    np.savetxt(filename, d, fmt='%.4e')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("start_index", type=int, help="Starting index.")
    parser.add_argument("end_index", type=int, help="Ending index.")
    parser.add_argument("resolution", type=int, help="Part of the name that is unchanged.")
    parser.add_argument("basename", type=str, help="Part of the name that is unchanged.")
    parser.add_argument("-g", "--generate_data", action="store_true", help="Used to generate random data to test output.")
    parser.add_argument("-m", "--multiprocessing", action="store_true", help="Uses Python's multiprocessing module to speed up the job.")
    parser.add_argument("-p", "--processes", type=int, default=2, help="Number of processes used to speed up the job if option \"-m\" has been specified, defaults to 4.")
    parser.add_argument("-e", "--extension", type=str, default=".dat", help="Extension of the files, defaults to \".dat\".")
    parser.add_argument("-s", "--skipheaderlines", type=int, default=0, help="Skip the first s lines of the data files.")
    args = parser.parse_args()

    args.end_index += 1

    if args.generate_data:
        gen_multiple_data(start_n_file=args.start_index, end_n_file=args.end_index, n_particles=10000, basename=args.basename)

    if not os.path.isfile(args.basename+"%05d"%(args.start_index,)+args.extension):
        print "File {} does not exixts.".format(args.basename+"%05d"%(args.start_index,)+args.extension)
        sys.exit(1)

    dmax, dmin = maxmin.maxmin(args.start_index, args.end_index, args.basename, args.skipheaderlines, args.resolution)

    gen_png_wrapper(i=args.start_index, f=args.end_index, res=args.resolution, basename=args.basename,
                    extension=args.extension, parallel=args.multiprocessing, use_processes=args.processes, header_lines=args.skipheaderlines)

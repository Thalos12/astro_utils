# -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging
import time
import platform
from multiprocessing import Pool
import numpy as np
import maxmin_new as maxmin
import math as m


# questa funzione serve per usare il codice in parallelo o meno
def gen_png_wrapper(i, f, res, basename, extension='.dat', parallel=False, use_processes=2, folder='.', header_lines=0):
    if parallel:
        f_args = []
        for k in range(i, f):
            f_args.append([res, basename+"%05d"%(k,), extension, header_lines])  # creo una lista da dare in pasto al metodo map del Pool
        # print f_args
        p = Pool(processes=use_processes)
        output = p.map(gen_png, f_args)
    else:
        output = []
        for k in range(i, f):
            filename = basename+"%05d"%(k,)
            output.append(gen_png(res, filename, extension, header_lines))
    print "Result of the operation:"
    for o in output:
        print o


# funzione che da in output i file .png
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
        return (f_name, -1)

    data = np.loadtxt(f_name+extension, skiprows=header_lines)
    header = np.genfromtxt(f_name+extension, max_rows=4)  # salvo le righe di header per t e dt

    global t
    t += header[-1]
    dt = header[-1]

    to_delete = []  # il ciclo che segue serve a creare la "fetta vuota" nel plot
    for i in range(0, data.shape[0]):
        if (data[i,1] < 0 and data[i,0] >0):
            to_delete.append(i)
    data = np.delete(data, to_delete, axis=0)
    rho = data[::res,-2]
    logrho=[m.log10(float(i)) for i in rho]

    from mayavi import mlab

    if platform.system == 'Linux':
        mlab.options.offscreen = True

    mfig = mlab.figure(size=(800,800)) # inizializzo una figura

    global dmax
    global dmin

    mlab.points3d(data[::res,0], data[::res,1], data[::res,2], logrho, colormap='jet', mode='sphere',scale_mode='none',scale_factor=8, vmax=dmax, vmin=dmin)  # posiziono i punti in 3d
    mlab.colorbar(title="Density", orientation='horizontal', nb_labels=6)  # faccio apparire la colorbar
   #mlab.text(0.10, 0.90, "time:{}  dt:{}".format(t, dt), figure=mfig, width=0.2)  # aggiungo le scritte con tempo e dt

    if '/' in f_name:  # ottengo il nome della simulazione
        base = f_name.split('/')[-1]
    else:
        base = f_name
    title = base.split('.')[0]  # ottengo la parte prima di tutti i punti: SIM.column.00xxx -> SIM
    # print "Title: ", title
    #mlab.text(0.70, 0.90, title, width=0.2, figure=mfig)
    mlab.title('{}    t = {}    dt = {}'.format(title,t,dt),width=0.85)

    mlab.axes(nb_labels=5, x_axis_visibility=False, z_axis_visibility=False,ranges=[-120.0,120.0,-120.0,120.0,-120.0,120.0], figure=mfig)
    outline = mlab.outline(figure=mfig)
    outline.outline_mode = 'cornered'
    # mlab.axes(y_axis_visibility=False, z_axis_visibility=False)
    mlab.view(-45.0, 90.0, distance=1000)  # imposto l'angolo di visione dell'insieme dei dati
    # mlab.show()
    mlab.savefig(f_name+'.png', figure=mfig)
    mlab.close(mfig)  # pulisco la figura per prepararla al prossimo set di dati

    return (f_name, 0)


# funzione che chiama il generatore di png per tutti i file
def gen_multiple_data(start_n_file, end_n_file, n_particles, basename, extension=''):
    for i in range(start_n_file, end_n_file):
        gen_data(n_particles, basename+"%05d"%(i,)+extension)


# genera set di dati casuali in forma array(x, y, z, rho)
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
    parser.add_argument("-t", "--time", action="store_true", help="Keeps track of the time taken by the script.")
    args = parser.parse_args()

    args.end_index += 1 # serve per fare il png di tutti i file

    if args.generate_data: # genera file con dati random per provare o script
        gen_multiple_data(start_n_file=args.start_index, end_n_file=args.end_index, n_particles=10000, basename=args.basename, extension=args.extension)

    if not os.path.isfile(args.basename+"%05d"%(args.start_index,)+args.extension): # verifica che ci sia almeno il primo file
        print "File {} does not exixts.".format(args.basename+"%05d"%(args.start_index,)+args.extension)
        sys.exit(1)

    dmax, dmin = maxmin.gen_maxmin_dat(args.start_index, args.end_index, args.basename, args.skipheaderlines, args.resolution) # calcolo massimo e minimo della densità
    dmax=m.log10(float(dmax))
    dmin=m.log10(float(dmin))
    print "Finished calculating maximum ({}) and minimum ({}) density.".format(dmax,dmin)

    # sys.exit()

    t = 0 # memorizza il tempo totale della simulazione

    if args.time:
        t_init = time.time()

    gen_png_wrapper(i=args.start_index, f=args.end_index, res=args.resolution, basename=args.basename,
                    extension=args.extension, parallel=args.multiprocessing, use_processes=args.processes, header_lines=args.skipheaderlines)

    if args.time:
        print "Time taken:", time.time()-t_init

# -*- coding: utf-8 -*-
import os
import sys
import argparse
import logging
import time
import platform
from multiprocessing import Pool
import numpy as np
import maxmin
import math as m


# questa funzione serve per usare il codice in parallelo o meno
def gen_png_wrapper(i, f, res, basename, extension='.dat', parallel=False, use_processes=2, folder='.', header_lines=4):
    f = f+1  # serve per includere anche l'ultimo file
    dmax, dmin = maxmin.gen_maxmin_dat(i, f, basename, header_lines, res)  # calcolo massimo e minimo della densità
    dmax = m.log10(float(dmax))
    dmin = m.log10(float(dmin))
    print "Finished calculating maximum ({}) and minimum ({}) density.".format(dmax,dmin)

    f_name = basename+"%05d"%(i,)
    data = data = np.loadtxt(f_name+extension, skiprows=header_lines)
    header = np.genfromtxt(f_name+extension, max_rows=4)

    t=0
    t += header[-1]
    dt = header[-1]
    to_delete = []  # il ciclo che segue serve a creare la "fetta vuota" nel plot
    for p in range(0, data.shape[0]):
        if (data[p,1] < 0 and data[p,0] > 0):
            to_delete.append(p)
    data = np.delete(data, to_delete, axis=0)
    rho = data[::res,-2]
    logrho = [m.log10(float(r)) for r in rho]

    from mayavi import mlab
    mfig=mlab.figure(size=(800,800))
    points = mlab.points3d(data[::res,0], data[::res,1], data[::res,2], logrho, colormap='jet', mode='sphere', scale_factor=8, scale_mode='none', vmax=dmax, vmin=dmin)  # posiziono i punti in 3d
    mlab.colorbar(title="Density", orientation='horizontal', nb_labels=6)  # faccio apparire la colorbar
    mlab.axes(nb_labels=5, x_axis_visibility=False, z_axis_visibility=False, ranges=[-120.0,120.0,-120.0,120.0,-120.0,120.0], figure=mfig)
    outline = mlab.outline(figure=mfig)
    outline.outline_mode = 'cornered'
    # mlab.axes(y_axis_visibility=False, z_axis_visibility=False)
    mlab.view(-45.0, 90.0, distance=800)  # imposto l'angolo di visione dell'insieme dei dati

    if '/' in f_name:  # ottengo il nome della simulazione
        base = f_name.split('/')[-1]
    else:
        base = f_name
    title = base.split('.')[0]  # ottengo la parte prima di tutti i punti: SIM.column.00xxx -> SIM
    # print "Title: ", title
    #mlab.text(0.70, 0.90, title, width=0.2, figure=mfig)
    fig_title = '{}    t = {:.2E}     dt = {:.2E}'.format(title,t,dt)
    mlab.title(fig_title, figure=mfig, size=0.38, height=0.85)
    mlab.savefig(f_name+'.png', figure=mfig)
    print "Finished {} of {}.".format(i,f)

    for k in range(i+1, f):
        f_name = basename+"%05d"%(k,)

        data = np.loadtxt(f_name+extension, skiprows=header_lines)
        header = np.genfromtxt(f_name+extension, max_rows=4)  # salvo le righe di header per t e dt

        t += header[-1]
        dt = header[-1]

        to_delete = []  # il ciclo che segue serve a creare la "fetta vuota" nel plot
        for w in range(0, data.shape[0]):
            if (data[w,1] < 0 and data[w,0] >0):
                to_delete.append(w)
        data = np.delete(data, to_delete, axis=0)
        rho = data[::res,-2]
        logrho = [m.log10(float(y)) for y in rho]

        points.mlab_source.set(x=data[::res,0], y=data[::res,1], z=data[::res,2], scalars=logrho)

        if '/' in f_name:  # ottengo il nome della simulazione
            base = f_name.split('/')[-1]
        else:
            base = f_name
        title = base.split('.')[0]  # ottengo la parte prima di tutti i punti: SIM.column.00xxx -> SIM
        # print "Title: ", title
        #mlab.text(0.70, 0.90, title, width=0.2, figure=mfig)
        fig_title = '{}    t = {:.2E}     dt = {:.2E}'.format(title,t,dt)

        #mlab.view(-45.0, 90.0, distance=1000)  # imposto l'angolo di visione dell'insieme dei dati
        mlab.title(fig_title, figure=mfig, size=0.38, height=0.85)
        mlab.savefig(f_name+'.png', figure=mfig)
        print "Finished {} of {}.".format(k,f)

if __name__ == '__main__':
    gen_png_wrapper(1, 10, 100, './hydro_energy_eqn_100UA_5M/HYDRO_ISO.column.', '')
    #gen_png_wrapper(1, 10, 100, './freefall_10000UA_1M/ff_10000_1M_00.column.', '')

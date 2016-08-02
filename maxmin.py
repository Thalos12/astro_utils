# -*- coding: utf-8 -*-
import numpy as np
import argparse
import os


def maxmin(initial, final, basename, sk, res):
    maxdens,mindens=0,0
    for i in range(initial,final):
        path=basename+'%05d'%(i,)
        data=np.genfromtxt(path,skip_header=sk)
        density=data[::res,-2]
        mindens_temp = np.amin(density)
        maxdens_temp = np.amax(density)
        if i==initial:
            maxdens=maxdens_temp
            mindens=mindens_temp
        else:
            if mindens_temp<mindens:
                mindens=mindens_temp
            if maxdens_temp>maxdens:
                maxdens=maxdens_temp

    return (maxdens,mindens)


# serve per scrivere il file maxmin.dat o, se è già presente, per leggerlo e ritornare i valori
def gen_maxmin_dat(initial, final, basename, sk, res):
    if '/' in basename: # questo ciclo serve per prendere il path giusto per il maxmin.dat
        b = basename.split('/')
        b[-1] = 'maxmin.dat'
        n = '/'.join(b)
    else:
        n = 'maxmin.dat'
    if os.path.isfile(n):
        print "File maxmin.dat found."
        with open(n,'r') as f:
            dat = f.readlines()
        print "Initial: {}Final: {}Basename: {}Resolution: {}Maxdens: {}Mindens: {}".format(dat[0], dat[1], dat[2], dat[3], dat[4], dat[5])
        gen = raw_input("Generate new maxmin.dat file or use current one? [new/current]\n---> ")
        if gen == 'current' or gen=='c':
            with open(n,'r') as f:
                data = f.readlines()
            maxdens = data[-2].rstrip()
            mindens = data[-1].rstrip()
            return (maxdens, mindens)

    print "Generating a new maxmin.dat"
    maxdens, mindens = maxmin(initial, final, basename, sk, res)
    data = [initial, final-1, basename, res, maxdens, mindens]
    with open(n,'w') as f:
        for e in data:
            f.write(str(e)+'\n')
    return (maxdens,mindens)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('initial', type=int)
    parser.add_argument('final', type=int)
    parser.add_argument('basename', type=str)
    parser.add_argument('skip_header', type=int)
    parser.add_argument('res', type=int)
    args = parser.parse_args()
    maxdens, mindens = maxmin(args.initial, args.final, args.basename, args.skip_header, args.res)
    print maxdens, mindens

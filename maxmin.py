import numpy as np
import argparse


def maxmin(initial,final,basename,sk,res):
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

#!/usr/bin/env python
import os,sys
import numpy as np
import argparse
from auxcodes import sepn
deg2rad = np.pi/180.0
rad2deg = 180.0/np.pi

def read_pointingfile(pointingfilename):

	pointingdict = {}
	infile = open(pointingfilename,'r')
	for line in infile:
		line = line.rstrip()
		line = line.split(',')
		while '' in line:
			line.remove('')
		if '#' in line[0]:
			continue
		pointingname,radeg,decdeg,integrationtime,pointingids = line[0],float(line[1]),float(line[2]),float(line[3]),line[4]
		pointingdict[pointingname] = [pointingids,radeg,decdeg,integrationtime]
	return pointingdict

def find_pointings_to_mosaic(pointingdict,mospointingname):
	seps = np.array([])
	tomospointings = np.array([])
	ra1,dec1 = pointingdict[mospointingname][1],pointingdict[mospointingname][2]
	for j in pointingdict:
		ra2,dec2 = pointingdict[j][1],pointingdict[j][2]
		seps = np.append(seps,(sepn(ra1*deg2rad,dec1*deg2rad,ra2*deg2rad,dec2*deg2rad)*rad2deg))
		tomospointings = np.append(tomospointings,j)
	sortedseps = np.sort(seps)
	# For now include the 6 closest pointings plus keep including others until we have all that are within the distance of 1.1 times the 6th closest pointing. At later stage try to take into account e.g. elongation of beam for low declination observations.
	endmosindex = 7
	for i in range(7,20):
		if (sortedseps[i])/(sortedseps[6]) < 1.1:
			endmosindex = i
	mosaicpointings = tomospointings[np.where(seps < sortedseps[endmosindex])]
	mosseps = seps[np.where(seps < sortedseps[endmosindex])]
	return mosaicpointings,mosseps

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('pointingfile', type=str, help='LoTSS pointing progress file')
    parser.add_argument('mospointingname', type=str, help='Mosaic central pointing name')

    args = parser.parse_args()

    pointingdict = read_pointingfile(args.pointingfile)

    mosaicpointings,mosseps = find_pointings_to_mosaic(pointingdict,args.mospointingname)

    printline = ''
    printlineseps=''
    for i in range(len(mosaicpointings)):
            printline += (',%s'%mosaicpointings[i])
            printlineseps += (',%s'%mosseps[i])

    print 'Separations: %s'%printlineseps[1:]
    print 'Pointings: %s'%printline[1:]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import sys, math
from timeit import default_timer as timer
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns 
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,AutoMinorLocator)
from matplotlib.font_manager import FontProperties
import dask.dataframe as dd
from matplotlib import rc

# sns.set(context='paper', style='darkgrid', palette='deep', font='sans-serif', font_scale=1, color_codes=True, rc=None)

start = timer()

# try:
# 	infilename = sys.argv[1]; outfilename = sys.argv[2]
# except:
	# print ("Usage:",sys.argv[0], "infile outfile"; sys.exit(1))

# ifile = '/Users/popa/Dropbox (CSI)/python/2D-dz-theta/shorter_001_f25.dat'
ifile = '/Users/popa/Dropbox (CSI)/python/2D-dz-theta/shorter_001_l25.dat'
output = '2dpmf-l25.dat'
### I/O ###
df = dd.read_csv(ifile,header=None, names=['a1','x','a2','a3','a4','y'],comment='#',delim_whitespace=True)
ofile = open(output, "w")

### I/O ###
ofile.write("# Nagg	shape pmf"+ '\n')
row = df['x'].size.compute()

### Parameters ###
xmin = 0
xmax = 100
xbinsize = 1.000
nbinx = int(xmax/xbinsize+1)

ymin = 0.00
ymax = 1.00
ybinsize = 0.1
nbiny = int(ymax/ybinsize+1)

pmax = 0.0000000
temp = 310.00
R = 0.002   # kcal / mol.K

### Functions ###
def do_sum_fast(ncount):
	found = 0
	for count in ncount:
		found  = found + count
	return found

# Procedures ###
for xbin in np.linspace(xmin, xmax, num=nbinx, endpoint=True, dtype=float):
	for ybin in np.linspace(ymin, ymax, num=nbiny, endpoint=True, dtype=float):
		xbinj = xbin + xbinsize
		ybinj = ybin + ybinsize
		# print(xbinj, ybinj)
		ncount =[]
		plist = []
		for i,val in df.iterrows():
			if (val['x'] >= xbin and val['x'] < xbinj and val['y'] >= ybin and val['y'] < ybinj):
				count = 1
				ncount.append(count)

		# Checking ncount array
		if (len(ncount) ==0):
			count = 0
			ncount.append(count)

		## Count the total bins in ncount
		count = do_sum_fast(ncount)
		p = count / row
		plist.append(p)
		for each in plist:
			if pmax < each:
				pmax = each 
	
for xbin in np.linspace(xmin, xmax, num=nbinx, endpoint=True, dtype=float):
	for ybin in np.linspace(ymin, ymax, num=nbiny, endpoint=True, dtype=float):
		xbinj = xbin + xbinsize
		ybinj = ybin + ybinsize
		#print xbinj, ybinj
		ncount =[] 
		for i,val in df.iterrows():
			if (val['x'] >= xbin and val['x'] < xbinj and val['y'] >= ybin and val['y'] < ybinj):
				count = 1
				ncount.append(count)

		## Checking ncount array
		if (len(ncount) ==0):	
			count = 0

		## Count the total bins in ncount
		count = do_sum_fast(ncount)
		p = count / row
		if p != 0.00000:
			pmf = -R*temp*math.log(p/pmax)
		else:
			pmf = 3.0000

		# data = np.append(data,([xbin+xbinsize/2,ybin+ybinsize/2, pmf]))
		ofile.write(repr(xbin+xbinsize/2) + "	" + repr(ybin+ybinsize/2) + "	" + repr(pmf) + '\n')

print 
ofile.close()

### INPUT ###
ifile = '/Users/popa/Dropbox (CSI)/python/2dpmf-f25.dat'
df = pd.read_csv(ifile,header=None, names=['size','shape','pmf'],comment='#',delim_whitespace=True)

### PREPARATIONS ###
minz = df['pmf'].min()
maxz = df['pmf'].max()

### MAKE GRID TABLE ###
piv = pd.pivot_table(df,values=['pmf'],index=['shape'],columns=['size'])

#Interpolation methods in imshow() = [None, 'none', 'nearest', 'bilinear', 'bicubic', 'spline16',
        #    'spline36', 'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
        #    'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc', 'lanczos']

### PLOTS ###
ax, fig = plt.subplots()
im = fig.imshow(piv,cmap='Spectral', norm=None, aspect='auto', interpolation='bicubic', 
    alpha=None, vmin=minz, vmax=maxz, origin='lower', extent=None, 
    filternorm=1, filterrad=4.0,resample=None, url=None,data=None)

# axs.set_title("Origin from rc, reversed y-axis")

### FONT PARAMETERS ###

font = FontProperties()
font.set_family('serif')
font.set_name('Times New Roman')
font.set_style('normal')

### TICKS PARAMETERS ###

# fig.set_ylim(0,10)
fig.set_xlabel('Size',fontsize=15)
fig.set_ylabel(r'I$_{min}$ / I$_{max}$',fontsize=15)

# Notes: Since we use one of the data as INDEX in pivot_table,
# we need to extract the index (Flaot64Index) and convert it to numerical values,
# then we place them on appropriate locations
ycolumn = piv.index
ylabels = []
for i in pd.to_numeric(ycolumn,downcast='float'):
    ylabels = np.append(ylabels,i)
T=np.arange(len(ylabels))
plt.yticks(T,ylabels.round(3))

fig.xaxis.set_minor_locator(AutoMinorLocator())
fig.yaxis.set_minor_locator(AutoMinorLocator())
fig.tick_params(which='major', width=1.5,length=7)
fig.tick_params(which='minor', width=1.0,length=4)

### COLOR BAR ### 
cbar = plt.colorbar(im)
cbar.set_label('kcal / mol', rotation=270,labelpad=20,fontsize=15)
# cbar.ax.set_xticklabels(np.linspace(xmin,xmax,nbinx))
# cbar.ax.set_yticklabels(np.linspace(ymin,ymax,nbiny))

### MISCELLANEOUS ###
## Put the major ticks at the middle of each cell
# ax.set_yticks(np.arange(data.shape[0]) + 0.5, minor=False)
# ax.invert_yaxis()
# ax.set_xticks(np.linspace(xmin,xmax))

## Draw object
# fig.text(3, 8, 'boxed italics text in data coords', style='italic',
#         bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

## Tight layout for multiple plots
#   fig.tight_layout()

### SAVE FIGURE ### 
ax.savefig("2dpmf-l25.png",dpi=200, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=True, bbox_inches=None, pad_inches=0.1,metadata=None)

plt.show()
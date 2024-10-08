#!/usr/bin/env python3

# V. Kireyeu
# 10.2024

import sys
try:
    import os
    import argparse
    import math
    import statistics
    import matplotlib.pyplot as plt

except ModuleNotFoundError as err:
    sys.exit(err)

parser = argparse.ArgumentParser(prog = 'calculate_ioas')
parser.add_argument('-y', '--year',       metavar = 'YEAR',     help = 'Selected year', default = '2023')
parser.add_argument('-b', '--observable', metavar = 'OBS',      help = 'Observable: WIND, WDIR, TMP, APCP, GNT_W, GNT_T ...', default = 'WIND')
parser.add_argument('-t', '--type',       metavar = 'TYPE',     help = 'Error type: ME, MAE, RMSE', default = 'RMSE')
parser.add_argument('-z', '--level',      metavar = 'LEVEL',    help = 'Level (e.g. Z10, P850 etc)', default = 'Z10')
parser.add_argument('-d', '--dir',        metavar = 'DIR',      help = 'Input directory with the data files', default = 'stat')
parser.add_argument('-o', '--output',     metavar = 'OUTPUT',   help = 'Name of the output file', default = 'calculated_ioa.txt')
parser.add_argument('-p', '--plot',       metavar = 'PLOT',     help = 'Name of the output plot', default = 'calculated_ioa.png')
parser.add_argument('--cf',               metavar = 'COLUMN_F', help = 'Column with the F-value', default = 26)
parser.add_argument('--co',               metavar = 'COLUMN_O', help = 'Column with the O-value', default = 36)


month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

args      = parser.parse_args()
year      = args.year
observ    = args.observable      # WIND, WDIR, TMP, APCP, GNT_W, GNT_T
e_type    = args.type            # ME, MAE, RMSE
level     = args.level
indir     = args.dir
outfile   = args.output
plotname  = args.plot
colf      = int(args.cf) - 1 # Because index in Python starts from 0
colo      = int(args.co) - 1 # Because index in Python starts from 0

ioa = []
for cur_month in range(1,13): # For each month read the corresponding file
    file_name = f'{indir}/time_var_{level}_{observ}_{e_type}_{year}{str(cur_month).zfill(2)}.stat'
    if(not os.path.isfile(file_name)):
        print(f'Error: {file_name} does not exist')
        exit(-1)
    fp = open(file_name)
    print(fp)
    file_f = []
    file_o = []
    for i, line in enumerate(fp):
        if i < 1:                  # Skip first 2 header lines from the file 
            continue
        if line in ['\n', '\r\n']: # End of file
            break
        if len(line.strip()) == 0: # Empty line
            break
        splitline = line.split()              # Split the line as the vector of values
        file_f.append(float(splitline[colf])) # The needed values are on the 26-th and 36-th position,
        file_o.append(float(splitline[colo])) #   but vector elements start from 0, so it must be 25 and 35 elements here
    fp.close()
    
    if len(file_f) != len(file_o):
        print('Something went very wrong')
        exit(-1)
    
    mean_o = statistics.mean(file_o)
    vnumerator   = []
    vdenominator = []
    for i,ef in enumerate(file_f):
        vnumerator.append(math.pow(file_o[i] - file_f[i], 2))
        vdenominator.append(math.pow(math.fabs(file_f[i] - mean_o) + math.fabs(file_o[i] - mean_o), 2))
    
    numerator = sum(vnumerator)
    denominator = sum(vdenominator)
    ioa.append(1. - numerator/denominator)

print(ioa)
f = open(f'{outfile}', 'w')
for entry in ioa:
    f.write(f'{entry}\n')
f.close()
print(f'Output data file: {outfile}')

# Figure plotting
plt.bar(month_names, ioa, width = 0.4, label='Mean per month')

# Mean for the year
plt.axhline(y = statistics.mean(ioa), color = 'orange', linewidth = 2, alpha=0.85, label='Mean per year')
# Reference value
plt.axhline(y = 0.6, color = 'lime', linestyle=':', linewidth = 3, alpha=0.8, label='Reference')

plt.title(year)     # plot tile (top)
plt.xlabel('Month') # x-axis title
plt.ylabel('IOA')   # y-axis title

# Legend
plt.legend(loc='best', facecolor='white', framealpha=1)

# Plot saving
plt.savefig(f'{plotname}', bbox_inches='tight', dpi=300)
plt.close()
print(f'Output plot: {plotname}')

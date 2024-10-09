#!/usr/bin/env python3

# V. Kireyeu
# 10.2024

import sys
try:
    import os
    import argparse
    import matplotlib.pyplot as plt
    import statistics

except ModuleNotFoundError as err:
    sys.exit(err)

parser = argparse.ArgumentParser(prog        = 'draw_percentiles')
parser.add_argument('-y', '--year',       metavar = 'YEAR',   help = 'Selected year', default = '2023')
parser.add_argument('-b', '--observable', metavar = 'OBS',    help = 'Observable', default = 'WIND')
parser.add_argument('-t', '--type',       metavar = 'TYPE',   help = 'Error type', default = 'ME')
parser.add_argument('-d', '--dir',        metavar = 'DIR',    help = 'Input directory with the data files', default = 'time')
parser.add_argument('-o', '--output',     metavar = 'OUTPUT', help = 'Name of the output plot')
parser.add_argument('-l', '--lower',      metavar = 'Y_LOW',  help = 'Y-axis lower limit', default = -2)
parser.add_argument('-u', '--upper',      metavar = 'Y_UP',   help = 'Y-axis upper limit', default = 3.99)
parser.add_argument('-c', '--column',     metavar = 'COLUMN', help = 'Column with the error', default = 6)
parser.add_argument('-z', '--level',      metavar = 'LEVEL',  help = 'Level (e.g. Z10, P850 etc)', default = 'Z10')
parser.add_argument('-m', '--moreticks',                      help = 'Add more ticks on the Y-axis', action = 'store_true')

args      = parser.parse_args()
year      = args.year
observ    = args.observable      # WIND, WDIR, TMP, APCP, GNT_W, GNT_T
e_type    = args.type            # ME, MAE, RMSE
indir     = args.dir
plotname  = args.output
y_low     = float(args.lower)
y_up      = float(args.upper)
column    = int(args.column) - 1 # Because index in Python starts from 0
level     = args.level
moreticks = args.moreticks

if not plotname:
   plotname = f'percentiles_{level}_{observ}_{e_type}_{year}.png'

p_sel = [10, 25, 50, 75, 90, 95] # Slected percentiles

y_labels    = {'ME': 'Systematic error, ', 'MAE': 'Absolute error, ', 'RMSE': 'Root mean square error, '}
qa_lines    = {'WDIR': {'ME': [-10,  10],  'MAE':  [30]},
               'WIND': {'ME': [-0.5, 0.5], 'RMSE': [2.0]},
               'TMP':  {'ME': [-0.5, 0.5], 'RMSE': [2.0]}}
if observ == 'TMP' and level == 'Z10': # Fix for the temperature level (Z10 -> Z2)
    level = 'Z2'
file_suffix = {'WDIR': f'{level}_WDIR', 'WIND': f'{level}_WIND_{e_type}', 'TMP': f'{level}_TMP_{e_type}',
               'APCP': f'APCP_{e_type}', 'GNT_W': f'GNT_W_{e_type}', 'GNT_T': f'GNT_T_{e_type}'}
units       = {'WDIR': 'deg', 'WIND': 'm/s', 'TMP': '$^\\circ$C', 'APCP': 'mm/12h', 'GNT_W': 'm/s', 'GNT_T': '$^\\circ$C per 100 m'}


y_mean = [] # vector for the year mean calculation
for cur_month in range(1,13): # For each month read the corresponding file
    file_name = f'{indir}/time_var_{file_suffix[observ]}_{year}{str(cur_month).zfill(2)}.txt'
    if(not os.path.isfile(file_name)):
        print(f'Error: {file_name} does not exist')
        exit(-1)
    fp = open(file_name)
    print(fp)
    file_mean = []                 # Mean values from the month file
    for i, line in enumerate(fp):
        if i < 2:                  # Skip first 2 lines from the file 
            continue
        if line in ['\n', '\r\n']: # End of file
            break
        if len(line.strip()) == 0: # Empty line
            break
        if observ == 'WDIR' and i % 2 > 0:
            continue
        splitline = line.split()                   # Split the line as the vector of values
        y_mean.append(float(splitline[column]))    #   so it's 5-th position here)
    fp.close()

res = statistics.quantiles(y_mean, n=100)
percentiles = []
for p in p_sel:
    percentiles.append(res[p-1])
print(percentiles)


# Matplotlib figure creation
fig, ax = plt.subplots()
ax.grid()
ax.plot(p_sel, percentiles, linestyle='-', marker='o', color='b')
ax.set_xticks(p_sel)

# Titles
plt.title(year)
plt.xlabel('Percentile')
plt.ylabel(y_labels[e_type]+units[observ])

# Quality criteria lines
if observ in qa_lines and 'Z' in level and e_type in qa_lines[observ]:
    for i,val in enumerate(qa_lines[observ][e_type]):
        plt.axhline(y = val, color = 'lime', linestyle=':', linewidth = 3, alpha=0.8)

# Plot saving
plt.savefig(f'{plotname}', bbox_inches='tight', dpi=300)
plt.close()
print(f'Output file: {plotname}')

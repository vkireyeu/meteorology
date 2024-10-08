#!/usr/bin/env python3

# V. Kireyeu
# 10.2024

# py draw_errors.py -o wind_me.png
# py draw_errors.py -l 0 -t MAE -o wind_mae.png
# py draw_errors.py -l 0 -u 4.99 -t RMSE -o wind_rmse.png

# py draw_errors.py -b TMP -l -5.99 -u 8.99 -o temp_me.png
# py draw_errors.py -b TMP -t MAE -l 0 -u 6.99 -o temp_mae.png
# py draw_errors.py -b TMP -t RMSE -l 0 -u 7.99 -o temp_rmse.png

# py draw_errors.py -b APCP -t ME   -l -10.99 -u 4.99  -o prec_me.png
# py draw_errors.py -b APCP -t MAE  -l -0.1   -u 14.99 -o prec_mae.png
# py draw_errors.py -b APCP -t RMSE -l -0.1   -u 14.99 -o prec_rmse.png

# draw_errors.py -b WDIR -l -180 -u 180             -o wdir_me.png
# draw_errors.py -b WDIR -l   -1 -u 181 -t MAE -c 7 -o wdir_mae.png

# draw_errors.py -b GNT_W -t RMSE -l -0.1 -u 2 -o gnt_w_rmse.png

import sys
try:
    import os
    import argparse
    import matplotlib.pyplot as plt
    import statistics

except ModuleNotFoundError as err:
    sys.exit(err)

parser = argparse.ArgumentParser(
                    prog        = 'draw_errors',
                    description = 'Errors for different observales')
parser.add_argument('-y', '--year',       metavar = 'YEAR',   help = 'Selected year', default = '2023')
parser.add_argument('-b', '--observable', metavar = 'OBS',    help = 'Observable', default = 'WIND')
parser.add_argument('-t', '--type',       metavar = 'TYPE',   help = 'Error type', default = 'ME')
parser.add_argument('-d', '--dir',        metavar = 'DIR',    help = 'Input directory with the data files', default = 'time')
parser.add_argument('-o', '--output',     metavar = 'OUTPUT', help = 'Name of the output plot', default = 'plot.png')
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

month_names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
y_labels    = {'ME': 'Systematic error, ', 'MAE': 'Absolute error, ', 'RMSE': 'Root mean square error, '}
qa_lines    = {'WDIR': {'ME': [-10,  10],  'MAE':  [30]},
               'WIND': {'ME': [-0.5, 0.5], 'RMSE': [2.0]},
               'TMP':  {'ME': [-0.5, 0.5], 'RMSE': [2.0]}}
if observ == 'TMP' and level == 'Z10': # Fix for the temperature level (Z10 -> Z2)
    level = 'Z2'
file_suffix = {'WDIR': f'{level}_WDIR', 'WIND': f'{level}_WIND_{e_type}', 'TMP': f'{level}_TMP_{e_type}',
               'APCP': f'APCP_{e_type}', 'GNT_W': f'GNT_W_{e_type}', 'GNT_T': f'GNT_T_{e_type}'}
units       = {'WDIR': 'deg', 'WIND': 'm/s', 'TMP': '$^\\circ$C', 'APCP': 'mm/12h', 'GNT_W': 'm/s', 'GNT_T': '$^\\circ$C per 100 m'}

# Matplotlib figure creation
fig = plt.figure()
ax = fig.add_subplot(111)

mmean = []  # List of the list for the monthly mean barplots
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
        file_mean.append(float(splitline[column])) # The mean value is on the 6-th position (but vector elements start from 0
        y_mean.append(float(splitline[column]))    #   so it's 5-th position here)
    fp.close()
    mmean.append(file_mean)                   # Fill the list of the list for the boxplots

bp = ax.boxplot(mmean, patch_artist = True,   # Draw all boxplots
                notch ='True', vert = 1,
                showmeans=True)

plt.setp(bp['medians'], linewidth = 1, color ='yellow') # The medians graphics
plt.setp(bp['fliers'], markersize=3.0, mec = 'magenta') # The 'fliers' (outliers)

for i,means in enumerate(bp['means']):        # The means graphics
    means.set(marker ='*', mfc ='red', mec ='red', label='Mean per month'  if i == 0 else '')

# Mean for the year
plt.axhline(y = statistics.mean(y_mean), color = 'k', linewidth = 2, alpha=0.85, label='Mean per year')

# Quality criteria lines
if observ in qa_lines and 'Z' in level and e_type in qa_lines[observ]:
    for i,val in enumerate(qa_lines[observ][e_type]):
        plt.axhline(y = val, color = 'lime', linestyle=':', linewidth = 2, alpha=0.8, label='Reference' if i == 0 else '')

# Modify a bit the y-axis range
plt.ylim(y_low, y_up)
if moreticks:                             # Add more ticks on the Y-axis
    plt.yticks([y * .5 for y in range(round(y_low)*2, round(y_up+0.1)*2)])

# Titles
ax.set_xticklabels(month_names)            # x-axis labels
plt.title(year)                            # plot tile (top)
plt.xlabel('Month')                        # x-axis title
plt.ylabel(y_labels[e_type]+units[observ]) # y-axis title

# Legend
plt.legend(loc='best')

# Plot saving
plt.savefig(f'{plotname}', bbox_inches='tight', dpi=300)
plt.close()
print(f'Output file: {plotname}')

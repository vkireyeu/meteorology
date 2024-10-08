#!/usr/bin/env python3

# V. Kireyeu
# 10.2024

import sys
try:
    import os
    import argparse
    import pandas as pd
    import pygmt

except ModuleNotFoundError as err:
    sys.exit(err)

parser = argparse.ArgumentParser(prog = 'calculate_mpr')
parser.add_argument('-y', '--year',       metavar = 'YEAR',        help = 'Selected year', default = '2023')
parser.add_argument('-b', '--observable', metavar = 'OBS',         help = 'Observable: WIND, WDIR, TMP, APCP, GNT_W, GNT_T ...', default = 'WIND')
parser.add_argument('-t', '--type',       metavar = 'TYPE',        help = 'Error type: ME, MAE, RMSE', default = 'RMSE')
parser.add_argument('-z', '--level',      metavar = 'LEVEL',       help = 'Level (e.g. Z10, P850 etc)', default = 'Z10')
parser.add_argument('-d', '--dir',        metavar = 'DIR',         help = 'Input directory with the data files', default = 'mpr')
parser.add_argument('-o', '--output',     metavar = 'OUTPUT',      help = 'Name of the output file', default = 'calculated_mpr_surf.csv')
parser.add_argument('-p', '--plot',       metavar = 'PLOT',        help = 'Name of the output plot', default = 'calculated_mpr.png')
parser.add_argument('--cs',               metavar = 'COLUMN_S',    help = 'Column with the station ID', default = 27)
parser.add_argument('--clat',             metavar = 'COLUMN_LAT',  help = 'Column with the station LAT', default = 28)
parser.add_argument('--clon',             metavar = 'COLUMN_LONG', help = 'Column with the station LONG', default = 29)
parser.add_argument('--olat',             metavar = 'OBJECT_LAT',  help = 'Object latitude', default = 48)
parser.add_argument('--olon',             metavar = 'OBJECT_LONG', help = 'Object longitude', default = 42.5)

region = [40, 45, 45.5, 49.5]

args      = parser.parse_args()
year      = args.year
observ    = args.observable      # WIND, WDIR, TMP, APCP, GNT_W, GNT_T
e_type    = args.type            # ME, MAE, RMSE
level     = args.level
indir     = args.dir
outfile   = args.output
plotname  = args.plot
csid      = int(args.cs) - 1 # Because index in Python starts from 0
clat      = int(args.clat) - 1 # Because index in Python starts from 0
clon      = int(args.clon) - 1 # Because index in Python starts from 0
olat      = float(args.olat)
olon      = float(args.olon)

file_name = f'{indir}/MPR_{level}_{observ}.stat'
if(not os.path.isfile(file_name)):
    print(f'Error: {file_name} does not exist')
    exit(-1)
fp = open(file_name)
print(fp)
file_sid = []
file_lat = []
file_lon = []
for i, line in enumerate(fp):
    if i < 1:                  # Skip first 2 lines from the file 
        continue
    if line in ['\n', '\r\n']: # End of file
        break
    if len(line.strip()) == 0: # Empty line
        break
    splitline = line.split()                # Split the line as the vector of values
    file_sid.append(int(splitline[csid]))   # The needed values are on the 27-th
    file_lat.append(float(splitline[clat])) #   28-th,
    file_lon.append(float(splitline[clon])) #   and 29-th positions
fp.close()
    
if len(file_sid) != len(file_lat):
    print('Something went very wrong')
    exit(-1)


df = pd.DataFrame({'ID': file_sid, 'LAT': file_lat, 'LON': file_lon})
df = df.drop_duplicates(subset=['ID'])
print(df)
df.to_csv(f'{outfile}', sep='\t', encoding='utf-8')
print(f'Output data file: {outfile}')

# Figure plotting
fig = pygmt.Figure()
topo_data = '@earth_relief_15s'

fig.grdimage(
    grid=topo_data,
    region=region,
    frame='afg',
    shading=True,
    projection='C47/-19/12c'
    )
fig.colorbar(
    frame='+l Elevation, m'
    )

fig.plot(
    x=df['LON'],
    y=df['LAT'],
    style='c0.12i',
    pen='black',
    fill='red')

fig.plot(x=olon, y=olat, style='a0.2i', fill='white', pen='black')
fig.savefig(plotname, crop=True, dpi=75)
print(f'Output plot: {plotname}')

'''
convert excel spreadsheets into ellitrack datafiles
'''
import pandas as pd
import os
import glob
from dateutil.parser import parse

src='/media/sf_C_DRIVE/Users/theo/Documents/projdirs/duivenvoorde/oudedata/tauw/gws'
dest=src

for fname in glob.glob(src+'/gws*.xlsx'):
    components = os.path.basename(fname).split('_')
    peilbuis = components[-1][:-5]
    print('Peilbuis '+peilbuis)
    df = pd.read_excel(fname)
    with open(os.path.join(dest,'Ellitrack-pb'+peilbuis+'.txt'),'w') as f:
        f.write('Datum\tWaterstand\tTemperatuur water\tTemperatuur intern\n')
        for row in df.itertuples():
            date = parse(row.PeilDtg)
            level = row.GWS_NAP
            temp1 = 0
            temp2 = 0
            f.write('\t'.join(map(str,[date.strftime('%Y-%m-%d %H:%M:%S'),level,temp1,temp2]))+'\n')
    
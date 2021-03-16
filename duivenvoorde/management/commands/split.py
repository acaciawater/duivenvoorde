'''
convert Tauw spreadsheets into ellitrack datafiles
'''
import glob
import logging
import os

from dateutil.parser import parse
from django.core.management.base import BaseCommand

from acacia.meetnet.models import LoggerPos
import pandas as pd


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Convert gws*.xlsx files van Tauw'
    
    def add_arguments(self,parser):
        
        parser.add_argument('folder', help = 'Folder met gws*.xlsx bestanden')

    def handle(self, *args, **options):
        
        src = options.get('folder')
        dest=src

        for fname in glob.glob(src+'/gws*.xlsx'):

            # find serial number of logger
            basename = os.path.basename(fname)
            components = basename.split('_')
            peilbuis_nummer = int(components[-1][:-5])
            peilbuis = 'Tauw %02d' % peilbuis_nummer
            
            installations = LoggerPos.objects.filter(screen__well__name__iexact=peilbuis)
            if not installations.exists():
                logger.error('Geen datalogger gevonden voor put {}'.format(peilbuis))
                continue
            
            serial = installations.latest('start_date').logger.serial
            logger.info('Reading {}'.format(basename))
            df = pd.read_excel(fname)

            filename = 'Ellitrack-{}-{}.txt'.format(serial, peilbuis)
            logger.info('Writing {} '.format(filename))
            
            with open(os.path.join(dest,filename),'w') as f:
                f.write('Datum\tWaterstand\tTemperatuur water\tTemperatuur intern\n')
                for row in df.itertuples():
                    date = parse(row.PeilDtg,dayfirst=True) # NL spreadsheet
                    level = row.GWS_NAP
                    temp1 = 0
                    temp2 = 0
                    f.write('\t'.join(map(str,[date.strftime('%Y-%m-%d %H:%M:%S'),level,temp1,temp2]))+'\n')
            
            

'''
Created on Jun 9, 2020

@author: theo
'''
import glob, os, logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from acacia.meetnet.models import Screen
import pandas as pd


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Import excel data from Tauw'
    
    def add_arguments(self,parser):
        
        parser.add_argument('folder', help = 'folder with timeseries data')

    def handle(self, *args, **options):
        # get the first superuser
        admin = User.objects.filter(is_superuser=True).first()
        folder = options.get('folder')
        logger.info('Importing from '+folder)
        for fname in glob.glob(os.path.join(folder,'*.xls?')):
            
            name, _ext = os.path.splitext(os.path.basename(fname))
            candidates = Screen.objects.filter(well__name__iexact=name)
            if not candidates.exists():
                logger.warning('No screen found for well %s' % name)
                continue
            if candidates.count() > 1:
                logger.warning('Multiple screens found matching well %s' % name)
                continue
            screen = candidates.first()

            series_name = '%s COMP' % str(screen)
            series,created = screen.mloc.series_set.update_or_create(name=series_name, defaults = {
                'timezone':'Etc/GMT-1', 
                'unit':'m', 
                'user': admin
            })

            if created:
                logger.debug('Created %s' % series)

            logger.debug('Reading %s' % fname)
            df = pd.read_excel(fname)
            if not 'Diverwaarde' in df.columns:
                # Not a proper timeseries speadsheet
                logger.warning('No timeseries found in %: skipped' % fname)
                continue
            
            try:
                df.set_index('DatumTijd',inplace=True)
                points = df['Diverwaarde'].tz_localize(series.timezone,ambiguous='infer')
                points = points.groupby(points.index).mean()
                logger.info('Updating %s (%d points)' % (series.name, points.size))
                series.replace_data(points)
            except Exception as e:
                logger.error(e)
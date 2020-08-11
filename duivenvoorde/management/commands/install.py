'''
Importeer logger installaties voor Tauw putten
'''
import logging

from django.core.management.base import BaseCommand

from acacia.meetnet.models import Screen, Datalogger
import pandas as pd
from datetime import datetime
import pytz


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Import installaties van Tauw putten'
    
    def add_arguments(self,parser):
        
        parser.add_argument('fname', help = 'Excel file met metadata')

    def handle(self, *args, **options):
        filename = options.get('fname')
        tz = pytz.timezone('Etc/GMT-1')
        logger.info('Importing from '+filename)
        df = pd.read_excel(filename,sheet_name='installaties')
        start = tz.localize(datetime(2000,01,01,01,0,0))
        for row in df.itertuples():
            name = row.Put
            serial = row.Logger
            
            datalogger, created = Datalogger.objects.get_or_create(serial=serial,model='etd')
            if created:
                logger.info('Created datalogger %s' % serial)
            
            candidates = Screen.objects.filter(well__name__iexact=name)
            if not candidates.exists():
                logger.warning('No screen found for well %s' % name)
                continue
            if candidates.count() > 1:
                logger.warning('Multiple screens found matching well %s' % name)
                continue
            screen = candidates.first()
            pos, created = screen.loggerpos_set.get_or_create(logger=datalogger,start_date=start,defaults={'refpnt': screen.refpnt})
            if created:
                logger.info('Created installation %s' % str(pos))
            
'''
Created on Sep 4, 2019

@author: theo
'''
from django.core.management.base import BaseCommand
import os,logging
from acacia.data.models import ManualSeries
from acacia.meetnet.models import Screen, Handpeilingen, Network
from django.contrib.auth.models import User
from django.conf import settings
import csv
from django.contrib.gis.geos.point import Point
from acacia.meetnet.util import register_well, register_screen
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'Import csv with well data'
    
    def add_arguments(self,parser):
        
        parser.add_argument('--file','-f',
                action='store',
                dest = 'fname',
                default = '',
                help = 'csv file with well data')

    def handle(self, *args, **options):
        # get the first superuser
#         user=User.objects.filter(is_superuser=True).first()
        fname = options.get('fname')
        if not fname:
            raise('csv file missing')
        net = Network.objects.first()
        with open(fname,'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row['LOCATIE']
                filter = int(row['FILTER'])
                x = float(row['X'])
                y = float(row['Y'])
                nitg = row['NITGCODE']
                loc = Point(x=x,y=y,srid=28992)
                loc.transform(4326)
                print(name,loc.x,loc.y)
                well,created = net.well_set.update_or_create(name=name,nitg=nitg,defaults={'location':loc})
                register_well(well)
                screen,created = well.screen_set.get_or_create(nr=filter)
                register_screen(screen)
                
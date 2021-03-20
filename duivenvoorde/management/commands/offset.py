import logging
import json

from django.core.management.base import BaseCommand
from django.db.models import F

from acacia.meetnet.models import LoggerPos
from datetime import timedelta
from acacia.data.models import Series, aware

logger = logging.getLogger(__name__)

def uncompensated(pos):
    ''' returns true is logger produces uncompensated data '''
    # old django version does not allow filtering on JSON field
    # return pos.logger.datasources.filter(config__compensated=False).exists()
    return any(filter(lambda d: json.loads(d.config).get('compensated',True)==False, pos.logger.datasources.all()))

class Command(BaseCommand):
    help = 'corrigeer voor offset nieuwe loggers'

    def add_arguments(self, parser):
        parser.add_argument('-d','--dry',action='store_true',dest='dry',help='Dry run: do not modify')
        parser.add_argument('-w','--well',dest='well',help='Name of well')
        parser.add_argument('-l','--limit',dest='limit',default=0.2,help='Tolerance')
    
    def handle(self, *args, **options):
        baro = Series.objects.get(name='Luchtdruk Voorschoten')
        
        # tolerantie voor aanpassingen
        limit = options.get('limit')
        tolerance = timedelta(hours=6)

        dry = options.get('dry')
        well = options.get('well')

        queryset = LoggerPos.objects.filter(logger__model__startswith='etd') # alleen ellitrack loggers
        if well:
            queryset = LoggerPos.objects.filter(screen__well__name=well)
            
        # Niet twee keer aanpassen...
        queryset = queryset.exclude(remarks__contains='aangepast')
        
        for pos in queryset.order_by('screen__well'):
            if not uncompensated(pos):
                continue
            screen = pos.screen
            start_date = aware(pos.start_date-timedelta(days=1),'utc').replace(hour=0,minute=0,second=0)
            hand = screen.get_manual_series(start=start_date)
            if hand is None or hand.empty:
                continue
            hand_date = min(hand.index)
            handpeiling = hand[hand_date]
            
            # zoek loggermeting tijdens of direct na de handpeiling
            levels = screen.get_compensated_series(start=hand_date).dropna()
            if levels is None or levels.empty:
                continue
            logger_date = min(levels.index)
            if logger_date - hand_date > tolerance:
                # tijdsverschil te groot
                continue

            # bereken verschil in meetwaarden
            loggerwaarde = levels[logger_date]
            verschil = loggerwaarde-handpeiling

            if abs(verschil) < limit:
                # verschil logger-handpeiling is binnen de limiet. Voer correctie uit
                # De kabellengte calibratie gaat uit van een luchtdruk van 1013 hPa
                # Als de werkelijke luchtdruk 1030 was tijdens calibratie in het veld, dan is gerekend met foutieve luchtdruk en 
                # wordt de kabellengte 17 cm te lang berekend (17 cm extra waterdruk door hogere luchtdruk)
                # in de luchtdruk compensatie (util.recomp()) wordt er van uitgegaan dat de kabellengte verdisconteerd is in de loggerbestanden
                # kabel aanpassingen heeft dus geen zin. Ophangpunt aanpassen kan wel 
                #
                # bereken offset door luchtdruk verschil. 
                hpa = baro.at(logger_date).value
                if baro.unit.startswith('0.1'):
                    hpa *= 0.1
                offset = 0.01 * (hpa - 1013) / 0.98123 
                # pas referentiepunt aan en rond af op mm
                refpnt = round(pos.refpnt+offset,3)
                logger.debug('{},{},{},{:+.1f} cm'.format(pos, pos.refpnt, refpnt, offset*100))
                if not dry:
                    pos.remarks = 'ophangpunt ({}) aangepast met {:+.2f} cm voor luchtdruk van {:.1f} hPa tijdens installatie.'.format(pos.refpnt, offset*100, hpa)
                    pos.refpnt = refpnt
                    pos.save()
                    series = screen.find_series()
                    if series:
                        logger.debug('Tijdreeks {} aanpassen...'.format(series))
                        # success = recomp(screen, series, start=pos.start_date,stop=pos.end_date)
                        q = series.datapoints.filter(date__gte=pos.start_date)
                        if pos.end_date:
                            q = q.filter(date__lte=pos.end_date)
                        q.update(value=F('value')+offset)
                        # TODO: revalidate and reload xl validation file
                        
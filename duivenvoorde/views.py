'''
Created on Sep 1, 2019

@author: theo
'''
import json

from django.conf import settings
from django.http.response import JsonResponse, HttpResponseServerError
from django.views.generic.detail import DetailView

from acacia.meetnet.models import Network, Well
from acacia.meetnet.views import NetworkView
from django.utils import timezone
from django.utils.timesince import timesince
import locale
from dateutil.parser import parser

def statuscolor(last):
    """ returns color for bullets on home page.
    Green is less than 1 day old, yellow is 1 - 2 days, red is 3 - 7 days and gray is more than one week old 
     """
    if last:
        now = timezone.now()
        age = now - last.date
        if age.days < 1:
            return 'green' 
        elif age.days < 2:
            return 'yellow'
        elif age.days < 7:
            return 'red' 
    return 'grey'

class HomeView(NetworkView):
    template_name = 'duivenvoorde/home.html'

    def get_context_data(self, **kwargs):
        context = NetworkView.get_context_data(self, **kwargs)
        options = {
            'center': [52.15478, 4.48565],
            'zoom': 12 }
        context['api_key'] = settings.GOOGLE_MAPS_API_KEY
        context['options'] = json.dumps(options)

        return context

    def get_object(self):
        return Network.objects.first()

class PopupView(DetailView):
    """ returns html response for leaflet popup """
    model = Well
    template_name = 'meetnet/well_info.html'

    
def well_locations(request):
    """ return json response with well data, latest measurement and status color
    """
    result = []
    queryset = Well.objects.filter(location__isnull=False)
    start = request.GET.get('start')
    if start:
        start = parser().parse(start).date()
        
#     hist = request.GET.get('h','0')
#     if hist == '0':
#         # exclude historic data (include VS* and WS* names
#         queryset = queryset.filter(name__regex=r'^[VW]S.+')
    #locale.setlocale(locale.LC_ALL, "nl_NL.utf8") # dates in Dutch
    for p in queryset:
        try:
            pnt = p.location
            last = p.last_measurement()
            if start:
                if (last is None) or (last.date and last.date.date() < start):
                    continue
 
            result.append({
                'id': p.id, 
                'name': p.name, 
                'nitg': p.nitg, 
                'description': p.description, 
                'lon': pnt.x, 
                'lat': pnt.y,
                'address': ', '.join([p.straat or '',p.plaats or '']),
                'latest': {'since': timesince(last.date), 'date': last.date.strftime('%A %-d %B %Y') if last.date else '-', 'value': last.value} if last else {},
                'color': statuscolor(last) 
                })
        except Exception as e:
            return HttpResponseServerError(unicode(e))

    return JsonResponse(result,safe=False)

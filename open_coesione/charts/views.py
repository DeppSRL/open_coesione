# -*- coding: utf-8 -*-
from collections import OrderedDict
from itertools import groupby
import json
from django.http import HttpResponse
from models import Indicatore, Ripartizione, IndicatoreRegionale


def indicatori(request):
    data = {
        'locations': OrderedDict(
            [(
                str(ripartizione.id),
                {
                    'name': ripartizione.descrizione,
                }
            ) for ripartizione in Ripartizione.objects.with_value().order_by('id')]
        ),
        'topics': OrderedDict(
            [(
                tema.codice,
                {
                    'name': tema.descrizione,
                    'indicators': OrderedDict(
                        [(
                            indicatore.codice,
                            {
                                'title': indicatore.titolo,
                                'subtitle': indicatore.sottotitolo,
                            }
                        ) for indicatore in indicatori]
                    ),
                }
            ) for tema, indicatori in groupby(Indicatore.objects.with_value().order_by('tema__priorita', 'codice').prefetch_related('tema'), key=lambda x: x.tema)]
        ),
    }

    return HttpResponse(json.dumps(data), mimetype='application/json')


def indicatori_regionali(request, indicatore_id):
    data = OrderedDict(
        [(
            ripartizione,
            [{
                'year': int(indicatore_regionale.anno),
                'value': float(indicatore_regionale.valore),
            } for indicatore_regionale in indicatori_regionali],
        ) for ripartizione, indicatori_regionali in groupby(IndicatoreRegionale.objects.filter(indicatore=indicatore_id).exclude(valore='').order_by('indicatore', 'ripartizione', 'anno'), key=lambda x: x.ripartizione_id)]
    )

    return HttpResponse(json.dumps(data), mimetype='application/json')

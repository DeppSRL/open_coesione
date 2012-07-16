from django.conf import settings
from open_coesione.data_classification import DataClassifier
from territori.models import Territorio
from progetti.models import Progetto

territori = Territorio.objects.filter(territorio='P', cod_reg=2)
data = dict((t.codice, Progetto.objects.totale_costi(territorio=t)) for t in territori)

classes_number = 5
if len(data) < 5:
    classes_number = len(data)

dc = DataClassifier(data.values(), classifier_args={'k':classes_number}, colors_map=settings.MAP_COLORS)
print dc.get_bins_ranges()

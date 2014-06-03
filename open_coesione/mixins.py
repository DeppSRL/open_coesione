import datetime
from django.utils import timezone

class DateFilterMixin(object):
    def _get_date_filter_value(self):
        return self.request.GET.get('date', None)

    def _apply_date_filter(self, qs):
        filter_value = self._get_date_filter_value()
        if filter_value is not None:
            now = timezone.now()
            start_date = now.date()
            end_date = start_date + datetime.timedelta(days = 1)
            if filter_value == 'w':
                start_date = start_date - datetime.timedelta(days=7)
            elif filter_value == 'm':
                start_date = start_date.replace(day=1)
            elif filter_value == 'y':
                start_date = start_date.replace(month=1, day=1)
            qs = qs.filter(published_at__gte=start_date, published_at__lt=end_date)
        return qs

    def _get_date_choices(self):
        filter_value = self._get_date_filter_value()

        choices = [
            {
                'name': 'Oggi',
                'param': 't',
            },
            {
                'name': 'Ultimi 7 giorni',
                'param': 'w',
            },
            {
                'name': 'Questo mese',
                'param': 'm',
            },
            {
                'name': "Quest'anno",
                'param': 'y',
            }
        ]
        for choice in choices:
            choice['selected'] = choice['param'] == filter_value
        return choices

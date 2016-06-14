from _csv import register_dialect, QUOTE_ALL
import csv
import codecs
import cStringIO
import datetime
import csvkit
from django.core.mail.backends.filebased import EmailBackend
import os
from django.http import HttpResponse


class EncodedRecoder:
    """
    Iterator that reads an encoded stream and reencodes the input to the specified encoding
    """
    def __init__(self, f, encoding="utf-8"):
        self.reader = codecs.getreader(encoding)(f)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode(self.encoding)


class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = EncodedRecoder(f, encoding)
        self.reader = csv.DictReader(f, dialect=dialect, **kwds)
        self.encoding = encoding

    def next(self):
        row = self.reader.next()
        return dict((k, s.decode(self.encoding)) for k, s in row.iteritems() if s is not None)

    @property
    def columns(self):
        return tuple(self.reader.fieldnames)

    def __iter__(self):
        return self


class UnicodeDictWriter(object):
    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.encoding = encoding

    def _unicode_row(self):
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode(self.encoding)
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writeheader(self):
        header = dict(zip(self.writer.fieldnames, self.writer.fieldnames))
        self.writerow(header)

    def writerow(self, D):
        self.writer.writerow(dict([(k, v.encode(self.encoding)) for k, v in D.items()]))
        self._unicode_row()

    def writerow_list(self, L):
        self.writer.writer.writerow([v.encode(self.encoding) for v in L])
        self._unicode_row()

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)


class excel_semicolon(csv.excel):
    """Extends excel Dialect in order to set semicolon as delimiter."""
    delimiter = ';'
    quoting = QUOTE_ALL

register_dialect("excel_semicolon", excel_semicolon)


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.encoding = encoding

    def writerow(self, row):
        self.writer.writerow([s.encode(self.encoding) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode(self.encoding)
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)



def export_select_fields_csv_action(description="Export selected objects as CSV file",
                                    fields=None, exclude=None, header=True):
    """
    This function returns an export csv action

    'fields' is a list of tuples denoting the field and label to be exported. Labels
    make up the header row of the exported file if header=True.

        fields=[
                ('field1', 'label1'),
                ('field2', 'label2'),
                ('field3', 'label3'),
            ]
    You can use the ORM lookup '__' syntax to access related fields,
    but the existance of the field is not checked in advance.
    Errors are trapped in this case and '' is returned as value.

    'exclude' is a flat list of fields to exclude. If 'exclude' is passed,
    'fields' will not be used. Either use 'fields' or 'exclude.'

        exclude=['field1', 'field2', field3]

    'header' is whether or not to output the column names as the first row

    Based on: http://djangosnippets.org/snippets/2020/
    """
    def extended_getattr(obj, attribute_name):
        if obj is None:
            return ''

        if '__' in attribute_name:
            (a1, a2) = attribute_name.split('__', 1)
            try:
                o = getattr(obj, a1)
            except AttributeError:
                o = None
            return extended_getattr(o, a2)
        else:
            try:
                return getattr(obj, attribute_name)
            except AttributeError:
                return ''


    def export_as_csv(modeladmin, request, queryset):
        """
        Generic csv export admin action.
        based on http://djangosnippets.org/snippets/1697/
        """
        opts = modeladmin.model._meta
        standard_field_names = [field.name for field in opts.fields]
        labels = []
        if exclude:
            field_names = [v for v in standard_field_names if v not in exclude]
        elif fields:
            field_names = [k for k, v in fields if k in standard_field_names or '__' in k or k == 'pippo']
            labels = [v for k, v in fields if k in standard_field_names or '__' in k or k == 'pippo']
        else:
            field_names = standard_field_names

        # uncomment this if download is not required required
        # response = HttpResponse(mimetype='text/plain; charset=utf8')

        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % unicode(opts).replace('.', '_')

        writer = csvkit.unicsv.UnicodeCSVWriter(response, delimiter=',')
        if header:
            if labels:
                writer.writerow(labels)
            else:
                writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([extended_getattr(obj, field) for field in field_names])
        return response


    export_as_csv.short_description = description
    return export_as_csv




def setup_view(view, request, *args, **kwargs):
    """
    Mimic as_view() returned callable, but returns view instance.
    args and kwargs are the same you would pass to ``reverse()``

    add slug=SLUG, and view.object = view.get_object() for classes that
    inherit from detail view
    """
    view.request = request
    view.args = args

    view.inner_filter = kwargs.pop('inner_filter', None)
    view.kwargs = kwargs

    return view


class EMLBackend(EmailBackend):
    """
    Class that writes email into a specified location, using the eml extension, rather than the default log one
    """
    def __init__(self, *args, **kwargs):
        super(EMLBackend, self).__init__(*args, **kwargs)
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        fname = "%s-%s.eml" % (timestamp, abs(id(self)))
        self._fname = os.path.join(self.file_path, fname)

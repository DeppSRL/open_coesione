# coding=utf-8
"""
 COD_INDICATORE;
 TITOLO;
 SOTTOTITOLO;
ID_TEMA1;
DESCRIZIONE_TEMA1;
ID_TEMA2;
DESCRIZIONE_TEMA2;
ID_PRIORITA;
DESCRIZIONE_PRIORITA_QSN;
ID_ASSE;
DESCRIZIONE_ASSE_QCS;
 ID_RIPARTIZIONE;
 DESCRIZIONE_RIPARTIZIONE;
 ANNO_RIFERIMENTO;
 VALORE;
 DESCRIZIONE_TEMA_SINTETICO
"""
import cStringIO
import codecs
from open_coesione import settings_local as settings
__author__ = 'daniele'


import csv
import locale
import copy
locale.setlocale(locale.LC_ALL, '')

csvfile = 'dati/istat.csv'
csvfile_encoding = 'latin'
indexes_allowed_file = 'dati/temi_indicatori.csv'

regioni_id_range = range(1,21) + [23]

temi_db_mapping = settings.TEMI_DB_MAPPING

# Prepare structures
db = {
    'regioni': {},
    'temi': {},
    'indici': {},
    'valori': {},
    'anni': [],
    'indici_per_tema': {}
}
hits = copy.deepcopy(db)

def read_location(line):
    id = int(line['ID_RIPARTIZIONE'])
    if not id in regioni_id_range:
        return False
    if not id in db['regioni']:
        db['regioni'][id] = unicode(line['DESCRIZIONE_RIPARTIZIONE'],csvfile_encoding)
        hits['regioni'][id] = 0
    return id

def read_topic(line):
    name = unicode(line['DESCRIZIONE_TEMA_SINTETICO'],csvfile_encoding)
    # try to load this topic from mapping
    id = temi_db_mapping[name]

    if not id in db['temi']:
        # add this topic to db
        db['temi'][id] = name
        hits['temi'][id] = 0
    return id

def read_index_value(line):
    id = line['COD_INDICATORE'].strip()
    year = int(line['ANNO_RIFERIMENTO'])

    if not id in db['indici']:
        db['indici'][id] = {
            'titolo': unicode(line['TITOLO'], csvfile_encoding),
            'sottotitolo': unicode(line['SOTTOTITOLO'], csvfile_encoding)
        }
        hits['indici'][id] = 0

    return id, year, (locale.atof(line['VALORE']) if line['VALORE'] else None)

def main():
    # take allowed indexes
    allowed_indexes = settings.INDICATORI_VALIDI

    # open file
    file = open(csvfile, 'rb')
    # make a csv reader
    reader = csv.DictReader(file, delimiter=';' )
    # parse data
    for row in reader:
        # skip not allowed index
        if not row['COD_INDICATORE'].strip() in allowed_indexes:
            continue

        # read location
        regione_id = read_location(row)

        if not regione_id:
            # skip if not in regioni_id_range
            continue

        hits['regioni'][regione_id] += 1

        # read topic
        tema_id = read_topic(row)

        hits['temi'][tema_id] += 1

        # read index
        index_id, year, value = read_index_value(row)

        hits['indici'][index_id] += 1

        # link this index with topic
        if not tema_id in db['indici_per_tema']:
            db['indici_per_tema'][tema_id] = []

        if not index_id in db['indici_per_tema'][tema_id]:
            db['indici_per_tema'][tema_id].append(index_id)

        if not year in db['anni']:
            db['anni'].append(year)

        if not index_id in db['valori']:
            # initialize db for this index
            db['valori'][index_id] = {}

        if not regione_id in db['valori'][index_id]:
            # initialize db with this region with this index
            db['valori'][index_id][regione_id] = {}

        # add index value to db
        db['valori'][index_id][regione_id][year] = value

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

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def write():
    years = db['anni']
    temaind_fieldnames = ['Regione'] + [str(y) for y in years]
    #temareg_fieldnames = ['Indicatore'] + years

    temi_fieldnames =       ['ID', 'Denominazione tema sintetico']
    indicatori_fieldnames = ['ID', 'Titolo', 'Sottotitolo']
    regioni_fieldnames =    ['ID', 'Denominazione regione']

    print "scrittura regioni"
    with open("dati/istat/regioni.csv", 'wb') as wf:
        # init writer
        writer = UnicodeWriter(wf)
        # write headers
        writer.writerow(regioni_fieldnames)
        # iterate on sorted locations by id
        for loc_id in sorted(db['regioni']):
            print "  %s" % db['regioni'][loc_id]
            writer.writerow( [ str(loc_id), db['regioni'][loc_id] ] )

    print " "

    print "scrittura temi"
    with open("dati/istat/temi.csv", 'wb') as wf:
        # init writer
        writer = UnicodeWriter(wf)
        # write headers
        writer.writerow(temi_fieldnames)
        # iterate on sorted locations by id
        for topic_id in sorted(db['temi']):
            print "  %s" % db['temi'][topic_id]
            writer.writerow( [ str(topic_id), db['temi'][topic_id] ] )

    print " "

    print "loop costruzione file csv distinti"
    for topic_id in sorted(db['indici_per_tema']):
        print " TEMA: %s" % db['temi'][topic_id]

        with open("dati/istat/indicatori/%s.csv" % topic_id, 'wb') as wf:
            writer = UnicodeWriter(wf)

            # write headers
            writer.writerow(indicatori_fieldnames)

            # write index in this topic
            for index_id in sorted(db['indici_per_tema'][topic_id]):
                index = db['indici'][index_id]
                print "  %s, %s" % ( index['titolo'], index['sottotitolo'] )
                writer.writerow( [ index_id , index['titolo'], index['sottotitolo'] ] )

                ind_writer = UnicodeWriter(open("dati/istat/temaind/%s_%s.csv" % ( topic_id, index_id ), 'wb'))

                # write headers
                ind_writer.writerow(temaind_fieldnames)

                for location_id in sorted(db['valori'][index_id]):

                    values = [ db['regioni'][location_id], ]
                    # collect values
                    for year in db['valori'][index_id][location_id]:
                        val = db['valori'][index_id][location_id][year]
                        values.append( str(val) if val else '' )

                    ind_writer.writerow( values )




if __name__ == '__main__':

    print "** Read CSV istat.csv **"
    main()
    print "** Split in files.. **"
    write()
    print "** THE END ***"
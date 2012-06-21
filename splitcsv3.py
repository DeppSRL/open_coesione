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
__author__ = 'daniele'


import csv
import locale
import copy
locale.setlocale(locale.LC_ALL, '')

csvfile = 'dati/istat.csv'
csvfile_encoding = 'latin'
index_ignore_file = ''

regioni_id_range = range(1,21) + [23]
temi_db_mapping = {
    u'Competitivit\xe0 per le imprese' : 6,
    u'Ambiente e prevenzione dei rischi' : 11 ,
    u'Occupazione e mobilit\xe0 dei lavoratori' : 2,
    u'Attrazione culturale, naturale e turistica' : 7,
    u'Trasporti e infrastrutture a rete' : 13,
    u'Rinnovamento urbano e rurale' : 12,
    u'Energia e efficienza energetica' : 5,
    u'Agenda digitale' : 4,
    u'Istruzione' : 3,
    u'Rafforzamento delle capacit\xe0 della PA' : 10,
    u'Inclusione sociale' : 1,
    u'Ricerca e innovazione' : 9 ,
    u'Servizi di cura infanzia e anziani' : 8
}

# Prepare structures
db = {
    'regioni': {},
    'temi': {},
    'indici': {},
    'valori': {},
    'anni': []
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
    id = int(line['COD_INDICATORE'])
    year = int(line['ANNO_RIFERIMENTO'])

    if not id in db['indici']:
        db['indici'][id] = {
            'titolo': unicode(line['TITOLO'], csvfile_encoding),
            'sottotitolo': unicode(line['SOTTOTITOLO'], csvfile_encoding),
        }
        hits['indici'][id] = 0

    return id, year, (locale.atof(line['VALORE']) if line['VALORE'] else 0.0)

def main():
    # open file
    file = open(csvfile, 'rb')
    # make a csv reader
    reader = csv.DictReader(file, delimiter=';' )
    # parse data
    for row in reader:
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

        if not index_id in db['valori']:
            # initialize db for this index
            db['valori'][index_id] = {}

        if not regione_id in db['valori'][index_id]:
            # initialize db with this region with this index
            db['valori'][index_id][regione_id] = {}

        # add index value to db
        db['valori'][index_id][regione_id][year] = value
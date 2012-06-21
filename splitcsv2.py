"""
Splits global CSV file for ISTAT indicators into many different CSV files suitable
for usage within highcharts js library.
Files are written in an outer path, and must be copied inside the static/csv path,
in order to be harvested by the collectstatic command.

TODO:
This is a temporary solution and the complete flow must be improved.
"""

import csv, sys
import locale


locale.setlocale(locale.LC_ALL, '')

indicatori_ammessi = []
with open('dati/temi_indicatori.csv') as file_indicatori:
    reader = csv.DictReader(file_indicatori, delimiter=';')
    try:
        for row in reader:
            if not row['IID'] == '000':
                indicatori_ammessi.append(row['IID'])
    except csv.Error, e:
        sys.exit('file %s, line %d: %s' % ('dati/temi_indicatori.csv', reader.line_num, e))

csvfile = 'dati/istat.csv'
with open(csvfile, 'rb') as f:
    reader = csv.DictReader(f, delimiter=';')
    rows = []
    try:
        for row in reader:
            if row['COD_INDICATORE'] in indicatori_ammessi:
                rows.append(row)
            #if reader.line_num > 50000:
            #    break
    except csv.Error, e:
        sys.exit('file %s, line %d: %s' % (csvfile, reader.line_num, e))

    years = [str(y) for y in range(1995, 2012)]
    temaind_fieldnames = ['Regione'] + years
    temareg_fieldnames = ['Indicatore'] + years

    temi_fieldnames = ['ID', 'Denominazione tema sintetico']
    indicatori_fieldnames = ['ID', 'Titolo', 'Sottotitolo']
    regioni_fieldnames = ['ID', 'Denominazione regione']


    print "scrittura regioni"
    regions = list(set([(r['ID_RIPARTIZIONE'], r['DESCRIZIONE_RIPARTIZIONE']) for r in rows if r['ID_RIPARTIZIONE'] in [str(k) for k in range(1, 21) + [23]]]))
    with open("dati/istat/regioni.csv", 'wb') as wf:
        writer = csv.writer(wf, regioni_fieldnames)

        # write headers
        writer.writerow(regioni_fieldnames)
        regions.sort(cmp=lambda x,y: cmp(int(x[0]), int(y[0])))
        for reg in regions:
            print "  %s" % reg[1]
            writer.writerow([reg[0], reg[1].decode('latin1').encode('utf-8')])


    print " "

    print "scrittura temi"
    themes = set([r['DESCRIZIONE_TEMA_SINTETICO'].decode('latin1').encode('utf-8')for r in rows])
    with open("dati/istat/temi.csv", 'wb') as wf:
        writer = csv.writer(wf, temi_fieldnames)

        # write headers
        writer.writerow(temi_fieldnames)

        for n_tema, t in enumerate(themes, start=1):
            print "  %s" % t
            writer.writerow([n_tema, t])

    print " "
    print "loop costruzione file csv distinti"
    for n_tema, t in enumerate(themes, start=1):
        print t
        theme_rows = [r for r in rows if r['DESCRIZIONE_TEMA_SINTETICO'].decode('latin1').encode('utf-8')==t]

        indicators_codes = list(set([(r['COD_INDICATORE'],
                                      r['TITOLO'].decode('latin1').encode('utf-8'),
                                      r['SOTTOTITOLO'].decode('latin1').encode('utf-8')) for r in theme_rows]))
        with open("dati/istat/indicatori/%s.csv" % n_tema, 'wb') as wf:
            writer = csv.writer(wf, temi_fieldnames)

            # write headers
            writer.writerow(indicatori_fieldnames)

            for i in indicators_codes:
                print "  %s, %s" % (i[0], i[1])
                writer.writerow(i)


        for i in indicators_codes:
            print "  %s, %s" % (i[0], i[1])
            indicators_rows = [r for r in theme_rows if r['COD_INDICATORE']==i[0]]
            regions = list(set([(r['ID_RIPARTIZIONE'], r['DESCRIZIONE_RIPARTIZIONE']) for r in indicators_rows if r['ID_RIPARTIZIONE'] in [str(k) for k in range(1, 21) + [23]]]))
            temaind_filename = "dati/istat/temaind/%s_%s.csv" % (n_tema, i[0])
            with open(temaind_filename, 'wb') as wf:
                writer = csv.DictWriter(wf, temaind_fieldnames)

                # write headers
                headers = {}
                for n in temaind_fieldnames:
                    headers[n] = n
                writer.writerow(headers)

                regions.sort(cmp=lambda x,y: cmp(int(x[0]), int(y[0])))
                for reg in regions:
                    region_rows = [r for r in indicators_rows if r['ID_RIPARTIZIONE']==reg[0]]
                    values = [reg[1].decode('latin1').encode('utf-8')]
                    for r in region_rows:
                        if r['VALORE']:
                            values.append(str(locale.atof(r['VALORE'])))
                        else:
                            values.append('')
                    dictrow = dict(zip(temaind_fieldnames, values))
                    writer.writerow(dictrow)



#        regions = list(set([(r['ID_RIPARTIZIONE'], r['DESCRIZIONE_RIPARTIZIONE']) for r in theme_rows if r['ID_RIPARTIZIONE'] in [str(k) for k in range(1, 21) + [23]]]))
#        for reg in regions:
#            print "  %s" % reg[1]
#            region_rows = [r for r in theme_rows if r['ID_RIPARTIZIONE']==reg[0]]
#            indicators_codes = list(set([(r['COD_INDICATORE'], r['TITOLO'].decode('latin1').encode('utf-8')) for r in region_rows]))
#            temareg_filename = "dati/istat/temareg/%s_%s.csv" % (n_tema, reg[0])
#            with open(temareg_filename, 'wb') as wf:
#                writer = csv.DictWriter(wf, temareg_fieldnames)
#
#                # write headers
#                headers = {}
#                for n in temareg_fieldnames:
#                    headers[n] = n
#                writer.writerow(headers)
#
#                for i in indicators_codes:
#                    indicator_rows = [r for r in region_rows if r['COD_INDICATORE']==i[0]]
#                    values = [i[1]]
#                    for r in indicator_rows:
#                        if r['VALORE']:
#                            values.append(str(locale.atof(r['VALORE'])))
#                        else:
#                            values.append('')
#                    dictrow = dict(zip(temareg_fieldnames, values))
#                    writer.writerow(dictrow)

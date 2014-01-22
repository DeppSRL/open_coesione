# This script produces/overwrites sample csv files of size N out of original full CSV files.

# parameters can be set here, to point to the correct position
# and fix sample's size
export DATA_ROOT=dati/dataset_dev # data path where original csv are (and produced sample will be)
export DATE=FSC0713_20131031 # suffix in csv filenames
export N=500 # sample size

pushd $DATA_ROOT

echo "prepare progetti sample of size $N - uses shuf command"
head -n 1 progetti_$DATE.csv > progetti_sample.csv
tail -n +2 progetti_$DATE.csv | shuf -n $N | sort >> progetti_sample.csv

echo sort localizzazioni, soggetti and pagamenti full csv files - if needed
if [ ! -f localizzazioni_sorted.csv ]; then
    head -n 1 localizzazioni_$DATE.csv > localizzazioni_sorted.csv
    tail -n +2 localizzazioni_$DATE.csv | sort >> localizzazioni_sorted.csv
fi

if [ ! -f soggetti_sorted.csv ]; then
    head -n 1 soggetti_$DATE.csv > soggetti_sorted.csv
    tail -n +2 soggetti_$DATE.csv | sort >> soggetti_sorted.csv
fi

if [ ! -f pagamenti_sorted.csv ]; then
    head -n 1 pagamenti_$DATE.csv > pagamenti_sorted.csv
    tail -n +2 pagamenti_$DATE.csv | sort >> pagamenti_sorted.csv
fi


echo generates header for sample files
head -n 1 localizzazioni_$DATE.csv > localizzazioni_sample.csv
head -n 1 soggetti_$DATE.csv > soggetti_sample.csv
head -n 1 pagamenti_$DATE.csv > pagamenti_sample.csv

popd

echo extract related records and append them to sample csv files
python manage.py extractsamplesrelated --data-root=$DATA_ROOT --sample=progetti_sample.csv --type=loc localizzazioni_sorted.csv >> $DATA_ROOT/localizzazioni_sample.csv
python manage.py extractsamplesrelated --data-root=$DATA_ROOT --sample=progetti_sample.csv --type=rec soggetti_sorted.csv >> $DATA_ROOT/soggetti_sample.csv
python manage.py extractsamplesrelated --data-root=$DATA_ROOT --sample=progetti_sample.csv --type=pay pagamenti_sorted.csv >> $DATA_ROOT/pagamenti_sample.csv

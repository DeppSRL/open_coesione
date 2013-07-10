rm cache_generation.log
touch cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log




curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/agenda-digitale/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/agenda-digitale/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/agenda-digitale/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/agenda-digitale/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/agenda-digitale{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/ambiente/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/ambiente/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/ambiente/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/ambiente/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/ambiente{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/citta-e-aree-rurali/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/citta-e-aree-rurali/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/citta-e-aree-rurali/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/citta-e-aree-rurali/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/citta-e-aree-rurali{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/competitivita-imprese/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/competitivita-imprese/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/competitivita-imprese/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/competitivita-imprese/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/competitivita-imprese{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/cultura-e-turismo/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/cultura-e-turismo/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/cultura-e-turismo/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/cultura-e-turismo/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/cultura-e-turismo{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/energia/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/energia/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/energia/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/energia/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/energia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/inclusione-sociale/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/inclusione-sociale/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/inclusione-sociale/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/inclusione-sociale/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/inclusione-sociale{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/infanzia-e-anziani/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/infanzia-e-anziani/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/infanzia-e-anziani/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/infanzia-e-anziani/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/infanzia-e-anziani{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/istruzione/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/istruzione/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/istruzione/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/istruzione/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/istruzione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/occupazione/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/occupazione/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/occupazione/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/occupazione/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/occupazione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/rafforzamento-pa/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/rafforzamento-pa/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/rafforzamento-pa/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/rafforzamento-pa/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/rafforzamento-pa{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/ricerca-e-innovazione/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/ricerca-e-innovazione/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/ricerca-e-innovazione/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/ricerca-e-innovazione/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/ricerca-e-innovazione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/trasporti/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/temi/trasporti/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/trasporti/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/temi/trasporti/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/temi/trasporti{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log





curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/acquisto-beni-e-servizi/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/acquisto-beni-e-servizi/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/acquisto-beni-e-servizi/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/acquisto-beni-e-servizi/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/tipologie/acquisto-beni-e-servizi{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/lavori-pubblici/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/lavori-pubblici/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/lavori-pubblici/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/lavori-pubblici/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/tipologie/lavori-pubblici{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/incentivi-alle-imprese/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/incentivi-alle-imprese/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/incentivi-alle-imprese/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/incentivi-alle-imprese/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/tipologie/incentivi-alle-imprese{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/contributi-a-persone/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/contributi-a-persone/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/contributi-a-persone/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/contributi-a-persone/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/tipologie/contributi-a-persone{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/conferimenti-capitale/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/conferimenti-capitale/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/conferimenti-capitale/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/conferimenti-capitale/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/tipologie/conferimenti-capitale{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/non-disponibile/regioni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/nature/non-disponibile/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/non-disponibile/regioni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/nature/non-disponibile/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/progetti/tipologie/non-disponibile{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log





curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/13/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/13/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/13/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/13/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/abruzzo-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/17/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/17/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/17/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/17/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/basilicata-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/18/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/18/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/18/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/18/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/calabria-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/15/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/15/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/15/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/15/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/campania-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/8/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/8/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/8/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/8/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/emilia-romagna-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/6/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/6/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/6/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/6/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/friuli-venezia-giulia-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/12/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/12/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/12/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/12/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/lazio-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/7/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/7/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/7/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/7/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/liguria-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/3/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/3/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/3/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/3/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/lombardia-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/11/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/11/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/11/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/11/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/marche-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/14/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/14/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/14/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/14/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/molise-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/1/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/1/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/1/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/1/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/piemonte-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/16/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/16/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/16/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/16/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/puglia-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/20/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/20/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/20/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/20/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/sardegna-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/19/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/19/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/19/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/19/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/sicilia-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/9/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/9/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/9/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/9/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/toscana-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/4/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/4/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/4/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/4/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/trentino-alto-adigesudtirol-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/10/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/10/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/10/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/10/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/umbria-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/2/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/2/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/2/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/2/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/valle-daostavallee-daoste-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/5/province.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/regioni/5/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/5/province.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/regioni/5/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/regioni/veneto-regione{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log






curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/84/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/84/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/agrigento-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/6/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/6/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/alessandria-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/42/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/42/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/ancona-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/51/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/51/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/arezzo-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/44/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/44/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/ascoli-piceno-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/5/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/5/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/asti-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/64/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/64/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/avellino-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/72/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/72/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/bari-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/110/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/110/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/barletta-andria-trani-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/25/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/25/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/belluno-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/62/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/62/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/benevento-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/16/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/16/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/bergamo-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/96/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/96/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/biella-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/37/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/37/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/bologna-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/21/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/21/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/bolzanobozen-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/17/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/17/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/brescia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/74/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/74/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/brindisi-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/92/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/92/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/cagliari-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/85/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/85/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/caltanissetta-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/70/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/70/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/campobasso-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/107/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/107/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/carbonia-iglesias-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/61/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/61/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/caserta-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/87/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/87/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/catania-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/79/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/79/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/catanzaro-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/69/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/69/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/chieti-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/13/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/13/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/como-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/78/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/78/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/cosenza-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/19/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/19/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/cremona-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/101/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/101/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/crotone-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/4/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/4/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/cuneo-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/86/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/86/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/enna-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/109/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/109/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/fermo-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/38/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/38/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/ferrara-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/48/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/48/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/firenze-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/71/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/71/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/foggia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/40/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/40/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/forli-cesena-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/60/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/60/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/frosinone-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/10/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/10/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/genova-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/31/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/31/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/gorizia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/53/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/53/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/grosseto-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/8/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/8/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/imperia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/94/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/94/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/isernia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/66/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/66/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/laquila-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/11/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/11/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/la-spezia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/59/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/59/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/latina-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/75/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/75/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/lecce-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/97/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/97/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/lecco-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/49/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/49/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/livorno-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/98/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/98/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/lodi-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/46/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/46/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/lucca-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/43/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/43/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/macerata-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/20/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/20/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/mantova-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/45/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/45/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/massa-carrara-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/77/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/77/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/matera-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/106/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/106/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/medio-campidano-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/83/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/83/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/messina-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/15/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/15/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/milano-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/36/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/36/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/modena-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/108/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/108/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/monza-e-della-brianza-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/63/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/63/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/napoli-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/3/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/3/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/novara-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/91/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/91/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/nuoro-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/105/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/105/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/ogliastra-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/104/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/104/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/olbia-tempio-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/95/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/95/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/oristano-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/28/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/28/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/padova-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/82/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/82/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/palermo-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/34/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/34/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/parma-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/18/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/18/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/pavia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/54/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/54/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/perugia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/41/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/41/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/pesaro-e-urbino-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/68/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/68/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/pescara-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/33/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/33/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/piacenza-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/50/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/50/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/pisa-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/47/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/47/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/pistoia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/93/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/93/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/pordenone-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/76/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/76/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/potenza-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/100/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/100/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/prato-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/88/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/88/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/ragusa-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/39/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/39/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/ravenna-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/80/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/80/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/reggio-di-calabria-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/35/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/35/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/reggio-nellemilia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/57/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/57/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/rieti-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/99/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/99/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/rimini-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/58/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/58/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/roma-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/29/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/29/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/rovigo-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/65/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/65/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/salerno-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/90/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/90/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/sassari-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/9/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/9/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/savona-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/52/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/52/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/siena-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/89/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/89/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/siracusa-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/14/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/14/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/sondrio-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/73/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/73/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/taranto-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/67/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/67/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/teramo-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/55/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/55/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/terni-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/1/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/1/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/torino-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/81/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/81/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/trapani-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/22/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/22/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/trento-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/26/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/26/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/treviso-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/32/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/32/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/trieste-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/30/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/30/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/udine-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/7/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/7/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/valle-daosta-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/12/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/12/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/varese-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/27/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/27/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/venezia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/103/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/103/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/verbano-cusio-ossola-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/2/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/2/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/vercelli-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/23/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/23/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/verona-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/102/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/102/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/vibo-valentia-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/24/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/24/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/vicenza-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log



curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/mapnik/province/56/comuni.xml{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log
curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/leaflet/province/56/comuni.json{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log


curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it/territori/province/viterbo-provincia{,?tematizzazione=totale_costi,?tematizzazione=totale_pagamenti,?tematizzazione=totale_progetti,?tematizzazione=totale_costi_procapite}" >> cache_generation.log




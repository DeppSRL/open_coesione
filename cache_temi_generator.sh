
rm cache_generation.log
touch cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/ambiente{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/citta-e-aree-rurali{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/competitivita-imprese{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/cultura-e-turismo{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/energia{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/inclusione-sociale{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/infanzia-e-anziani{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/istruzione{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/occupazione{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/rafforzamento-pa{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/ricerca-e-innovazione{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/temi/trasporti{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/tipologie/acquisto-beni-e-servizi{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/tipologie/lavori-pubblici{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/tipologie/incentivi-alle-imprese{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/tipologie/contributi-a-persone{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/tipologie/conferimenti-capitale{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log

curl -L -o/dev/null -w '%{url_effective} - %{http_code} (%{time_total}sec.)\n' "http://opencoesione.gov.it:8010/progetti/tipologie/non-disponibile{/,/?tematizzazione=totale_costi,/?tematizzazione=totale_pagamenti,/?tematizzazione=totale_progetti}" >> cache_generation.log



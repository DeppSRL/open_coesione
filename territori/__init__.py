import TileStache
# Singleton module
_my_tiles_config = None

def getTilesConfig():
    global _my_tiles_config
    if _my_tiles_config is None:
        config = {
            "cache": {"name": "Test"},
            "layers": {
                "regioni": {
                    "provider": {
                        "name": "vector",
                        "driver": "shapefile",
                        "parameters": {"file": "/Users/guglielmo/Workspace/open_coesione/dati/reg2011_g/regioni_stats.shp"}
                    },
                    "projection": "spherical mercator"
                }
            }
        }
        _my_tiles_config = TileStache.Config.buildConfiguration(config)
    return _my_tiles_config


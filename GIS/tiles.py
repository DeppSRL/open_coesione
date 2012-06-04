import TileStache
import ModestMaps
from optparse import OptionParser

parser = OptionParser()

(options, args) = parser.parse_args()

r = 0
c = 0
z = 0

if len(args) >= 1:
    r = int(args[0])
if len(args) >= 2:
    c = int(args[1])
if len(args) == 3:
    z = int(args[2])

config = {
    "cache": {"name": "Test"},
    "layers": {
        "comuni": {
            "provider": {"name": "mapnik", "mapfile": "comuni_italia.xml"},
            "projection": "spherical mercator"
        }
    }
}

# like http://tile.openstreetmap.org/1/0/0.png
coord = ModestMaps.Core.Coordinate(r, c, z)
config = TileStache.Config.buildConfiguration(config)
type, bytes = TileStache.getTile(config.layers['comuni'], coord, 'png')
filename = 'tile_%s_%s_%s.png' % (r, c, z)
open(filename, 'w').write(bytes)

print "tile %s created\n" % filename

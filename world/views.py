import TileStache
from django.http import HttpResponse
from django.views.generic import View, TemplateView

import json
from django import http


class TilesView(TemplateView):
    config = {
        "cache": {"name": "Test"},
        "layers": {
            "comuni": {
                "provider": {
                    "name": "mapnik",
                    "mapfile": "/Users/guglielmo/Workspace/open_coesione/GIS/comuni_italia.xml"},
                "projection": "spherical mercator"
            }
        }
    }

    def render_to_response(self, context, **response_kwargs):

        params = context['params']
        layer_name = params['layer_name']
        z = params['z']
        x = params['x']
        y = params['y']
        extension = params['extension']

        mimetype, bytes = self.tiles(layer_name, z, x, y, extension)
        return HttpResponse(bytes, mimetype=mimetype)

    def tiles(self, layer_name, z, x, y, extension):
        """
        Proxy to tilestache
        {X} - coordinate column.
        {Y} - coordinate row.
        {B} - bounding box.
        {Z} - zoom level.
        {S} - host.
        """
        config =  TileStache.Config.buildConfiguration(self.config)
        path_info = "%s/%s/%s/%s.%s" % (layer_name, z, x, y, extension)
        coord, extension = TileStache.splitPathInfo(path_info)[1:]
        return TileStache.getTile(config.layers[layer_name], coord, extension)




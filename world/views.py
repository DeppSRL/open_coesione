import TileStache
from django.http import HttpResponse
from django.views.generic import View, TemplateView

import json
from django import http


class PNGResponseMixin(object):
    def render_to_response(self, context):
        "Returns a PNG response containing 'context' as payload"
        return self.get_png_response(context)

    def get_png_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='image/png',
                                 **httpresponse_kwargs)



class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return http.HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)

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




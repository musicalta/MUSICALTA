from odoo import http
from odoo.http import request
import base64
import os


class SocialMediaImageController(http.Controller):

    @http.route([
        '/social_media_image/fb',
        '/social_media_image/instagram',
        '/social_media_image/linkedin'
        '/social_media_image/logo'
        '/social_media_image/phone_logo'
    ], type='http', auth="public")
    def social_media_image(self, **kwargs):
        image_map = {
            'fb': 'fb.jpg',
            'instagram': 'instagram.png',
            'linkedin': 'linkedin.png',
            'logo': 'logo.jpg',
            'phone_logo': 'phone_logo.jpg',
        }
        # Get the key from the end of the URL
        key = request.httprequest.path.split('/')[-1]
        filename = image_map.get(key)

        if not filename:
            return request.not_found()

        # Determine the full path to the file
        module_path = os.path.join(os.path.dirname(
            __file__), '..', 'static', 'src', 'img')
        file_path = os.path.join(module_path, filename)

        # Check if the file exists
        if not os.path.isfile(file_path):
            return request.not_found()

        with open(file_path, 'rb') as f:
            image_data = f.read()

        return request.make_response(
            image_data,
            [('Content-Type', 'image/png'),  # Assuming all are PNGs, change if not
             ('Content-Disposition', 'inline; filename="{}"'.format(filename))]
        )

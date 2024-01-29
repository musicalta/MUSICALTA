from odoo import http
from odoo.http import request


class SocialMediaImageController(http.Controller):

    @http.route([
        '/social_media_image/fb',
        '/social_media_image/instagram',
        '/social_media_image/linkedin'
    ], type='http', auth="public")
    def social_media_image(self, **kwargs):
        image_map = {
            'fb': 'fb.jpg',
            'instagram': 'instagram.png',
            'linkedin': 'linkedin.png',
        }
        # Get the key from the end of the URL
        key = request.httprequest.path.split('/')[-1]
        filename = image_map.get(key)

        if not filename:
            return request.not_found()

        path = f'musicalta_mail/static/src/img/{filename}'
        # The full path to the file is needed
        full_path = request.module_boot(path)
        if not full_path:
            return request.not_found()

        # Stream the file
        return http.send_file(full_path)

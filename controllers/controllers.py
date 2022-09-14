# -*- coding: utf-8 -*-
# from odoo import http


# class XPaie91322(http.Controller):
#     @http.route('/x_paie_9_13_22/x_paie_9_13_22/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/x_paie_9_13_22/x_paie_9_13_22/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('x_paie_9_13_22.listing', {
#             'root': '/x_paie_9_13_22/x_paie_9_13_22',
#             'objects': http.request.env['x_paie_9_13_22.x_paie_9_13_22'].search([]),
#         })

#     @http.route('/x_paie_9_13_22/x_paie_9_13_22/objects/<model("x_paie_9_13_22.x_paie_9_13_22"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('x_paie_9_13_22.object', {
#             'object': obj
#         })

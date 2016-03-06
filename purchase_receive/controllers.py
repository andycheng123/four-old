# -*- coding: utf-8 -*-
from openerp import http

# class PurchaseReceive(http.Controller):
#     @http.route('/purchase_receive/purchase_receive/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_receive/purchase_receive/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_receive.listing', {
#             'root': '/purchase_receive/purchase_receive',
#             'objects': http.request.env['purchase_receive.purchase_receive'].search([]),
#         })

#     @http.route('/purchase_receive/purchase_receive/objects/<model("purchase_receive.purchase_receive"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_receive.object', {
#             'object': obj
#         })
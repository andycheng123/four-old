# -*- encoding: utf-8 -*-
from openerp import models, api, fields


class sale_order(models.Model):
    _inherit = 'sale.order'

    store_id = fields.Many2one('sale.store', string='Store', default=lambda s: s.env.user.default_store_id, help='')

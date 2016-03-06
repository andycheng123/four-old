# -*- coding:utf-8 -*-
from openerp import models, api, fields


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.model
    def _get_default_store(self):
        return self.env.user.default_store_id

    store_id = fields.Many2one('sale.store', string=u'門店',
                               default=_get_default_store, help='')

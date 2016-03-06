# -*- coding: utf-8 -*-

from openerp import models, fields, api


class product_template(models.Model):
    _inherit = 'product.template'

    store_ids = fields.Many2many('sale.store', related='product_variant_ids.store_ids',
                                   default=lambda s: s.env.user.default_store_id, string='Stores', )

class product_product(models.Model):
    _inherit = 'product.product'

    store_ids = fields.Many2many('sale.store', 'product_store_rel', 'product_id', 'store_id',
                                   default=lambda s: s.env.user.default_store_id, string='Stores', )

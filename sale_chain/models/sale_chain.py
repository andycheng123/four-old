# -*- coding: utf-8 -*-

from openerp import models, api, fields


class sale_store(models.Model):
    _name = 'sale.store'
    _inherits = {'res.partner': 'partner_id'}
    _description = 'Sale Store'

    partner_id = fields.Many2one('res.partner', string='Partner', required='True', ondelete='cascade',)
    user_id = fields.Many2one('res.users', string='Store Leader',)
    member_ids = fields.Many2many('res.users', 'sale_store_member_rel', 'store_id', 'user_id', string='Members', help='')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required='True',)


class res_users(models.Model):
    _inherit = 'res.users'

    default_store_id = fields.Many2one('sale.store', string='Default Store', ondelete='set null',
                                       help='The user default serviced store, it fill some form as default value')

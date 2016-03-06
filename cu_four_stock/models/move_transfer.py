# -*- coding:utf-8 -*-
from openerp import models, api, fields, _

class move_transfer_wizard(models.TransientModel):
    _inherit='move.transfer.wizard'

    #@api.model
    #def default_get(self, field_list):
    #    #res = super(move_transfer_wizard, self).default_get(['location_id'])
    #    res={}
    #    transfer = self.env['move.transfer'].browse(self.env.context['active_id'])
    #    res.update(location_id=transfer.location_id)
    #    #res['location_id'] = transfer.location_id
    #    return res

    @api.model
    def _get_default_location_id(self):
        transfer = self.env['move.transfer'].browse(self.env.context['active_id'])
        return transfer.location_id

    location_id = fields.Many2one('stock.location', string=u'來源倉庫', required='True', default=_get_default_location_id, readonly=True, help='',domain=[('usage','=', 'internal')])
    stock_quant_ids = fields.Many2many(domain="[('qty', '>', 0), ('location_id', '=', location_id)]")
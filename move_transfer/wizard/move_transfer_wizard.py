# -*- coding: utf-8 -*-
'''
Created on 2015年9月29日

@author: michael
'''
from openerp import models, fields, api, _

class move_transfer_wizard(models.TransientModel):
    _name='move.transfer.wizard'


    stock_quant_ids = fields.Many2many('stock.quant','stock_quant_move_transfter_ref','wizard_id','stock_quant_id', string='庫存明細', help='')

    @api.multi
    def action_addline(self):
        mt_obj=self.env["move.transfer"]
        move_id=self.env.context.get("active_id",False)
        if move_id:
           mt = mt_obj.browse(move_id)
           lines= []
           for x in self["stock_quant_ids"]:
               if x.location_id.id == mt.location_id.id:
                  lines.append((0,0,{"lot_id":x.lot_id.id,
                                     "product_id":x.product_id.id,
                                     "product_uom_id":x.product_id.uom_id.id,
                                     "product_qty":x.qty}))
           if lines:
               mt.write({"line_ids":lines})
        return {'type': 'ir.actions.act_window_close'}


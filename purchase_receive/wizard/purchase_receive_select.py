# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv

__author__ = 'kevin'
from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp


class purchase_receive_select(models.TransientModel):
    _name = 'purchase.receive.select'

    partner_id = fields.Many2one('res.partner', string='供应商', help='')
    product_id = fields.Many2one('product.product', string='产品', help='')
    purchase_order_id = fields.Many2one('purchase.order', string='采购订单', help='')
    date_from = fields.Date(string='日期起', help='')
    date_to = fields.Date(string='日期迄', help='')
    line_ids = fields.One2many('purchase.receive.select.line', 'select_id', string='收货明细', help='')

    @api.model
    def default_get(self, field_list):
        res = super(purchase_receive_select, self).default_get(field_list)
        rcv = self.env['purchase.receive'].browse(self.env.context['active_id'])
        res.update(receive_id=rcv.id, partner_id=rcv.partner_id.id)
        return res

    @api.one
    @api.onchange('product_id', 'purchase_order_id', 'date_from', 'date_to')
    def _onchange_data(self):
        wheres = ['m.purchase_line_id=pl.id and pl.order_id=po.id '
                  'and m.receive_line_id is null '
                  'and po.partner_id=%s '
                  'and m.state not in (\'done\', \'cancel\')']
        params = [self.partner_id.id]
        if self.product_id:
            wheres.append('m.product_id = %s')
            params.append(self.product_id.id)
        if self.purchase_order_id:
            wheres.append('pl.order_id = %s')
            params.append(self.purchase_order_id.id)
        if self.date_from:
            wheres.append('date_expected >= %s')
            params.append(self.date_from)
        if self.date_to:
            wheres.append('date_expected <= %s')
            params.append(self.date_to)
        filters = 'and '.join(wheres)
        query = """
        select m.product_id,pl.order_id,min(m.date_expected),sum(m.product_uom_qty)
        from stock_move m, purchase_order_line pl, purchase_order po
        where """ + filters + """
        group by m.product_id, pl.order_id
        order by min(m.date_expected)
        """
        items = []
        self.env.cr.execute(query, params)
        for row in self.env.cr.fetchall():
            items.append({
                'product_id': row[0],
                'purchase_order_id': row[1],
                'date_plan': row[2],
                'unreceive_qty': row[3],
                'select_qty': row[3],
            })
        self.line_ids = items

    @api.multi
    def confirm(self):
        rcv = self.env['purchase.receive'].browse(self.env.context.get('active_id', False))
        if rcv:

            for line in self.line_ids.filtered(lambda x: x.selected and x.select_qty > 0.0):
                exist_line = rcv.line_ids.filtered(lambda x: x.purchase_order_id == line.purchase_order_id and x.product_id == line.product_id)
                if not exist_line:
                    rcv.write({'line_ids': [(0, 0, {
                        'purchase_order_id': line.purchase_order_id.id,
                        'product_id': line.product_id.id,
                        'name': line.product_id.name_get()[0][1],
                        'product_qty': line.select_qty,
                        'sequence': line.sequence,
                    })]})
                else:
                    exist_line.product_qty = line.select_qty


class purchase_receive_select_line(models.TransientModel):
    _name = 'purchase.receive.select.line'

    select_id = fields.Many2one('purchase.receive.select', string='订单选择', help='')
    selected = fields.Boolean(string='选择', help='')
    purchase_order_id = fields.Many2one('purchase.order', string='采购订单', help='')
    product_id = fields.Many2one('product.product', string='产品', help='')
    product_uom_id = fields.Many2one('product.uom', string='单位', related='product_id.uom_id', help='')
    date_plan = fields.Date(string='预定到货日', help='')
    unreceive_qty = fields.Float(string='可收货数量',  help='')
    select_qty = fields.Float(string='本次收货数量', digits_compute=dp.get_precision('Product Unit Of Measure'), help='')

    _order = 'date_plan'

    @api.onchange('select_qty')
    def onchange_select_qty(self):
        if self.select_qty > self.unreceive_qty:
            raise osv.except_osv(_('提示'), _('本次收貨數量 不可超過 可收貨數量!'))



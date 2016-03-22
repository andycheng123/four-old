# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import openerp.addons.decimal_precision as dp


class MoveTransfer(models.Model):
    _name = 'move.transfer'
    _description = '調撥單'

    @api.model
    def _get_default_store_id(self):
        return self.env.user.default_store_id

    @api.model
    def _get_default_src_loc(self):
        return self.env.user.default_store_id.warehouse_id.lot_stock_id

    @api.model
    def _get_today(self):
        return fields.Date.context_today(self)

    name = fields.Char(string=u'單號', default='/', readonly='True', copy=False, help='')
    store_id = fields.Many2one('sale.store', string='開單門店', default=_get_default_store_id, help='')
    location_id = fields.Many2one('stock.location', string=u'來源倉庫', required='True', default=_get_default_src_loc, help='',domain=[('usage','=', 'internal')])
    location_dest_id = fields.Many2one('stock.location', string=u'目的倉庫', required='True', help='',domain=[('usage','=', 'internal')])
    date_move = fields.Date(string='應出貨日期', required='True', default=_get_today, help='')
    date_deliver = fields.Date(string=u'出貨日期', readonly = 'True', help='出貨日期')
    date_receive = fields.Date(string=u'收貨日期', readonly = 'True', help='收貨日期')
    state = fields.Selection([('draft', u'未出貨'), ('delivered', '已出貨'), ('done', u'完成'), ('cancel', u'取消')], string=u'狀態',
                             default='draft', help='調撥單狀態',readonly='True')
    line_ids = fields.One2many('move.transfer.line', 'transfer_id', string=u'調撥單明細', help='')

    _order = 'date_move, id'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env.ref('move_transfer.move_transfer')._next() or '/'
        res = super(MoveTransfer, self).create(vals)

        return res

    @api.one
    def unlink(self):
        if self.state not in ['draft', 'cancel']: raise ValidationError(u'必須先取消該筆調撥單才能刪除！')
        else: super(MoveTransfer, self).unlink()

    @api.one
    def create_stock_move(self):
        for line in self.line_ids:
            move_val = {
                'name': line.product_id.partner_ref,
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id,
                'product_uom_qty': line.product_qty,
                'location_id': self.location_id.id,
                'location_dest_id': self.location_dest_id.id,
            }
            move_id = self.env['stock.move'].create(move_val)
            move_id.action_done()
        return True

    # Deliver product
    @api.multi
    def action_deliver(self):
        for transfer in self:
            if transfer.state == 'draft':
                transfer.create_stock_move()
                transfer.date_deliver = fields.datetime.today()
                transfer.state = 'delivered'
        return True

    # Cancel deliver
    @api.multi
    def action_cancel_deliver(self):
        for transfer in self:
            self.create_return_stock_move()
            transfer.state = 'cancel'
        return True

    # Receive product
    @api.multi
    def action_confirm(self):
        for transfer in self:
            if transfer.state == 'delivered':
                transfer.action_done()
                transfer.date_receive = fields.datetime.today()
        return True

    @api.one
    def action_done(self):
        self.state = 'done'
        return True

    @api.one
    def create_return_stock_move(self):
        for line in self.line_ids:
            move_val = {
                'name': line.product_id.partner_ref,
                'product_id': line.product_id.id,
                'product_uom': line.product_uom_id.id,
                'product_uom_qty': line.product_qty,
                'location_id': self.location_dest_id.id,
                'location_dest_id': self.location_id.id,
            }
            move_id = self.env['stock.move'].create(move_val)
            move_id.action_done()
        return True

    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        return True


class MoveTransferLine(models.Model):
    _name = 'move.transfer.line'
    _description = '調撥單明細'

    sequence = fields.Integer(string='Sequence', default=10, help="Gives the sequence order when displaying a list of sales order lines.")
    transfer_id = fields.Many2one('move.transfer', string='Move Transfer', ondelete='cascade',
                                  required='True', help='')
    product_id = fields.Many2one('product.product', string=u'產品', required='True', help='')
    product_uom_id = fields.Many2one('product.uom', string=u'單位', help='')
    product_qty = fields.Float(string=u'產品數量', digits=dp.get_precision('Product Unit of Measure'), help='')

    _order = 'sequence, id'

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id

    @api.onchange('lot_id')
    def onchange_lot_id(self):
        self.product_id = self.lot_id.product_id
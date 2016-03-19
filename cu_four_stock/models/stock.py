# -*- coding:utf-8 -*-
import base64
from openerp import models, api, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def force_assign(self):
        rtn = super(StockPicking, self).force_assign()
        self.do_transfer()
        return rtn

    @api.cr_uid_ids_context
    def do_enter_transfer_details(self, cr, uid, picking, context=None):
        self.do_transfer(cr, uid, picking, context=context)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(StockMove, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
        if inv_type in ('out_invoice', 'out_refund') and move.procurement_id and move.procurement_id.sale_line_id:
            sale_line = move.procurement_id.sale_line_id
            if move.product_id.id != sale_line.product_id.id:
                res['price_unit'] = move.product_id.list_price_prod
            else:
                res['price_unit'] = sale_line.price_unit

        if inv_type == 'in_invoice' and move.purchase_line_id:
            purchase_line = move.purchase_line_id
            # res['invoice_line_tax_id'] = [(6, 0, [x.id for x in purchase_line.taxes_id])]
            res['price_unit'] = purchase_line.price_unit
        elif inv_type == 'in_refund' and move.origin_returned_move_id.purchase_line_id:
            purchase_line = move.origin_returned_move_id.purchase_line_id
            # res['invoice_line_tax_id'] = [(6, 0, [x.id for x in purchase_line.taxes_id])]
            res['price_unit'] = purchase_line.price_unit
        return res


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.one
    def _compute_date_last_in(self):
        moveObject = self.env['stock.move']
        domain = [('state', '=', 'done'), ('product_id', '=', self.product_id.id),
                  ('location_dest_id', '=', self.location_id.id), ('location_id.usage', '!=', 'inventory')]
        mline = moveObject.search(domain, limit=1, order='date desc')
        if mline:
            self.date_last_in = mline.date
        else:
            self.date_last_in = False

    @api.one
    def _compute_date_last_out(self):
        moveObject = self.env['stock.move']
        domain = [('state', '=', 'done'), ('product_id', '=', self.product_id.id),
                  ('location_id', '=', self.location_id.id),  ('location_dest_id.usage', '!=', 'inventory')]
        mline = moveObject.search(domain, limit=1, order='date desc')
        if mline:
            self.date_last_out = mline.date
        else:
            self.date_last_in = False

    date_last_in = fields.Date(string='最近入庫日', compute='_compute_date_last_in', help='')
    date_last_out = fields.Date(string='最近出庫日', compute='_compute_date_last_out', help='')
    list_price_prod = fields.Float(string='標準售價', related='product_id.list_price_prod', store=True, help='')


class StockTxtExport(models.Model):
    _name = 'stock.txt.export'

    @api.model
    def get_file(self):
        quantObject = self.env['stock.quant']
        domain = [('qty', '>', 0), ('location_id.usage', '=', 'internal'),
                  ('product_id.product_tmpl_id.sale_product_categ_id.code', '=', 'A')]
        quants = quantObject.search(domain)
        with open('stock.txt', 'wb') as f:
            for quant in quants:
                date = quant.in_date[:4] + '/' + quant.in_date[5:7] + '/' + quant.in_date[8:10]
                row = '%s\t%s\t%s\t%d\t%s\r\n' % (
                    quant.product_id.default_code,
                    quant.product_id.name_product,
                    quant.product_id.product_tmpl_id.brand_id.name,
                    quant.product_id.list_price_prod,
                    ('\"' + date + ',' + quant.location_id.name + '\"'))
                f.writelines(row.encode('utf-8'))

        with open('stock.txt', 'rb') as readf:
            readfile = readf.read()
            data = readfile.encode('base64')
        return data

    name = fields.Char(string='FileName', default='stock.txt', help='')
    data = fields.Binary(string='File', default=get_file, help='')



# -*- coding:utf-8 -*-
from openerp import models, api, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def _get_store(self):
        if len(self.order_ids) > 0:
            self.store_id = self.order_ids[0].store_id
        else:
            self.store_id = False

    type_invoice = fields.Selection([('1', u'三聯式'), ('2', u'二聯式')], string=u'發票類型', help='')
    order_ids = fields.Many2many('sale.order', 'sale_order_invoice_rel', 'invoice_id', 'order_id', string='Orders', readonly=True, copy=False, help="Origin orders")
    store_id = fields.Many2one('sale.store', string='門市', compute=_get_store, help='門市')

    _defaults = {
        'type_invoice': '1',
    }


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        rtn = super(AccountInvoiceLine, self).product_id_change(product, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        context = self._context
        company_id = company_id if company_id is not None else context.get('company_id', False)
        self = self.with_context(company_id=company_id, force_company=company_id)

        values = rtn.get('value', {'uos_id': False})
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain': {'uos_id': []}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain': {'uos_id': []}}

        print rtn
        part = self.env['res.partner'].browse(partner_id)

        if part.lang:
            self = self.with_context(lang=part.lang)
        product = self.env['product.product'].browse(product)

        if type in ('in_invoice', 'in_refund'):
            values['price_unit'] = price_unit or product.standard_price_prod
        else:
            values['price_unit'] = product.list_price_prod

        company = self.env['res.company'].browse(company_id)
        currency = self.env['res.currency'].browse(currency_id)

        if company and currency:
            if company.currency_id != currency:
                if type in ('in_invoice', 'in_refund'):
                    values['price_unit'] = product.standard_price_prod
                values['price_unit'] = values['price_unit'] * currency.rate

            if values['uos_id'] and values['uos_id'] != product.uom_id.id:
                values['price_unit'] = self.env['product.uom']._compute_price(
                    product.uom_id.id, values['price_unit'], values['uos_id'])

        rtn['value'] = values
        return rtn

class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    @api.one
    @api.depends('move_ids.reconcile_id')
    def _get_invoice(self):
        for invoice in self.env['account.invoice'].search([('state', '!=', 'draft'), ('journal_id.type', '=', 'sale')]):
            for line in invoice.move_id.line_id:
                for voucher_line in self.move_ids:
                    if (voucher_line.reconcile_id and voucher_line.reconcile_id == line.reconcile_id) or (voucher_line.reconcile_partial_id and voucher_line.reconcile_partial_id == line.reconcile_partial_id):
                        self.invoice = invoice
                        self.store_id = invoice.store_id
                        return True

    @api.model
    def set_store(self, cr, uid, context=None):
        for voucher in self.env['account.voucher'].search([]):
            voucher.store_id = voucher.invoice.store_id
        return True

    invoice = fields.Many2one('account.invoice', compute='_get_invoice', string='對應發票', help='對應之發票')
    store_id = fields.Many2one('sale.store', compute='_get_invoice', string='門市', store=True, help='門市')
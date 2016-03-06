# -*- coding:utf-8 -*-
from itertools import groupby
from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from openerp import SUPERUSER_ID
from openerp.osv import osv


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_default_store(self):
        return self.env.user.default_store_id

    store_id = fields.Many2one('sale.store', string='門市', default=_get_default_store, help='')
    sale_invoices = fields.One2many('sale.order.invoice', 'saleorder_id', string=u'發票明細', help='')
    #receive_ids = fields.One2many('sale.order.receive', 'saleorder_id', string=u'收款明細', help='')
    receive_ids = fields.Many2many(related='invoice_ids.payment_ids', string='收款明細', help='收款明細')
    tax_ids = fields.Many2many('account.tax', 'sale_order_tax_rel', 'sale_order_id', 'tax_id', string=u'税别', help='')
    balance = fields.Float(related='invoice_ids.residual', digits=dp.get_precision('Account'), string="未收款", help='應收款項餘額')
    date_order = fields.Datetime('開單日期', required=True, readonly=True, select=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False)

    @api.model
    def default_get(self, field_list):
        res = super(SaleOrder, self).default_get(field_list)
        acc_conf = self.env['account.config.settings'].search([], limit=1, order='write_date desc')
        if acc_conf.default_sale_tax.id:
            res.update(tax_ids=[(6, 0, [acc_conf.default_sale_tax.id])])
        else:
            res.update(tax_ids=[(6, 0, [5])])
        return res

    @api.one
    @api.onchange("store_id")
    def _onchange_store_id(self):
        if self.store_id:
            self.warehouse_id = self.store_id.warehouse_id.id

    @api.onchange("partner_id")
    def onchange_order_partner_id(self):
        product_obj = self.env['product.product']
        if self.partner_id:
            fpos = False
            if not self.fiscal_position:
                fpos = self.partner.property_account_position or False
            else:
                fpos = self.fiscal_position
            # The superuser is used by website_sale in order to create a sale order. We need to make
            # sure we only select the taxes related to the company of the partner. This should only
            # apply if the partner is linked to a company.
            if self.uid == SUPERUSER_ID and self.env.company_id:
                taxes = product_obj.taxes_id.filtered(lambda r: r.company_id.id == self.env.company_id.id)
            else:
                taxes = product_obj.taxes_id
            self.tax_ids = self.env['account.fiscal.position'].map_tax(fpos, taxes)

    @api.onchange('tax_ids')
    def onchange_tax_ids(self):
        for line in self.order_line:
            line.tax_id = self.tax_ids

    @api.multi
    def action_quotation_send(self):
        self.state = 'sent'

    # Automatically create invoice after order confirmed
    @api.multi
    def action_button_confirm(self):
        rtn = super(SaleOrder, self).action_button_confirm()
        for order in self:
            order.action_invoice_create()
            order.invoice_ids.action_date_assign()
            order.invoice_ids.action_move_create()
            order.invoice_ids.action_number()
            order.invoice_ids.invoice_validate()
    #        amount_rec = sum(line.amount for line in order.receive_ids)
    #        if amount_rec < order.amount_total:
    #            raise osv.except_osv(_(u'收款不足'), _((u'收款金额不足 %s') % order.amount_total))
        return rtn
        
    # Register payment
    @api.one
    def action_pay(self):
        #raise osv.except_osv(_('action_pay'), _('action_pay'))
        uid = self._uid
        for invoice in self.invoice_ids:
            cr = invoice._cr
            context = invoice._context
            dummy, view_id = invoice.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')
            inv = invoice
            return {
                'name':_("Pay Invoice"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'account.voucher',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': {
                    'payment_expected_currency': inv.currency_id.id,
                    'default_partner_id': invoice.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                    'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                    'default_reference': inv.name,
                    'close_after_process': True,
                    'invoice_type': inv.type,
                    'invoice_id': inv.id,
                    'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                    'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
                }
            }

    @api.multi
    def action_invoice_confirm(self):
        for order in self:
            order.create_account_for_journal(order.store_id, order.date_order, order.tax_ids)
        self.state = 'done'

    @api.model
    def create_account_for_journal(self, store_id, date, tax_ids):

        journal_saj_id = self.env['account.journal'].search([('code', '=', 'SAJ')], limit=1)
        tax_account = tax_ids.account_collected_id
        sale_amount_total = 0
        tax_amount = 0

        cur = self.env.user.company_id.currency_id
        account_move_lines = []

        for journal, lines in groupby(self.receive_ids.sorted(lambda x: x.journal_id), lambda x: x.journal_id):
            account_id = journal.default_debit_account_id
            amount_sell = sum(ln.amount for ln in lines)

            sale_amount = amount_sell / (1 + tax_ids.amount)
            sale_amount_total += sale_amount
            tax_amount += amount_sell - sale_amount
            print sale_amount, tax_amount, tax_ids.amount

            account_move_lines.append((0, 0, {
                'debit': ((amount_sell > 0) and amount_sell) or 0.0,
                'credit': 0.0,
                'name': store_id.name,
                'account_id': account_id.id,
                'partner_id': self.partner_id.id}))

        if self.amount_tax:
            amount_diff = self.amount_tax - tax_amount != 0
            if amount_diff != 0:
                tax_amount += amount_diff
                sale_amount_total -= amount_diff

        if tax_amount:
            account_move_lines.append((0, 0, {
                'debit': 0.0,
                'credit': ((tax_amount > 0) and tax_amount) or 0.0,
                'name': tax_ids.name,
                'account_id': tax_account.id,
                'tax_amount': ((tax_amount > 0) and tax_amount) or 0.0,
                'partner_id': self.partner_id.id}))

        account_move_lines.append((0, 0, {
            'debit': 0.0,
            'credit': ((sale_amount_total > 0) and sale_amount_total) or 0.0,
            'name': store_id.name,
            'account_id': journal_saj_id.default_debit_account_id.id,
            'partner_id': self.partner_id.id}))

        self.action_create_account_move(account_move_lines, journal_saj_id, store_id, date)

        return True

    @api.model
    def action_create_account_move(self, lines, journal_id, store_id, date):
        move_obj = self.env['account.move']
        period = self.env['account.period'].find(date)[0]
        move_val = {
            'journal_id': journal_id.id,
            'period_id': period and period.id or False,
            'company_id': self.env.user.company_id.id,
            'date': date,
            'ref': 'A' + store_id.name,
            'period_id': period.id,
            'line_id': lines,
        }
        move_id = move_obj.create(move_val)
        return move_id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.one
    def _compute_gross_profit(self):
        self.line_cost = self.product_uom_qty * self.product_id.standard_price
        self.gross_profit = self.price_subtotal - self.line_cost
        self.gross_profit_rate = self.price_subtotal and self.gross_profit / self.price_subtotal * 100 or 0

    recipe_id = fields.Many2one('sale.recipe', string=u'處方單', help='')
    line_cost = fields.Float(string=u'成本', compute='_compute_gross_profit', digits=(16, 0), help='')
    gross_profit = fields.Float(string=u'毛利', compute='_compute_gross_profit', digits=(16, 0), help='')
    gross_profit_rate = fields.Float(string=u'毛利率%', compute='_compute_gross_profit', digits=(16, 0), help='')
    brand_id = fields.Many2one(related='product_id.brand_id', store=True, string=u'品牌', help='')
    sale_product_categ_id = fields.Many2one('sale.product.category', string=u'品類',
                                            related='product_id.sale_product_categ_id', store=True, help='')
    product_model = fields.Many2one(string=u'產品型號', related='product_id.product_tmpl_id.sale_product_model_id', store=True, help='')
    product_specs = fields.Many2one(string=u'品规', related='product_id.product_specs_id', help='')
    date_order = fields.Datetime(string=u'訂單日期', related='order_id.date_order', store=True, help='')
    user_id = fields.Many2one('res.users', string=u'承建人', related='order_id.user_id', help='')
    partner_id = fields.Many2one('res.partner', string=u'客戶', related='order_id.partner_id', help='')
    store_id = fields.Many2one('sale.store', related='order_id.store_id', store=True, string=u'門店', help='')
    note = fields.Text(string=u'備註', help='')

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        rtn = super(SaleOrderLine, self).product_id_change(cr, uid, ids, pricelist, product, qty, uom, qty_uos, uos,
                                                           name, partner_id, lang, update_tax, date_order,  packaging,
                                                           fiscal_position, flag, context=context)
        product_obj = self.pool.get('product.product')
        context_partner = context.copy()
        context_partner.update({'lang': lang, 'partner_id': partner_id})
        product = product_obj.browse(cr, uid, product, context=context_partner)
        partner_obj = self.pool.get('res.partner')
        partner = partner_obj.browse(cr, uid, partner_id)
        fpos = False
        if not fiscal_position:
            fpos = partner.property_account_position or False
        else:
            fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)
        if update_tax: #The quantity only have changed
            # The superuser is used by website_sale in order to create a sale order. We need to make
            # sure we only select the taxes related to the company of the partner. This should only
            # apply if the partner is linked to a company.
            if uid == SUPERUSER_ID and context.get('company_id'):
                taxes = product.taxes_id.filtered(lambda r: r.company_id.id == context['company_id'])
            else:
                taxes = product.taxes_id
            rtn['value']['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, taxes)

        price = product.list_price_prod
        if update_tax:
            price = self.pool['account.tax']._fix_tax_included_price(cr, uid, price, product.taxes_id, rtn['value']['tax_id'])
        rtn['value'].update({'price_unit': price})

        return rtn


class SaleOrderInvoice(models.Model):
    _name = 'sale.order.invoice'
    _description = u'銷售發票'

    name = fields.Char(string=u'發票號碼', help='')
    type_invoice = fields.Selection([('1', u'三聯式'), ('2', u'二聯式')], string=u'發票類型', help='')
    partner_id = fields.Many2one('res.partner', string=u'客戶', help='')
    name_title = fields.Char(string=u'抬頭', help='')
    saleorder_id = fields.Many2one('sale.order', string=u'銷貨單', help='')
    code_uniform = fields.Char(string=u'統一編號', help='')
    amount = fields.Float(string=u'金額', digits=dp.get_precision('Account'), help='')
    amount_tax = fields.Float(string=u'稅額', digits=dp.get_precision('Account'), help='')
    amount_total = fields.Float(string=u'含稅金額', digits=dp.get_precision('Account'), help='')
    note = fields.Text(string=u'備註', help='')
    invoice_lines = fields.One2many('sale.order.invoice.line', 'invoice_id', string=u'發票', help='')

    @api.onchange('saleorder_id')
    def _onchange_saleorder_id(self):
        if self.saleorder_id:
            self.partner_id = self.saleorder_id.partner_id
            self.name_title = self.saleorder_id.partner_id.invoice_name
            self.code_uniform = self.saleorder_id.partner_id.name_company
        return True

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.name_title = self.partner_id.invoice_name
        self.code_uniform = self.partner_id.name_company

    @api.onchange('amount')
    def _onchange_amount(self):
        self.amount_tax = self.saleorder_id.amount_tax
        self.amount_total = self.amount_tax + self.amount

    @api.onchange('amount_tax')
    def _onchange_amount_tax(self):
        self.amount_total = self.amount + self.amount_tax


class saleorderinvoiceline(models.Model):
    _name = 'sale.order.invoice.line'
    _description = u'發票明細'

    invoice_id = fields.Many2one('sale.order.invoice', string=u'發票', help='')
    name_product = fields.Char(string=u'品名', help='')
    quantity = fields.Float(string=u'數量', digits=dp.get_precision('Account'), help='')
    price = fields.Float(string=u'單價', digits=dp.get_precision('Account'), help='')
    amount = fields.Float(string=u'金額', digits=dp.get_precision('Account'), help='')
    note = fields.Text(string=u'備註', help='')

    @api.onchange('quantity')
    def _onchange_quantity(self):
        self.amount = self.price * self.quantity

    @api.onchange('price')
    def _onchange_price(self):
        self.amount = self.quantity * self.price


class saleorderreceive(models.Model):
    _name = 'sale.order.receive'
    _description = u'收款明細'

    date_receive = fields.Date(string=u'收款日期', default=fields.date.today(), help='')
    amount = fields.Float(string=u'金額', digits=dp.get_precision('Account'), help='')
    journal_id = fields.Many2one('account.journal', string=u'收款方式', required='True', help='')
    count_period = fields.Float(string=u'刷卡期數', digits=dp.get_precision('Account'), help='')
    note = fields.Text(string=u'備註', help='')
    saleorder_id = fields.Many2one('sale.order', string=u'銷貨單', help='')
    store_id = fields.Many2one('sale.store', related='saleorder_id.store_id', store=True,
                               string=u'門店', help='')

# -*- coding:utf-8 -*-
import datetime
from openerp import models, api, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_default_store(self):
        return self.env.user.default_store_id

    store_id = fields.Many2one('sale.store', string=u'門市', default=_get_default_store, help='')
    tax_ids = fields.Many2many('account.tax', 'purchase_order_tax_rel', 'purchase_order_id', 'tax_id',
                               string=u'税别', help='')
    specs_flag = fields.Boolean(string=u'產品品規', default=False, help='')
    user_id = fields.Many2one('res.users', string=u'採購人員', default=lambda x: x.env.uid, help='')

    _defaults = {
        'invoice_method': 'picking',
    }

    @api.model
    def default_get(self, field_list):
        res = super(PurchaseOrder, self).default_get(field_list)
        acc_conf = self.env['account.config.settings'].search([], limit=1, order='write_date desc')
        if acc_conf.default_purchase_tax.id:
            res.update(tax_ids=[(6, 0, [acc_conf.default_purchase_tax.id])])
        else:
            res.update(tax_ids=[(6, 0, [4])])
        return res

    @api.onchange('tax_ids')
    def onchange_tax_ids(self):
        for line in self.order_line:
            line.taxes_id = self.tax_ids

    @api.multi
    def action_cancel(self):
        for order in self:
            for line in order.order_line:
                for move in line.move_ids:
                    move.action_cancel()
                    move.unlink()
            super(PurchaseOrder, order).action_cancel()

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    store_id = fields.Many2one('sale.store', related='order_id.store_id', string=u'門店', help='')
    product_tmpl_id = fields.Many2one('product.template', string=u'產品', help='')
    product_specs_id = fields.Many2one('sale.product.specs', string=u'品规', help='')
    date_order = fields.Datetime(string=u'訂單日期', related='order_id.date_order', store=True, help='')
    note = fields.Text(string=u'備註', help='')

    @api.model
    def create(self, vals):
        if 'product_tmpl_id' in vals:
            if vals['product_tmpl_id']:
                product_val = vals
                product_obj = self.env['product.product']
                product_tmpl = self.env['product.template'].browse(product_val['product_tmpl_id'])
                product_specs = self.env['sale.product.specs'].browse(product_val['product_specs_id'])
                default_code = product_tmpl.name + (product_specs and product_specs.name or '')
                domain = [('active', '=', False), ('default_code', '=', default_code),
                          ('product_tmpl_id', '=', product_val['product_tmpl_id']),
                          ('product_specs_id', '=', product_val['product_specs_id'])]
                product_id = product_obj.with_context(active_test=False).search(domain, limit=1)
                if not product_id:
                    product_id = product_obj.create({
                        'name': product_tmpl.name,
                        'product_tmpl_id': product_tmpl.id,
                        'product_specs_id': product_val['product_specs_id'],
                        'default_code': default_code,
                        'standard_price_prod': product_val['price_unit'] or product_tmpl.standard_price,
                        'active': False
                    })
                product_val['product_id'] = product_id.id
                vals.update(product_val)

        res = super(PurchaseOrderLine, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        product_obj = self.env['product.product']
        if set(('product_tmpl_id', 'product_specs_id')).intersection(set(vals.keys())):
            for line in self:
                tmpl_id = vals['product_tmpl_id'] if 'product_tmpl_id' in vals else line.product_tmpl_id.id
                product_specs_id = vals['product_specs_id'] if 'product_specs_id' in vals else line.product_sepcs_id.id
                domain = [('active', '=', False), ('product_tmpl_id', '=', tmpl_id), ('product_specs_id', '=', product_specs_id)]
                product_id = product_obj.search(domain, limit=1)
                standard_price_prod = vals['price_unit'] if 'price_unit' in vals else line.price_unit
                product_tmpl = self.env['product.template'].browse(tmpl_id)
                product_specs = self.env['sale.product.specs'].browse(product_specs_id)
                if not product_id:
                    product_id = product_obj.create({
                        'name': product_tmpl.name,
                        'product_tmpl_id': tmpl_id,
                        'product_specs_id': product_specs_id,
                        'default_code': product_tmpl.name + (product_specs and product_specs.name or ''),
                        'standard_price_prod': standard_price_prod,
                        'active': False,

                    })
                else:
                    product_id.standard_price_prod = standard_price_prod
                vals['product_id'] = product_id.id
                vals['name'] = product_tmpl.name + (product_specs and product_specs.name or ''),
                vals['date_planned'] = datetime.datetime.today()
        return super(PurchaseOrderLine, self).write(vals)

    @api.onchange('product_tmpl_id', 'product_specs_id')
    def onchange_product_tmpl_id(self):
        if not self.product_tmpl_id:
            return
        product_obj = self.env['product.product']
        domain = []
        self.name = self.product_tmpl_id.name
        self.date_planned = datetime.datetime.today()
        self.taxes_id = self.order_id.tax_ids

        if self.product_tmpl_id or self.product_specs_id:
            self.name = self.product_tmpl_id.name
            domain.append(('active', '=', False))
            domain.append(('product_tmpl_id', '=', self.product_tmpl_id.id))
            domain.append(('product_specs_id', '=', self.product_specs_id.id))
            product_id = product_obj.with_context(active_test=False).search(domain, limit=1)
            self.price_unit = product_id.standard_price_prod or self.product_tmpl_id.standard_price

        if self.product_tmpl_id.description_purchase:
            self.name += self.product_tmpl_id.description_purchase

    def onchange_product_id(self, cr, uid, ids, pricelist_id, product_id, qty, uom_id, partner_id, date_order=False,
                            fiscal_position_id=False, date_planned=False, name=False, price_unit=False, state='draft',
                            context=None):
        rtn = super(PurchaseOrderLine, self).onchange_product_id(cr, uid, ids, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=date_order, fiscal_position_id=fiscal_position_id, date_planned=date_planned,
            name=name, price_unit=price_unit, state=state, context=context)
        """
        onchange handler of product_id.
        """
        if context is None:
            context = {}

        product_product = self.pool.get('product.product')
        res_partner = self.pool.get('res.partner')
        account_fiscal_position = self.pool.get('account.fiscal.position')
        account_tax = self.pool.get('account.tax')

        context_partner = context.copy()
        if partner_id:
            lang = res_partner.browse(cr, uid, partner_id).lang
            context_partner.update( {'lang': lang, 'partner_id': partner_id} )
        product = product_product.browse(cr, uid, product_id, context=context_partner)

        price = price_unit
        if price_unit is False or price_unit is None:
            price = product.standard_price_prod

        taxes = account_tax.browse(cr, uid, map(lambda x: x.id, product.supplier_taxes_id))
        fpos = fiscal_position_id and account_fiscal_position.browse(cr, uid, fiscal_position_id, context=context) or False
        taxes_ids = account_fiscal_position.map_tax(cr, uid, fpos, taxes)
        price = self.pool['account.tax']._fix_tax_included_price(cr, uid, price, product.supplier_taxes_id, taxes_ids)
        rtn['value'].update({'price_unit': price})

        return rtn


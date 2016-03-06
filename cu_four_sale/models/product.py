# -*- coding: utf-8 -*-
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sale_product_categ_id = fields.Many2one('sale.product.category', related='sale_product_model_id.sale_product_categ_id', readonly=True, store=True, string=u'品類', help='')
    brand_id = fields.Many2one('product.brand', related='sale_product_model_id.brand_id', readonly=True, store=True, string=u'品牌', help='')
    sale_product_model_id = fields.Many2one('sale.product.model', string=u'型号', help='')
    spec_ids = fields.One2many('sale.product.specs', 'product_tmpl_id', string=u'品規', help='')

    _defaults = {
        'name': '/',
        'type': 'product',
    }

    _order = 'name'

    @api.multi
    def create_variant_ids(self):
        pass

    @api.onchange('spec_ids')
    def _onchange_default_code(self):
        self.default_code = self.name

    @api.onchange('brand_id', 'sale_product_categ_id', 'sale_product_model_id')
    def _onchange_name(self):
        self.name = self.sale_product_categ_id and self.sale_product_categ_id.code or ''
        if self.name:
            self.name += self.brand_id and ('-' + self.brand_id.code) or ''
        else:
            self.name += self.brand_id and self.brand_id.code or ''

        if self.name:
            self.name += self.sale_product_model_id.name and ('-' + self.sale_product_model_id.name) or ''
        else:
            self.name += self.sale_product_model_id.name or ''

        if not self.default_code:
            self.default_code = self.name

    #def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
    #    if not args:
    #        args=[]
    #    return super(ProductTemplate, self).name_search(cr, user, name, args=args, operator=operator, context=context,limit=limit)

    # By Aaron
    def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=100):
        if not args: args = []
        ids = []
        if name: ids = self.search(cr, user, [('name', 'ilike', name)] + args, limit=limit)
        if not ids:
            return super(ProductTemplate, self).name_search(cr, user, name, args=args, operator=operator, context=context,limit=limit)
        return self.name_get(cr, user, ids, context=context)



class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.multi
    def name_get(self):
        res = []
        for x in self:
            name = x.name_template
            if x.default_code:
                name = '[%s] %s' % (x.default_code, x.name_template)
            if x.product_specs_id and x.product_specs_id.name:
                name += '-' + x.product_specs_id.name

            res.append((x.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        if args is None:
            args=[]
        if context is None:
            context={}
        ids = []
        if name:
            ids = self.search(cr, uid, ['|', ('name_product', 'ilike', name), ('name_code_product', 'ilike', name)]+ args, limit=limit)
            if not ids:
                return super(ProductProduct, self).name_search(cr, uid, name, args, operator, context=context, limit=80)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    @api.one
    def _compute_date_last_sale(self):
        saleOrderLine = self.env['sale.order.line']
        domain = [('state', 'in', ['done', 'confirmed']), ('product_id', '=', self.id)]
        sline = saleOrderLine.search(domain, limit=1, order='date_order desc')
        self.date_last_sale = sline.date_order


    @api.one
    def _compute_date_last_purchase(self):
        purchaseOrderLine = self.env['purchase.order.line']
        domain = [('state', '=', 'done'), ('product_id', '=', self.id)]
        pline = purchaseOrderLine.search(domain, limit=1, order='date_order desc')
        self.date_last_purchase = pline.date_order

    @api.one
    def _compute_date_last_move(self):
        move_line = self.env['stock.move']
        domain = [('state', '=', 'done'), ('product_id', '=', self.id)]
        mline = move_line.search(domain, limit=1, order='date desc')
        self.date_last_move = mline.date

    name_code_product = fields.Char(string=u'產品', help='')
    name_product = fields.Char(string=u'品名', help='')
    product_specs_id = fields.Many2one('sale.product.specs', string=u'品規', help='')
    brand_id = fields.Many2one('product.brand', string=u'品牌', help='')
    ean8 = fields.Char(string='EAN8', help='')
    list_price_prod = fields.Float(string=u'標準售價', digits=dp.get_precision('Product Price'), help='')
    standard_price_prod = fields.Float(string=u'成本', digits=dp.get_precision('Product Price'), help='')
    partner_prod_id = fields.Many2one('res.partner', related="product_tmpl_id.brand_id.partner_id",
                                      readonly="True", string=u'供應商', help='')
    note = fields.Char(string='note', help='')
    description = fields.Text(string='Description', translate=True,
                              help='A precise description of the Product, used only for internal information purposes.')
    date_last_sale = fields.Date(string=u'最近銷貨日', compute='_compute_date_last_sale', help='')
    date_last_purchase = fields.Date(string=u'最近進貨日', compute='_compute_date_last_purchase', help='')
    date_last_move = fields.Date(string=u'最後異動日', compute='_compute_date_last_move', help='')

    _order = "product_tmpl_id, product_specs_id"

    @api.onchange('product_tmpl_id', 'product_specs_id')
    def onchange_name(self):
        if self.product_tmpl_id:
            self.brand_id = self.product_tmpl_id.brand_id

        self.name_product = self.product_tmpl_id and self.product_tmpl_id.name or ''
        if self.name:
            self.name_product += self.product_specs_id and ('-' + self.product_specs_id.name) or ''
        else:
            self.name_product += self.product_specs_id.name or ''

    @api.onchange('name_product', 'default_code')
    def onchange_name_product(self):
        self.name_code_product = '[' + (self.default_code or '') + ']' + (self.name_product or '')


class SaleProductCategory(models.Model):
    _name = 'sale.product.category'
    _description = u'品類'

    code = fields.Char(string=u'編號', required='True', help='')
    name = fields.Char(string=u'名稱', required='True', help='')
    note = fields.Text(string=u'說明', help='')

    @api.multi
    def name_get(self):
        res = []
        for x in self:
            name = "[%s]%s" % (x.code, x.name)
            res.append((x.id, name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args=[]
        if not context:
            context={}
        ids = []
        if name:
            ids = self.search(cr, uid, [('code','ilike',name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('name',operator,name)]+ args, limit=limit)
        return self.name_get(cr, uid, ids, context=context)


class SaleProductModel(models.Model):
    _name = 'sale.product.model'
    _description = u'型号'

    code = fields.Char(string=u'編號', required='True', help='')
    name = fields.Char(string=u'名稱', required='True', help='')
    sale_product_categ_id = fields.Many2one('sale.product.category', string=u'品類', help='')
    brand_id = fields.Many2one('product.brand', string=u'品牌', help='')

    note = fields.Text(string=u'說明', help='')

    _order = "sale_product_categ_id, brand_id,code"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args=[]
        if not context:
            context={}
        ids = []
        if name:
            ids = self.search(cr, uid, [('code','ilike',name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('name',operator,name)]+ args, limit=limit)
        return self.name_get(cr, uid, ids, context=context)


class SaleProductSpecs(models.Model):
    _name = 'sale.product.specs'
    _description = u'品規'

    code = fields.Char(string=u'編號', required='True', help='')
    name = fields.Char(string=u'名稱', required='True', help='')
    product_tmpl_id = fields.Many2one('product.template', required='True', string=u'產品款式', help='')
    note = fields.Text(string=u'說明', help='')

    _order = "product_tmpl_id, code"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=80):
        if not args:
            args=[]
        if not context:
            context={}
        ids = []
        if name:
            ids = self.search(cr, uid, ['|', ('code','ilike',name),('name','ilike',name)]+ args, limit=limit)
        if not ids:
            ids = self.search(cr, uid, [('name',operator,name)]+ args, limit=limit)
        return self.name_get(cr, uid, ids, context=context)


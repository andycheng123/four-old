# -*- coding:utf-8 -*-
from openerp import models, api, fields
import openerp.addons.decimal_precision as dp


class TempIm(models.Model):
    _name = 'temp.im'

    product_id = fields.Char(string=u'产品id', help='')
    name = fields.Char(string=u'品名', help='')
    default_code = fields.Char(string=u'內部編號', help='')
    ean8 = fields.Char(string='ean8', help='')
    product_tmpl_id = fields.Many2one('product.template', string=u'產品款式', help='')
    product_tmpl_name = fields.Char(string=u'款式名稱', help='')
    categ_name = fields.Char(string=u'品類', help='')
    categ_id = fields.Many2one('sale.product.category', string=u'品類', help='')
    brand_name = fields.Char(string=u'品牌', help='')
    brand_id = fields.Many2one('product.brand', string=u'品牌', help='')
    product_model = fields.Char(string=u'型號', help='')
    product_model_id = fields.Many2one('sale.product.model', string=u'型號', help='')
    product_specs = fields.Char(string=u'品規', help='')
    product_specs_id = fields.Many2one('sale.product.specs', string=u'品規', help='')
    lst_price = fields.Float(string=u'售價', digits=dp.get_precision('Product Price'), help='')
    standard_price = fields.Float(string=u'成本價', digits=dp.get_precision('Product Price'), help='')
    supplier_name = fields.Char(string=u'供应商名称', help='')
    supplier_id = fields.Many2one('res.partner', string=u'供应商名称', help='')
    update_flag = fields.Text(string='update flag', help='')
    old_it_id = fields.Integer(string='old it id', help='')
    old_im_id = fields.Integer(string='old im id', help='')
    temp_default_code = fields.Char(string=u'temp內部編號', help='')


class TempImCode(models.Model):
    _name = 'temp.im.code'

    name = fields.Char(string=u'品名', help='')
    default_code = fields.Char(string=u'內部編號', help='')
    ean8 = fields.Char(string='ean8', help='')
    product_tmpl_name = fields.Char(string=u'款式名稱', help='')
    product_model = fields.Char(string=u'產品型號', help='')
    product_specs = fields.Char(string=u'品規', help='')


class TempIt(models.Model):
    _name = 'temp.it'

    name = fields.Char(string=u'款式名稱', help='')
    sale_product_categ_id = fields.Many2one('sale.product.category', string=u'品類', help='')
    categ_name = fields.Char(string=u'品類名稱', help='')
    brand_id = fields.Many2one('product.brand', string=u'品牌', help='')
    brand_name = fields.Char(string=u'品牌名稱', help='')
    product_model = fields.Char(string=u'產品型號', help='')
    update_flag = fields.Text(string='update_flag', help='')
    old_it_id = fields.Integer(string='old it id', help='')


class TempBrand(models.Model):
    _name = 'temp.brand'

    code = fields.Char(string=u'編號', help='')
    name = fields.Char(string=u'名稱', help='')
    update_flag = fields.Text(string='update_flag', help='')
    old_brand_id = fields.Integer(string='old brand id')
    partner_id = fields.Many2one('res.partner', string=u'供應商', help='')
    partner_name = fields.Char(string=u'供應商名稱', help='')


class TempEan8(models.Model):
    _name = 'temp.ean8'

    default_code = fields.Char(string=u'內部編號', help='')
    ean8 = fields.Char(string=u'ean8', help='')



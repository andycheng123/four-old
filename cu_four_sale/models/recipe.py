# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.osv import osv
import openerp.addons.decimal_precision as dp


class SaleRecipe(models.Model):
    _name = 'sale.recipe'

    @api.model
    def _get_default_company(self):
        company_id = self.env['res.users']._get_company()
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the  current user!'))
        return company_id

    @api.model
    def _get_default_store(self):
        return self.env.user.default_store_id

    name = fields.Char(string='Number', defalut='/', copy=False, readonly='True', help='')
    date_recipe = fields.Date(string='Date Recipe', default=fields.Date.today, help='')
    partner_id = fields.Many2one('res.partner', string='Partner', required='True', help='')
    user_id = fields.Many2one('res.users', string='User', default=lambda s: s.env.uid, help='')
    company_id = fields.Many2one('res.company', string='company', default=_get_default_company, help='')
    note = fields.Text(string=u'備註', help='備註')
    frame = fields.Char(string='Frame', help='')
    glasses = fields.Char(string='Glasses', help='')
    category_id = fields.Many2one('sale.recipe.category', string=u'種類', help='')
    period = fields.Char(string='Period', size=10, help='')
    optometry_id = fields.Many2one('sale.optometry', string='Optometry', help='')
    dist_sph_r = fields.Char(string='Distance SPH R', help='')
    dist_cyl_r = fields.Char(string='Distance SPH R', help='')
    dist_ax_r = fields.Char(string='Distance AX R', help='')
    read_add_r = fields.Char(string='Reading ADD R', help='')
    prism_vector_r = fields.Char(string='Prism Vector R', help='')
    prism_angle_r = fields.Char(string='Prism Angle R', help='')
    vision_r = fields.Char(string='VA R', help='')
    pd_r = fields.Char(string='PD R', help='')
    radian_r = fields.Char(string='Radian R', help='')
    dist_sph_l = fields.Char(string='Distance SPH L', help='')
    dist_cyl_l = fields.Char(string='Distance SPH L', help='')
    dist_ax_l = fields.Char(string='Distance AX L', help='')
    read_add_l = fields.Char(string='Reading ADD L', help='')
    prism_vector_l = fields.Char(string='Prism Vector L', help='')
    prism_angle_l = fields.Char(string='Prism Angle L', help='')
    vision_l = fields.Char(string='VA L', help='')
    pd_l = fields.Char(string='PD L', help='')
    radian_l = fields.Char(string='Radian L', help='')
    eye_position_r = fields.Char(string='Eye Position R', help='')
    eye_position_l = fields.Char(string='Eye Position L', help='')
    eye_benefit_r = fields.Char(string=u'利眼 R', help='')
    eye_benefit_l = fields.Char(string=u'利眼 L', help='')

    extend_A = fields.Char(string='A', help='')
    extend_B = fields.Char(string='B', help='')
    extend_DBL = fields.Char(string='DBL', help='')
    extend_Panto = fields.Char(string='Panto', help='')
    extend_Bawangle = fields.Char(string='Bawangle', help='')
    extend_BVD = fields.Char(string='BVD', help='')
    extend_RD = fields.Char(string='RD', help='')
    extend_FF = fields.Char(string='FF', help='')
    store_id = fields.Many2one('sale.store', string=u'門店', default=_get_default_store, help='')

    _order = 'date_recipe desc, id'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env.ref('cu_four_sale.sale_recipe')._next() or '/'
        res = super(SaleRecipe, self).create(vals)

        return res

    @api.onchange('optometry_id')
    def onchange_optometry_id(self):
        if not self.partner_id:
            self.partner_id = self.optometry_id.partner_id
        self.dist_sph_r = self.optometry_id.dist_sph_r
        self.dist_cyl_r = self.optometry_id.dist_cyl_r
        self.dist_ax_r = self.optometry_id.dist_ax_r
        self.read_add_r = self.optometry_id.read_add_r
        self.prism_vector_r = self.optometry_id.prism_vector_r
        self.prism_angle_r = self.optometry_id.prism_angle_r
        self.vision_r = self.optometry_id.vision_r
        self.pd_r = self.optometry_id.pd_r
        self.radian_r = self.optometry_id.radian_r
        self.dist_sph_l = self.optometry_id.dist_sph_l
        self.dist_cyl_l = self.optometry_id.dist_cyl_l
        self.dist_ax_l = self.optometry_id.dist_ax_l
        self.read_add_l = self.optometry_id.read_add_l
        self.prism_vector_l = self.optometry_id.prism_vector_l
        self.prism_angle_l = self.optometry_id.prism_angle_l
        self.vision_l = self.optometry_id.vision_l
        self.pd_l = self.optometry_id.pd_l
        self.radian_l = self.optometry_id.radian_l


class RecipeCategory(models.Model):
    _name = 'sale.recipe.category'
    _description = 'Sale Recipe Category'

    code = fields.Char(string=u'編號', required='True', help='')
    name = fields.Char(string=u'名稱', required='True', help='')
    note = fields.Text(string=u'說明', help='')

    _sql_constraints = [('name_uniq', 'unique(code)', 'The Code of the Category must be unique!')]



# -*- coding:utf-8 -*-
from openerp import models, api, fields, _
import openerp.addons.decimal_precision as dp
from openerp.osv import osv


class SaleOptometry(models.Model):
    _name = 'sale.optometry'
    _description = 'glasses optometry order'
    _order = 'date_order desc'

    @api.model
    def _get_default_company(self):
        company_id = self.env['res.users']._get_company()
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the  current user!'))
        return company_id

    @api.model
    def _get_default_store(self):
        return self.env.user.default_store_id

    @api.one
    def _compute_recipe_count(self):
        self.recipe_count = self.env['sale.recipe'].search_count([('optometry_id', '=', self.id)])

    recipe_count = fields.Integer(string='Recipe Count', compute='_compute_recipe_count', help='')
    name = fields.Char(string='Number', defalut='/', copy=False, readonly='True', help='')
    date_order = fields.Date(string='Date Order', default=fields.Date.today, help='')
    partner_id = fields.Many2one('res.partner', string='Partner', required='True', help='')
    user_id = fields.Many2one('res.users', string='User', default=lambda s: s.env.uid, help='')
    company_id = fields.Many2one('res.company', string='company', default=_get_default_company, help='')
    dist_sph_r = fields.Char(string='Distance SPH R', help='')
    dist_cyl_r = fields.Char(string='Distance CYL R', help='')
    dist_ax_r = fields.Char(string='Distance AX R', help='')
    read_add_r = fields.Char(string='Reading ADD R', help='')
    prism_vector_r = fields.Char(string='Prism Vector R', help='')
    prism_angle_r = fields.Char(string='Prism Angle R', help='')
    vision_r = fields.Char(string='VA R', help='')
    pd_r = fields.Char(string='PD R', help='')
    radian_r = fields.Char(string='Radian R', help='')
    dist_sph_l = fields.Char(string='Distance SPH L', help='')
    dist_cyl_l = fields.Char(string='Distance CYL L', help='')
    dist_ax_l = fields.Char(string='Distance AX L', help='')
    read_add_l = fields.Char(string='Reading ADD L', help='')
    prism_vector_l = fields.Char(string='Prism Vector L', help='')
    prism_angle_l = fields.Char(string='Prism Angle L', help='')
    vision_l = fields.Char(string='VA L', help='')
    pd_l = fields.Char(string='PD L', help='')
    radian_l = fields.Char(string='Radian L', help='')
    eye_benefit_l = fields.Char(string=u'利眼 L', help='')
    eye_benefit_r = fields.Char(string=u'利眼 R', help='')
    customer_description_id = fields.Many2one('sale.customer.description', string=u'主訴', help='')
    note = fields.Text(string=u'備註', help='')
    store_id = fields.Many2one('sale.store', string=u'門店', default=_get_default_store, readonly='True', help='')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env.ref('cu_four_sale.sale_optometry')._next() or '/'
        return super(SaleOptometry, self).create(vals)


class CustomerDescription(models.Model):
    _name = 'sale.customer.description'
    _description = 'Sale Customer Description'

    code = fields.Char(string=u'編號', required='True', help='')
    name = fields.Char(string=u'主訴', required='True', help='')
    note = fields.Text(string=u'說明', help='')

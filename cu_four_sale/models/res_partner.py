# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.osv import osv


class Partner(models.Model):
    _inherit = 'res.partner'

    @api.one
    def _compute_recipe_count(self):
        self.recipe_count = self.env['sale.recipe'].search_count([('partner_id', '=', self.id)])

    @api.one
    def _compute_optometry_count(self):
        self.optometry_count = self.env['sale.optometry'].search_count([('partner_id', '=', self.id)])

    @api.model
    def _get_default_store(self):
        return self.env.user.default_store_id

    recipe_ids = fields.One2many('sale.recipe', 'partner_id', string='Recipes', help='')
    recipe_count = fields.Integer(string='Recipe Count', compute='_compute_recipe_count', help='')
    optometry_count = fields.Integer(string='Optometry Count', compute='_compute_optometry_count', help='')
    relation_ids = fields.One2many('res.partner.relation', 'partner_master_id', string='Relation Partner', help='')
    introducer_id = fields.Many2one('res.partner', string='Introducer', help='')
    introduced_ids = fields.One2many('res.partner', 'introducer_id', string='Introduce Partner', help='')
    store_id = fields.Many2one('sale.store', string=u'門店', default=_get_default_store, help='')
    invoice_name = fields.Char(string=u'發票抬頭', help='')
    name_company = fields.Char(string=u'統一編號', help='')
    sex = fields.Char(string=u'性別', help='')
    old_ref = fields.Char(string=u'舊客戶編號', help='')

    @api.one
    @api.onchange('relation_ids')
    def _onchange_relation_ids(self):
        for relation_id in self.relation_ids:
            if not (relation_id.name or relation_id.partner_id):
                raise osv.except_osv(_('提示'), _('客户关系中名稱和客户，不能同时为空！'))


class PartnerRelation(models.Model):
    _name = 'res.partner.relation'

    name = fields.Char(string='Description', help='')
    type = fields.Many2one('res.partner.relation.type', string='Type', help='')
    partner_master_id = fields.Many2one('res.partner', string='Relation Partner', on_delete='cascade', help='')
    partner_id = fields.Many2one('res.partner', string='Partner', help='')


class PartnerRelationType(models.Model):
    _name = 'res.partner.relation.type'

    name = fields.Char(string='名稱', help='')



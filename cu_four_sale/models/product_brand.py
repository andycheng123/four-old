# -*- coding:utf-8 -*-
from openerp import models, api, fields


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = '品牌'

    code = fields.Char(string=u'編號', required='True', help='')
    name = fields.Char(string=u'名稱', required='True', help='')
    note = fields.Text(string=u'說明', help='')
    partner_id = fields.Many2one('res.partner', required='True', string=u'供應商', help='')
    partner_name = fields.Char(string=u'供應商名稱', help='')

    _order = 'code'

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

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.partner_name = self.partner_id and self.partner_id.name or ''

# -*- coding: utf-8 -*-

from openerp import models, fields, api


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def wkf_confirm_order(self):
        res = super(purchase_order, self).wkf_confirm_order()
        self.env['res.partner'].browse(list(set(self.mapped('partner_id.id'))))._update_last_purchase_order()
        return res


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    sequence = fields.Integer(string='序号', default=10, help='用于列表排序用')

    @api.multi
    def name_get(self):
        return [(l.id, '%s#%s' % (l.order_id.name, l.sequence)) for l in self]


class purchase_vender(models.Model):
    _inherit = 'res.partner'

    date_last_purchase = fields.Date(string=u'最后采购交易时间', readonly=True, help=u'最后采购交易时间')
    amount_last_purchase = fields.Float(string=u'最后采购交易金额', readonly=True, help=u'最后采购交易金额')

    @api.multi
    def _update_last_purchase_order(self):

        if not self.ids:
            return
        self._cr.execute("""
                 update res_partner set date_last_purchase=b.date_order,amount_last_purchase=b.amount_total
                 from  (select partner_id,date_order,amount_total from purchase_order
                        where id in(select max(id) as id from purchase_order aa
                                    left join (select partner_id,max(date_order) as date_order
                                               from purchase_order group by partner_id) bb
                                               on bb.partner_id=aa.partner_id
                                    where bb.partner_id in %s group by bb.partner_id)) b
                 where res_partner.id=b.partner_id and supplier= true and b.partner_id>0
            """, (tuple(self.ids),))

    @api.model
    def update_all_last_purchase_order(self):
        self.search([('supplier', '=', True)])._update_last_purchase_order()


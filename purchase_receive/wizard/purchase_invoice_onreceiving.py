# -*- coding: utf-8 -*-
__author__ = 'kevin'

from openerp import models, api, fields, _
from openerp.exceptions import Warning


class purchase_invoice_onreceiving(models.TransientModel):
    _name = 'purchase.invoice.onreceiving'
    _description = u'采购进货发票开立'

    @api.model
    def _get_journal(self):
        journal_obj = self.env['account.journal']
        journals = journal_obj.search([('type', '=', 'purchase')])
        return journals and journals[0].id or False

    journal_id = fields.Many2one('account.journal', 'Destination Journal', default=_get_journal, domain=[('type', '=', 'purchase')], required=True)
    invoice_date = fields.Date(string='立账日期', default=fields.Date.today, help='当前发票所立账的月份及日期')
    supplier_invoice_number = fields.Char(string='Supplier Invoice Number',
                                          help="The reference of this invoice as provided by the supplier.",)

    @api.model
    def view_init(self, fields_list):
        res = super(purchase_invoice_onreceiving, self).view_init(fields_list)
        rcv_obj = self.env['purchase.receive']
        count = 0
        active_ids = self.env.context.get('active_ids',[])
        for rcv in rcv_obj.browse(active_ids):
            if rcv.invoice_state != '2binvoiced':
                count += 1
        if len(active_ids) == count:
            raise Warning(_('None of these picking lists require invoicing.'))
        return res

    @api.multi
    def open_invoice(self):
        invoice_ids = self.create_invoice()
        if not invoice_ids:
            raise Warning(_('No invoice created!'))

        action_id = self.env.ref('account.action_invoice_tree2')

        if action_id:
            action = action_id.read()[0]
            action['domain'] = "[('id','in', ["+','.join(map(str, invoice_ids))+"])]"
            return action
        return True

    @api.multi
    def create_invoice(self):
        inv_type = 'in_invoice'

        active_ids = self._context.get('active_ids', [])
        rcv_ids = self.env['purchase.receive'].browse(active_ids)
        picking_ids = self.env['stock.picking'].with_context(date_inv=self.invoice_date, inv_type=inv_type)
        for rcv in rcv_ids:
            picking_ids += rcv.picking_ids
        res = picking_ids.action_invoice_create(self.journal_id.id,
                                                group=True,
                                                type=inv_type,)
        rcv_ids.write({'invoice_ids': [(4, x) for x in res]})
        rcv_ids.signal_workflow('invoice_created')
        return res





# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError, Warning
from itertools import groupby
from operator import itemgetter

class purchase_receive(models.Model):
    _name = 'purchase.receive'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = u'采购收货单'

    def _get_picking_in(self):
        return self.env.ref('stock.picking_type_in').id

    @api.multi
    def _get_picking_ids(self):
        for r in self:
            r.picking_ids = self.env['stock.picking']
        if not self.ids:
            return
        query = """
        select a.receive_id, m.picking_id
        from purchase_receive_line a, stock_move m
        where m.receive_line_id=a.id and a.receive_id in %s
        order by a.receive_id
        """
        self.env.cr.execute(query, (tuple(self.ids),))
        picks = {c[0]: map(itemgetter(1), c[1]) for c in groupby(self.env.cr.fetchall(), itemgetter(0))}
        for r in self:
            r.picking_ids = picks.get(r.id, [])

    @api.one
    @api.depends('picking_ids.invoice_state')
    def _get_invoice_state(self):
            self.invoice_state = 'none'
            for pick in self.picking_ids:
                if pick.invoice_state == 'invoiced':
                    self.invoice_state = 'invoiced'
                elif pick.invoice_state == '2binvoiced':
                    self.invoice_state = '2binvoiced'
                    break

    @api.one
    def _set_invoice_state(self):
        invoice_state = self.invoice_state
        if self.picking_ids:
            self.picking_ids.write({'invoice_state': invoice_state})

    name = fields.Char('单据编号', default='/', readonly=True, copy=False)
    date_receive = fields.Date(string='收货日期', default=fields.Date.today, required='True', readonly=True,
                               states={'draft': [('readonly', False)]}, help='计划收货日期')
    partner_id = fields.Many2one('res.partner', string='供应商', required='True', readonly='True',
                                 states={'draft': [('readonly', False)]}, help='')
    partner_ref = fields.Char(string='供應商單號', help='供應商單號')
    notes = fields.Text(string='备注说明', help='')
    state = fields.Selection([('draft', '草稿'),
                             ('shipping', '收货中'),
                             ('manual', '待开发票'),
                             ('progress', '收款中'),
                             ('except_receive', '收货异常'),
                             ('except_invoice', '发票异常'),
                             ('done', '已完成'),
                             ('cancelled', '已取消')], string='状态', default='draft', required='True', readonly='True',
                             help='收货单的执行状态.\n'
                                  '* 收货中表示该单已经正式收效，正在执行具体收货过程，如已产生入库单\n'
                                  '* 待开发票表示该单已完成收货流程，等待供应提供发票立帐\n'
                                  '* 已完成表示已完成收货流程与完成立帐\n'
                                  '* 已取消未收货并未立帐的可以被取消或删除')
    line_ids = fields.One2many('purchase.receive.line', 'receive_id', string='收货明细', copy=True, readonly='True',
                               states={'draft': [('readonly', False)]}, help='')
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', help="This will determine picking type of incoming shipment", required=True,
                                       default=_get_picking_in, readonly='True', states={'draft': [('readonly', False)]})
    picking_ids = fields.One2many('stock.picking', compute='_get_picking_ids', string='出库单', help='该销货单关联的所有出库单')
    invoice_ids = fields.Many2many('account.invoice', 'purchase_receive_invoice_rel', 'receive_id', 'invoice_id',
                                   string='Invoices', help='Invoice generated in a receive')
    invoice_state = fields.Selection([
                            ("invoiced", "Invoiced"),
                            ("2binvoiced", "To Be Invoiced"),
                            ("none", "Not Applicable")
                        ], compute='_get_invoice_state', inverse='_set_invoice_state', string="Invoice Control")

    _order = 'id desc'

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].with_context(sequence_time=vals.get('date_receive', False))\
                .next_by_id(self.env.ref('purchase_receive.sequence_purchase_receive').id)
        return super(purchase_receive, self).create(vals)

    @api.multi
    def unlink(self):
        for r in self:
            if r.state not in ('draft', 'cancelled'):
                raise Warning(_('只允许删除草稿或已取消的单据。'))
        return super(purchase_receive, self).unlink()

    @api.model
    def _prepare_picking(self, receive):
        move_obj = self.env['stock.move']
        move_ids = []
        for line in receive.line_ids:
            qty = line.product_qty
            domain = [('product_id', '=', line.product_id.id), ('receive_line_id', '=', False), ('state', 'not in', ('done', 'cancel'))]
            if line.purchase_order_id:
                domain += [('purchase_line_id.order_id', '=', line.purchase_order_id.id)]
            else:
                domain += [('purchase_line_id.order_id.partner_id', '=', line.receive_id.partner_id.id)]
            for move in move_obj.search(domain):
                if tools.float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) <= 0:
                    break
                if tools.float_compare(qty, move.product_uom_qty, precision_rounding=move.product_uom.rounding) < 0:
                    move = move_obj.browse(move_obj.split(move, qty))
                move.write({'picking_type_id': receive.picking_type_id.id, 'receive_line_id': line.id})
                move_ids.append((4, move.id))
                qty -= move.product_uom_qty
            if tools.float_compare(qty, 0.0, precision_rounding=line.product_uom_id.rounding) > 0:
                raise Warning(_(u'%s 订单数量不足，多出订单数量：%s') % (line.name, qty))
        pick_vals = {
            'picking_type_id': receive.picking_type_id.id,
            'partner_id': receive.partner_id.id,
            'date': receive.date_receive,
            'move_lines': move_ids,
            'origin': receive.name,
        }
        return pick_vals

    @api.multi
    def create_picking(self):
        for r in self:
            pick = self.env['stock.picking'].create(self._prepare_picking(r))
            pick.action_confirm()

    @api.multi
    def confirm(self):
        self.create_picking()
        self.write({'state': 'shipping'})
        return True

    @api.multi
    def test_received(self):
        for r in self:
            if any(x.state not in ('done', ) for x in r.picking_ids):
                return False
        return True

    @api.multi
    def test_receive_except(self):
        at_least_one_cancelled = False
        all_doneorcancel = True
        for r in self:
            for pick in r.picking_ids:
                if pick.state == 'cancel':
                    at_least_one_cancelled = True
                if pick.state not in ('done', 'cancel'):
                    all_doneorcancel = False
        return at_least_one_cancelled and all_doneorcancel

    @api.multi
    def wkf_invoice_created(self):
        res = []
        self.write({'state': 'progress'})
        for rcv in self:
            res += rcv.invoice_ids.filtered(lambda x: x.state == 'draft').mapped(int)
        return res and res[0] or False

    @api.multi
    def wkf_receive_cancel(self):
        self.write({'state': 'cancelled'})
        return True

    @api.multi
    def wkf_receive_done(self):
        self.write({'state': 'done'})
        return True

    @api.multi
    def view_picking(self):
        '''
        This function returns an action that display existing picking orders of given purchase order ids.
        '''
        action = self.env.ref('stock.action_picking_tree').read()[0]

        pick_ids = []
        for po in self:
            pick_ids += [picking.id for picking in po.picking_ids]

        #override the context to get rid of the default filtering on picking type
        action['context'] = {}
        #choose the view_mode accordingly
        if len(pick_ids) > 1:
            action['domain'] = "[('id','in',[" + ','.join(map(str, pick_ids)) + "])]"
        else:
            form = self.env.ref('stock.view_picking_form')
            action['views'] = [(form.id, 'form')]
            action['res_id'] = pick_ids and pick_ids[0] or False
        return action

    @api.multi
    def invoice_open(self):
        result = self.env.ref('account.action_invoice_tree2')
        result = result.read()[0]
        inv_ids = []
        for po in self:
            inv_ids+= po.invoice_ids.mapped(int)
        if not inv_ids:
            raise Warning(_('Please create Invoices.'))
            #choose the view_mode accordingly
        if len(inv_ids) > 1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = self.env.ref('account.invoice_supplier_form')
            result['views'] = [(res and res[0].id or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result


class purchase_receive_line(models.Model):
    _name = 'purchase.receive.line'
    _description = u'采购收货明细'

    name = fields.Text('Description', required=True)
    receive_id = fields.Many2one('purchase.receive', string='采购收货单', ondelete='cascade', help='')
    product_id = fields.Many2one('product.product', string='产品', help='接收的产品')
    product_uom_id = fields.Many2one('product.uom', related='product_id.uom_id', store=True,
                                     string='计量单位', readonly='True', help='收货时的计量单位')
    product_qty = fields.Float(string='数量', digits_compute=dp.get_precision('Product Unit Of Measure'), help='')
    purchase_order_id = fields.Many2one('purchase.order', string='采购订单', ondelete='set null',
                                       help='按订单收货时，所对应的采购订单')

    @api.model
    def create(self, vals):
        if vals.get('product_id') and 'name' not in vals:
            vals['name'] = self.product_id.name_get()[0][1]
        return super(purchase_receive_line, self).create(vals)

    @api.one
    @api.onchange('purchase_order_id', 'product_id')
    def _onchange_product_id(self):
        if not self.product_id:
            self.product_qty = 0.0
            return

        self.name = self.product_id.name_get()[0][1]

        query = """
        select sum(m.product_uom_qty) as qty
        from stock_move m, purchase_order_line pl
        where m.purchase_line_id=pl.id
          and m.receive_line_id is null
          and m.state not in ('done', 'cancel')
          and m.product_id = %s
        """
        params = [self.product_id.id]
        if self.purchase_order_id:
            query += '\nand pl.order_id = %s'
            params.append(self.purchase_order_id.id)
        self.env.cr.execute(query, params)
        qty = self.env.cr.fetchone()
        if qty:
            qty = qty[0]
        self.product_qty = qty


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def action_picking_create(self):
        for order in self:
            self._create_stock_moves(order, order.order_line, )

    @api.model
    def _prepare_order_line_move(self, order, order_line, picking_id, group_id):
        res = super(purchase_order, self)._prepare_order_line_move(order, order_line, picking_id, group_id)
        for vals in res:
            vals['picking_type_id'] = False
        return res


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    @api.one
    @api.depends('move_ids')
    def _compute_received_qty(self):
        if self.state in ('draft', 'cancel'):
            self.unreceived_qty = self.product_qty
            self.received_qty = 0
        else:
            self.unreceived_qty = sum([move.product_uom_qty for move in self.move_ids if move.state not in ('done', 'cancel')])
            self.received_qty = self.product_qty - self.unreceived_qty

    unreceived_qty = fields.Float(string='未交數量', compute='_compute_received_qty', digits=dp.get_precision('Product Unit of Measure'), help='')
    received_qty = fields.Float(string='已交數量', compute='_compute_received_qty', digits=dp.get_precision('Product Unit of Measure'), help='')


class stock_move(models.Model):
    _inherit = 'stock.move'


    receive_line_id = fields.Many2one('purchase.receive.line', string='收货明细',
                                      help='如果当前移动是采购订单所产生的，此处呈现已创建的收货单之明细')

    @api.multi
    def write(self, vals):
        res = super(stock_move, self).write(vals)
        from openerp.workflow.service import WorkflowService
        if vals.get('state') in ['done', 'cancel']:
            for move in self:
                if move.receive_line_id.receive_id:
                    move.receive_line_id.receive_id.step_workflow()
        return res











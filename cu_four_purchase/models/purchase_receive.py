# -*- coding:utf-8 -*-
from openerp import models, api, fields, tools, _
import openerp.addons.decimal_precision as dp
from openerp.osv import osv
from itertools import groupby
from operator import attrgetter, itemgetter
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)

"""
split lot number
return lot_no char, num[] int
"""
def extract_lot_no(lot_no):
    if not lot_no:
        return False, False
    num = []
    for i in range(len(lot_no)-1, -1, -1):
        if lot_no[i].isdigit():
            num.insert(0, lot_no[i])
            lot_no = lot_no[:i]
        else:
            break
    return lot_no, int(''.join(num))


class PurchaseReceive(models.Model):
    _inherit = 'purchase.receive'

    @api.model
    def _get_default_company(self):
        company_id = self.env['res.users']._get_company()
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the  current user!'))
        return company_id

    @api.multi
    def _get_picking_ids(self):
        if self.specs_flag:
            for r in self:
                r.picking_ids = self.env['stock.picking']
            if not self.ids:
                return
            query = """
            select a.receive_id, m.picking_id
            from stock_receive_operation a, stock_move m
            where m.operation_line_id=a.id and a.receive_id in %s
            order by a.receive_id
            """
            self.env.cr.execute(query, (tuple(self.ids),))
            picks = {c[0]: map(itemgetter(1), c[1]) for c in groupby(self.env.cr.fetchall(), itemgetter(0))}
            for r in self:
                r.picking_ids = picks.get(r.id, [])
        else:
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

    @api.model
    def _get_default_store(self):
        return self.env.user.default_store_id

    @api.model
    def _get_default_user(self):
        return self.env.user

    receive_operation_ids = fields.One2many('stock.receive.operation', 'receive_id', string='Receive Operation',
                                            help='')
    strategy_id = fields.Many2one('purchase.receive.strategy', string=u'分配方案', help='')
    start_code_no = fields.Char(string=u'起始序號', size=12, help=u'如果此欄位有值，則按此序號開始按1遞增')
    store_id = fields.Many2one('sale.store', string=u'門店', default=_get_default_store,)
    specs_flag = fields.Boolean(string=u'產品品規', default=False, help='')
    user_id = fields.Many2one('res.users', string=u'採購員', default=_get_default_user, help='')
    update_ids = fields.One2many('purchase.receive.update', 'receive_id', string=u'更新明細', help=u'更新明細')
    update_done = fields.Boolean(string=u'是否已產生更新明細', default=False, help=u'是否已產生更新明細')
    update_running = fields.Boolean(string=u'是否產生更新明細中', default=False, help=u'是否產生更新明細中')

    _defaults = {
        'invoice_state': '2binvoiced',
    }

    @api.cr_uid
    def generate_updates(self, cr, uid, ids=None, context=None):
        """
        Update product price and store in update_ids
        """

        if context is None: context = {}
        rcvs = self.browse(cr, uid, self.search(cr, uid, [('state', '!=', 'draft'), ('update_done', '=', False), ('specs_flag', '=', True)], context), context)
        _logger.info("Records to update price: " + str(rcvs))

        for rcv in rcvs:
            if not rcv.update_running:
                rcv.update_running = True
                _logger.info("Record to update: " + str(rcv))
                updates = []
                for line in rcv.line_ids:
                    for product in self.pool.get('product.product').search(cr, uid,[('product_specs_id', '=', line.product_id.product_specs_id.id), ('qty_available', '>', 0)], context):
                        product = self.pool.get('product.product').browse(cr, uid, product, context)
                        if product.list_price_prod != line.price:
                            product.list_price_prod = line.price
                            updates.append((0, 0, {
                                'product_id': product.id,
                                'receive_id': rcv.id
                            }))
                _logger.info("Update with: " + str(updates))
                rcv.update_ids.unlink()
                rcv.write({'update_ids': updates})
                rcv.update_done = True
                rcv.update_running = False

        return True

    @api.multi
    def generate_lots(self):
        for rcv in self:
            salt = ''
            if rcv.start_code_no:
                salt = rcv.start_code_no

            prefix, start_no = extract_lot_no(salt)

            strategy = rcv.strategy_id.type_strategy
            #{'product1': qty, 'product2': qty...}
            pqtys = {g[0]: sum(map(attrgetter('product_qty'), g[1])) for g in
                     groupby(rcv.line_ids.sorted(lambda x: x.product_id.id), lambda x: x.product_id.id)}
            if strategy == 'ratio':
                pstra = {}
                #by percentage dispatch qty [('product1', qty), ('product2', qty)...]
                for product_id, ttl in pqtys.items():
                    remain_qty = ttl
                    percent = 0.0
                    stra = []
                    for sln in rcv.strategy_id.line_ids:
                        qty = round(ttl * sln.ratio / 100)
                        percent += sln.ratio
                        if qty == 0:
                            continue
                        #[(store_id, dispatch_qty)]
                        stra.append((sln.store_id.id, min(remain_qty, qty)))
                        remain_qty -= qty
                        if remain_qty < 0 or percent >= 100:
                            break
                    #{'product_id': [(store_id, dispatch_qty)]}
                    pstra[product_id] = stra

            else:
                stra = rcv.strategy_id.line_ids.filtered('fixed_qty').mapped(lambda x: (x.store_id.id, x.fixed_qty))
                pstra = dict.fromkeys(pqtys.keys(), stra)

            ops = []
            for line in rcv.line_ids:
                stra = pstra[line.product_id.id]
                for i in range(int(line.product_qty)):
                    if start_no:
                        start_no += 1
                        default_code = prefix + str(start_no-1)
                    else:
                        default_code = self.env.ref('cu_four_purchase.sequence_product_default_code')._next() or '/'

                    #get store_id
                    store_id = self.store_id.id
                    if stra:
                        store_id, qty = stra[0]
                        qty -= 1
                        if qty <= 0:
                            del stra[0]
                        else:
                            stra[0] = (store_id, qty)
                    product_id = line.product_id.id
                    if rcv.specs_flag:
                        pass

                    ops.append((0, 0, {
                        'product_id': product_id,
                        'product_uom_id': line.product_id.uom_id.id,
                        'product_qty': 1,
                        'default_code': default_code,
                        'store_id': store_id,
                        'purchase_order_id': line.purchase_order_id.id,
                        'sequence': line.sequence,
                        'cost': line.cost,
                    }))
            rcv.receive_operation_ids.unlink()
            rcv.write({'receive_operation_ids': ops})

    @api.model
    def _prepare_picking(self, receive):
        pick_vals = super(PurchaseReceive, self)._prepare_picking(receive)
        pick_vals.update({'invoice_state': '2binvoiced'})
        return pick_vals

    @api.multi
    def confirm(self):
        if self.specs_flag:
            if not self.receive_operation_ids:
                raise Warning(_(u'請先爲產品分配序號'))

            move_line_val = []
            for store_id, operations in groupby(self.receive_operation_ids.sorted(lambda x: (x.store_id.id, x.product_id.id)),
                                           lambda x: x.store_id):
                warehouse = self.env['stock.warehouse'].search([('store_id', '=', store_id.id)], limit=1)
                if not warehouse:
                    raise Warning(_(u'未找到门店[%s]所对应的仓库') % store_id.name)
                picking_type = self.env['stock.picking.type'].search([('warehouse_id', '=', warehouse.id),
                                                                      ('code', '=', 'internal')], limit=1)
                location_src_id = self.picking_type_id.default_location_src_id.id,
                # if store_id != self.store_id:
                #     location_src_id = self.picking_type_id.default_location_dest_id.id,

                move_obj = self.env['stock.move']
                for line in operations:
                    qty = line.product_qty
                    name_product = line.product_id.product_tmpl_id.name
                    if line.product_id.product_specs_id and line.product_id.product_specs_id.name:
                        name_product += '-'+line.product_id.product_specs_id.name
                    name_code_product = '[' + line.default_code + ']' + name_product

                    prod_val = {
                        'name': line.product_id.product_tmpl_id.name,
                        'name_product': name_product,
                        'name_code_product': name_code_product,
                        'product_tmpl_id': line.product_id.product_tmpl_id.id,
                        'product_specs_id': line.product_id.product_specs_id.id,
                        'default_code': line.default_code,
                        'ean8': line.default_code,
                        'standard_price_prod': line.cost,
                        'list_price_prod': line.product_price_latest,
                    }
                    line.product_id.product_tmpl_id.cost_method = 'real'
                    line.product_id.product_tmpl_id.standard_price = line.cost
                    product_id_new = self.env['product.product'].create(prod_val)

                    domain = [('product_id', '=', line.product_id.id), ('receive_line_id', '=', False), ('state', 'not in', ('done', 'cancel'))]
                    if line.purchase_order_id:
                        domain += [('purchase_line_id.order_id', '=', line.purchase_order_id.id)]
                    else:
                        domain += [('purchase_line_id.order_id.partner_id', '=', line.receive_id.partner_id.id)]
                    moves = move_obj.search(domain)
                    for move in moves:
                        #qty <= 0 break
                        if tools.float_compare(qty, 0.0, precision_rounding=move.product_uom.rounding) <= 0:
                            break
                        #qty <= move_qty split
                        if tools.float_compare(qty, move.product_uom_qty, precision_rounding=move.product_uom.rounding) < 0:
                            move = move_obj.browse(move_obj.split(move, qty))

                        move.write({
                            'name': '%s-%s-%s' % (store_id.name, product_id_new.name, 1),
                            'product_id': product_id_new.id,
                            'product_uom': product_id_new.uom_id.id,
                            'product_uom_qty': 1,
                            'location_id': location_src_id,
                            'location_dest_id': picking_type.default_location_dest_id.id,
                            'operation_line_id': line.id,
                            'price_unit': line.cost,
                        })
                        move_line_val.append((4, move.id))
                        qty -= move.product_uom_qty

                    line.product_id = product_id_new
                    #retain_qty > 0, over leak
                    if tools.float_compare(qty, 0.0, precision_rounding=line.product_uom_id.rounding) > 0:
                        raise Warning(_(u'%s 订单数量不足，多出订单数量：%s') % (line.product_id.name, qty))

            picking_val = {
                'picking_type_id': self.picking_type_id.id,
                'partner_id': self.partner_id.id,
                'date': self.date_receive,
                'origin': self.name,
                'move_lines': move_line_val,
                'invoice_state': '2binvoiced'
            }
            picking = self.env['stock.picking'].with_context(no_recompute=True).create(picking_val)
            picking.do_transfer()
            self.write({'state': 'shipping'})
        else:
            rtn = super(PurchaseReceive, self).confirm()
            return rtn

class PurchaseReceiveLine(models.Model):
    _inherit = 'purchase.receive.line'

    price = fields.Float(related = 'product_id.list_price_prod', string = '定價', digits=dp.get_precision('Product Price'), help = '定價')
    sequence = fields.Integer(string=u'序號', readonly=True, help='')
    cost = fields.Float(string=u'成本單價', readonly=True, help=u'成本單價')

class PurchaseReceiveUpdate(models.Model):
    _name = 'purchase.receive.update'

    @api.one
    @api.depends('product_id')
    def _compute_product_name(self):
        self.product_name = self.product_id.product_tmpl_id.name + '-' + self.product_id.product_specs_id.name

    receive_id = fields.Many2one('purchase.receive', string='進貨單', ondelete='cascade', help='進貨單')
    product_id = fields.Many2one('product.product', string='產品', ondelete='cascade', help='產品')
    product_code = fields.Char(related='product_id.default_code', string='貨號')
    product_name = fields.Char(compute='_compute_product_name', string = '品名')
    product_brand = fields.Char(related='product_id.product_tmpl_id.brand_id.name', string='品牌', readonly=True)
    product_price = fields.Float(related='product_id.list_price_prod', string='定價')
    store_id = fields.Many2one('sale.store', string='門市', help='門市')
    receive_date = fields.Date(string=u'確認日期', related='receive_id.date_receive', help=u'確認日期')


class StockMove(models.Model):
    _inherit = 'stock.move'

    operation_line_id = fields.Many2one('stock.receive.operation', string='收货明细',
                                        help='如果当前移动是采购订单所产生的，此处呈现已创建的收货单之明细')
    sequence = fields.Integer(related='purchase_line_id.sequence', string=u'序號', store=True, readonly=True, help='')

    @api.multi
    def write(self, vals):
        res = super(StockMove, self).write(vals)
        from openerp.workflow.service import WorkflowService
        if vals.get('state') in ['done', 'cancel']:
            for move in self:
                if move.operation_line_id.receive_id:
                    move.operation_line_id.receive_id.step_workflow()
        return res


class StockReceiveOperation(models.Model):
    _name = 'stock.receive.operation'
    _description = u'分配明細'

    @api.one
    @api.depends('product_id')
    def _compute_product_name(self):
        self.product_name = self.product_id.product_tmpl_id.name + '-' + self.product_id.product_specs_id.name

    sequence = fields.Integer(string=u'序號', readonly='True', help='')
    receive_id = fields.Many2one('purchase.receive', string='Purchase Receive', ondelete='cascade', help='')
    product_id = fields.Many2one('product.product', '產品')
    product_name = fields.Char(compute='_compute_product_name', string = '品名')
    product_brand = fields.Char(related='product_id.product_tmpl_id.brand_id.name', string='品牌', readonly=True)
    product_price_latest = fields.Float(related = 'product_id.list_price_prod', digits=dp.get_precision('Product Price'), string = '定價')
    product_uom_id = fields.Many2one('product.uom', string=u'度量單位', help='')
    product_qty = fields.Float(string=u'數量', digits=dp.get_precision('Product Unit of Measure'), required=True, help='')
    default_code = fields.Char(string=u'貨號', help='')
    store_id = fields.Many2one('sale.store', string=u'分店', help='')
    purchase_order_id = fields.Many2one('purchase.order', string=u'採購單', help='')
    cost = fields.Float(string=u'成本單價', readonly=True, help=u'成本單價')


class PurchaseReceiveStrategy(models.Model):
    _name = 'purchase.receive.strategy'
    _description = 'Purchase Receive Strategy'

    code = fields.Char(string=u'編號', required='True', help='')
    name = fields.Char(string=u'名称', required='True', help='')
    type_strategy = fields.Selection([('ratio', u'比例'), ('fixed', u'固定')],
                                     default='ratio', string=u'分配模式', required='True', help='')
    note = fields.Char(string=u'說明', help='')
    line_ids = fields.One2many('purchase.receive.strategy.line', 'strategy_id', string='Strategy Line', help='')

    @api.onchange('type_strategy')
    def onchange_type_strategy(self):
        for line in self.line_ids:
            line.ratio = 0
            line.fixed_qty = 0


class PurchaseReceiveStrategyLine(models.Model):
    _name = 'purchase.receive.strategy.line'
    _description = 'Purchase Receive Strategy'

    sequence = fields.Integer(string='Sequence', default=10, required='True', help='')
    strategy_id = fields.Many2one('purchase.receive.strategy', string='Strategy', ondelete='cascade', help='')
    store_id = fields.Many2one('sale.store', string=u'分店', required='True', help='')
    ratio = fields.Float(string=u'分配百分比', digits=(16, 2), help=u'分配百分比')
    fixed_qty = fields.Integer(string=u'分配固定数量', help='')

    _order = 'sequence'

class purchase_receive_select(models.TransientModel):
    _inherit = 'purchase.receive.select'

    selected_all = fields.Boolean(string=u"全選", default=False, help=u"全選")

    @api.onchange('selected_all')
    def _onchange_partner(self):
        if self.selected_all:
            for line in self.line_ids: line.selected = True
        else:
            for line in self.line_ids: line.selected = False

    @api.one
    @api.onchange('product_id', 'purchase_order_id', 'date_from', 'date_to')
    def _onchange_data(self):
        wheres = ['m.purchase_line_id=pl.id and pl.order_id=po.id '
                  'and m.receive_line_id is null '
                  'and po.partner_id=%s '
                  'and m.state not in (\'done\', \'cancel\')']
        params = [self.partner_id.id]
        if self.product_id:
            wheres.append('m.product_id = %s')
            params.append(self.product_id.id)
        if self.purchase_order_id:
            wheres.append('pl.order_id = %s')
            params.append(self.purchase_order_id.id)
        if self.date_from:
            wheres.append('date_expected >= %s')
            params.append(self.date_from)
        if self.date_to:
            wheres.append('date_expected <= %s')
            params.append(self.date_to)
        filters = 'and '.join(wheres)
        query = """
        select m.product_id,pl.order_id,min(m.date_expected),sum(m.product_uom_qty), min(m.sequence), avg(m.price_unit)
        from stock_move m, purchase_order_line pl, purchase_order po
        where """ + filters + """
        group by m.product_id, pl.order_id
        order by pl.order_id, min(m.sequence)
        """
        items = []
        self.env.cr.execute(query, params)
        for row in self.env.cr.fetchall():
            items.append({
                'product_id': row[0],
                'purchase_order_id': row[1],
                'date_plan': row[2],
                'unreceive_qty': row[3],
                'select_qty': row[3],
                'sequence': row[4],
                'cost': row[5],
            })
        self.line_ids = items

    @api.multi
    def confirm(self):
        rcv = self.env['purchase.receive'].browse(self.env.context.get('active_id', False))
        if rcv:

            for line in self.line_ids.filtered(lambda x: x.selected and x.select_qty > 0.0):
                exist_line = rcv.line_ids.filtered(lambda x: x.purchase_order_id == line.purchase_order_id and x.product_id == line.product_id)
                if not exist_line:
                    rcv.write({'line_ids': [(0, 0, {
                        'purchase_order_id': line.purchase_order_id.id,
                        'product_id': line.product_id.id,
                        'name': line.product_id.name_get()[0][1],
                        'product_qty': line.select_qty,
                        'sequence': line.sequence,
                        'cost': line.cost,
                    })]})
                else:
                    exist_line.product_qty = line.select_qty

class purchase_receive_select_line(models.TransientModel):
    _inherit = 'purchase.receive.select.line'

    sequence = fields.Integer(string=u'序號', readonly=True, help=u'序號')
    cost = fields.Float(string=u'成本單價', readonly=True, help=u'成本單價')
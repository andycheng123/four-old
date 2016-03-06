# -*- coding: utf-8 -*-
{
    'name': "Purchase Receiving",

    'summary': """
        采购收货，采购收货流程""",

    'description': """
        * 采购订单确认后不再自动收货单，而只采购供需求使用的stock.move
        * 允许手工新增收货单，收货数量以采购订单为基准
        * 可从已订未交中选择一张或多张订单的明细成生一张收货单
    """,

    'author': "Kevin Wang",
    'website': "http://www.loyal-info.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['ly_purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_receive_select_view.xml',
        'wizard/purchase_invoice_onreceiving_view.xml',
        'purchase_data.xml',
        'purchase_view.xml',
        'receive_workflow.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
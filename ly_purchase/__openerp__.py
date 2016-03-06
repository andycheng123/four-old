# -*- coding: utf-8 -*-
{
    'name': "ly_purchase",

    'summary': """
        联扬公司特点的采购管理""",

    'description': """
        * 采购订单明细显示序号
    """,

    'author': "Kevin Wang",
    'website': "http://www.loyal-info.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'purchase_view.xml',
        'purchase_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
}
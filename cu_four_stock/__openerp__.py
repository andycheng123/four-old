# -*- coding: utf-8 -*-
{
    'name': u"四季眼鏡，庫存管理",

    'summary': u"""
        多門店管理""",

    'description': """
    """,

    'author': "LY",
    'website': "http://www.loyal-info.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'stock Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock','cu_four_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/stock_view.xml',
        # 'data/sale_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}


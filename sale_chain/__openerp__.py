# -*- coding: utf-8 -*-
{
    'name': u"连锁零售管理",

    'summary': u"""
        多门店管理""",

    'description': """
    """,

    'author': "LY",
    'website': "http://www.loyal-info.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_stock'],

    # always loaded
    'data': [
        'security/sale_security.xml',
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/sale_chain_view.xml',
        'views/sale_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
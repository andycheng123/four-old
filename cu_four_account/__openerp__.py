# -*- coding: utf-8 -*-
{
    'name': u"四季眼鏡，財務管理",

    'summary': u"""
        財務管理""",

    'description': """
    """,

    'author': "",
    'website': "http://www.loyal-info.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account Management',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}

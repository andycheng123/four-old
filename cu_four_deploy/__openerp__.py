# -*- coding: utf-8 -*-
{
    'name': u"四季眼鏡，部署模块",

    'summary': u"""""",

    'description': """
    """,

    'author': "LY",
    'website': "http://www.loyal-info.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Deploy',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['cu_four_base', 'cu_four_sale', 'cu_four_account', 'cu_four_purchase', 'cu_four_stock'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}

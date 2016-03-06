# -*- coding:utf-8 -*-
{
    'name': "四季眼鏡-基礎模組",
    'summary': "四季眼鏡基礎模組客製化",
    'description': """
四季眼鏡 - 基礎模組
==========================================================
四季眼鏡基礎模組客製化

* 介面調整

- v0.2
	* By Andy Cheng
	* 更新過濾器
- v0.1
    * By LY
    """,
    'author': "Andy Cheng <andy.cheng@aboutscript.net>",
    'maintainer':'Andy Cheng <andy.cheng@aboutscript.net>',
    'website': "http://www.dobtor.com",
    'category': 'Base',
    'version': '0.2',
    'depends': ['base', 'product', 'sale_chain', 'hr'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/company_view.xml',
        'views/partner_view.xml',
        'data/product_data.xml',
        'data/sale_chain_data.xml',
    ],
    'demo': [
    ],
}

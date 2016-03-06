# -*- coding: utf-8 -*-
{
    'name': "黃顧問-客製化調撥單",
    'summary': "黃顧問客製化調撥單",
    'description': """
黃顧問 - 客製化調撥單
==========================================================
黃顧問客製化調撥單

* 增加調撥單
* 出貨單位確認
* 收貨單位確認

- v0.2
	* By Andy Cheng
	* 收貨單位確認
	* Todo
	    * Status bar coloring
	    * New API to call server action?
	    * Search view filter - my store
- v0.1
    * By LY
    * 增加調撥單
    """,

    'author': "Andy Cheng <andy.cheng@aboutscript.net>",
    'maintainer':'Andy Cheng <andy.cheng@aboutscript.net>',
    'website': "http://www.dobtor.com",
    'category': 'stock',
    'version': '0.2',
    'depends': ['stock', 'sale_chain'],
    'data': [
        'wizard/move_transfer_wizard.xml',
        'security/move_transfer_security.xml',
        'security/ir.model.access.csv',
        'views/move_transfer_view.xml',
        'data/move_transfer_data.xml',

    ],
    'demo': [
        # 'demo.xml',
    ],
}

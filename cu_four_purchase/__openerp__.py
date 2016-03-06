# -*- coding: utf-8 -*-
{
    'name': "四季眼鏡-採購管理",
    'summary': "四季眼鏡採購管理客製化",
    'description': """
四季眼鏡 - 採購管理
==========================================================
四季眼鏡採購管理客製化

* 款式品規進貨
* 進貨分配明細
    * 更新同款產品價格明細
    * 列印條碼標籤

- V0.3
    * 更新明細改為Cron執行
- v0.2
	* By Andy Cheng
	* 款式品規進貨
	    * 分配明細增加條碼列印用欄位
	    * 更新同款產品價格明細
	    * 介面調整
	    * 列印條碼標籤
- v0.1
    * By LY
    """,
    'author': "Andy Cheng <andy.cheng@aboutscript.net>",
    'maintainer':'Andy Cheng <andy.cheng@aboutscript.net>',
    'website': "http://www.dobtor.com",
    'category': 'Purchase Management',
    'version': '0.3',
    'depends': ['purchase_receive', 'cu_four_base', 'cu_four_sale', 'sale_chain'],
    'data': [
        'security/purchase_security.xml',
        'security/ir.model.access.csv',
        'views/report_product_barcode.xml',
        'views/purchase_view.xml',
        'views/stock_view.xml',
        'data/stock_data.xml',
    ],
    'demo': [
    ],
}

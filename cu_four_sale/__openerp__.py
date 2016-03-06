# -*- coding: utf-8 -*-
{
    'name': "四季眼鏡-銷售管理",
    'summary': "四季眼鏡銷售管理客製化",
    'description': """
四季眼鏡 - 銷售管理
==========================================================
四季眼鏡銷售管理客製化

* 簡化銷貨單流程，使用者可在銷貨單中完成後續財會及物流相關動作。
* 產品主檔資料結構變更，增加款式品規等架構
* 增加處方單、驗光單
* 更新過濾條件

- v0.2
	* By Andy Cheng
	* 更新過濾條件
	* 銷貨單
	    * 修改銷貨單流程，產生發票及出貨單
	    * 出貨單
	        * 出貨單顯示於分頁
	        * 隱藏「檢視出貨單」按鈕
	    * 發票
	        * 發票顯示於分頁
	        * 銷貨單確立後自動產生已確立發票
	    * 付款
	        * 付款資料顯示於分頁
	    * 產品款式
	        * 增加「品規」分頁
	* Todo
	    * Invoice
	        * workflow
	    * Hide view d/o button
	    * Register payment in recieve tab
	    * Chk accounting entries
	    * Refund & return
	    * S/O status
- v0.1
    * By LY
    * 銷貨流程不產生 invoice 或 D/O
    """,
    'author': "Andy Cheng <andy.cheng@aboutscript.net>",
    'maintainer':'Andy Cheng <andy.cheng@aboutscript.net>',
    'website': "http://www.dobtor.com",
    'category': 'Sales Management',
    'version': '0.2',
    'depends': ['sale', 'sales_team', 'cu_four_base', 'account_voucher'],
    'data': [
        'security/ir.model.access.csv',
        'views/recipe_view.xml',
        'views/res_partner_view.xml',
        'views/sale_optometry_view.xml',
        'views/sale_view.xml',
        'views/product_view.xml',
        'views/product_brand_view.xml',
        'views/stock_view.xml',
        # 'views/temp_view.xml',
        'data/sale_data.xml',
    ],
    'demo': [
    ],
}

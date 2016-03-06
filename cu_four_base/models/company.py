# -*- coding:utf-8 -*-
from openerp import models, api, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char(string=u'公司代號', help='')

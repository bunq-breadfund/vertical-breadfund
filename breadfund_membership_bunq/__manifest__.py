# -*- coding: utf-8 -*-
{
    'name': 'Breadfund Membership BUNQ',
    'version': '11.0.1.0.0',
    'summary': 'Membership module BUNQ',
    'author': 'Sunflower IT',
    'website': 'http://www.sunflowerweb.nl',
    'category': 'Extra Tools',
    'images': [],
    'depends': [
        'breadfund_membership',
    ],
    'data': [
        'data/ir_cron.xml',
        'views/member_payment.xml',
        'views/res_company.xml',
        'views/res_partner.xml'
    ],
    'installable': True,
}

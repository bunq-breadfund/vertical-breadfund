# -*- coding: utf-8 -*-

{
    'name': 'Breadfund Membership',
    'version': '11.0.1.0.0',
    'summary': 'Extends membership module to add features for breadfund functionality',
    'author': 'Sunflower IT',
    'website': 'http://www.sunflowerweb.nl',
    'category': 'Extra Tools',
    'images': [],
    'depends': [
        'membership',
        'account',
        'sale_contract',
    ],
    'data': [
        'data/mail_templates.xml',
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/member_contibution.xml',
        'views/member_payment.xml'
    ],
    'installable': True,
}

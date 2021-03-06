# -*- coding: utf-8 -*-
{
    'name': 'Breadfund Membership',
    'version': '11.0.1.0.0',
    'summary': 'Extends membership module to add features for breadfund functionality',
    'author': 'Sunflower IT',
    'website': 'http://www.sunflowerweb.nl',
    'category': 'Extra Tools',
    'depends': [
        'membership'
    ],
    'data': [
        'data/mail_templates.xml',
        'data/res_partner_member_type.xml',
        'data/sequence.xml',
        'security/ir_model_category.xml',
        'security/res_groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        'views/menus.xml',
        'views/member_contribution.xml',
        'views/member_payment.xml',
        'views/res_partner.xml',
        'views/res_partner_sick.xml',
        'views/res_company.xml',
        'views/res_partner_member_type.xml',
        'views/res_company.xml',
        'data/ir_cron.xml'
    ],
    'installable': True,
}

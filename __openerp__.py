{
    'name': 'Customer Credit Limit Request Contact Form',
    'category': 'Website',
    'website': '',
    'summary': 'Create Credit Limit request through the website',
    'version': '1.0',
    'description': """
OpenERP Credit Limit Request Contact Form
====================

        """,
    'author': 'Vipin Kumar Tripathi IN',
    'depends': ['base','sale','website_partner','crm'],
    'data': [
        #'data/website_crm_data.xml',
        'views/credit_limit_view.xml',
        'views/website_creditlimit.xml',
        'data/website_configure_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}

{
    'name': 'Sales Targets',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Track and manage sales targets for your team',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_target_views.xml',
        'views/sale_target_menu.xml',
        'report_sale_target.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}
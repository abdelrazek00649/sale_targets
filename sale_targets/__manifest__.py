{
    'name': 'Sales Targets | أهداف المبيعات',
    'version': '19.0.1.0.0',
    'category': 'Sales',
    'summary': 'Track and manage sales targets for your team',
    'author': 'Mohamed Abdelrazek',
    'website': 'https://wa.me/201050924550',
    'license': 'LGPL-3',
    'price': 19.99,
    'currency': 'USD',
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
    'images': [
        'static/description/main_screenshot.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,}
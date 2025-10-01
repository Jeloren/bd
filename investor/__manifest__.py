# investor_management/__manifest__.py
{
    'name': "Управление Инвестициями",
    'summary': "Модуль для лабораторной работы по проектированию РБД.",
    'description': """
        Проектирование РБД для управления инвестициями на основе лабораторной работы.
        Вариант: Инвестор.
    """,
    'author': "Назаров Ярослав Сергеевич",
    'website': "http://www.chuvsu.ru",
    'category': 'ЧувГУ /Управление Инвестициями',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/investor_views.xml',
        'views/broker_views.xml',
        'views/account_views.xml',
        'views/asset_views.xml',
        'views/transaction_views.xml',
        'data/data.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
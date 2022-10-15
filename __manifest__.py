# -*- coding: utf-8 -*-
{
    'name': "Paie PME",

    'summary': """
        Ce module permet d'automatiser le calcul de paie
        et de présence en utilisant une pointeuse.
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Blueprint",
    'website': "http://150.136.173.59:8069/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human ressource',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'data/data.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

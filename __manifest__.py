# -*- coding: utf-8 -*-
{
    'name': "Tema Portal Resmi Ma'had Al-Jami'ah PTKIN",
    'version': '20.0.1.0.0',
    'category': 'Theme/Education',
    'summary': 'Tema Website Publik Ma\'had Al-Jami\'ah dengan Estetika Modern Purwadhika Tech & Aksen Hijau Tosca/Mint',
    'description': """
        Modul Tema Khusus Website Ma'had Al-Jami'ah (mahad.iainpare.ac.id):
        1. Desain Neo-Minimalist terinspirasi dari Purwadhika Digital Tech School.
        2. Palet warna kontras Charcoal (#171717), Tosca (#0D9488), dan Mint Soft (#2DD4BF / #CCF5DC).
        3. Tipografi modern menggunakan Google Fonts (Inter & Space Grotesk).
        4. Komponen card-based bergaris halus dengan efek hover halus.
        5. Widget publik pencarian verifikasi status Syahadah Ma'had (terkoneksi API).
    """,
    'author': 'sufyALDI | TIPD IAIN Parepare',
    'website': 'https://mahad.iainpare.ac.id',
    'license': 'LGPL-3',
    'depends': ['website', 'sirita_mahad', 'sirita_mahad_pembinaan'],
    'data': [
        'data/website_menu_data.xml',
        'views/layout_templates.xml',
        'views/homepage_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'sirita_theme/static/src/scss/_variables.scss',
        ],
        'web.assets_frontend': [
            'sirita_theme/static/src/scss/_typography.scss',
            'sirita_theme/static/src/scss/_components.scss',
            'sirita_theme/static/src/scss/_header_footer.scss',
            'sirita_theme/static/src/scss/theme.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}

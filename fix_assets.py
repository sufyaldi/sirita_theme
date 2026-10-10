env['ir.attachment'].create([
    {
        'name': 'user_values.scss',
        'url': '/_custom/web.assets_frontend/website/static/src/scss/options/user_values.scss',
        'raw': b'',
        'public': True,
        'mimetype': 'text/scss',
    },
    {
        'name': 'user_theme_color_palette.scss',
        'url': '/_custom/web.assets_frontend/website/static/src/scss/options/colors/user_theme_color_palette.scss',
        'raw': b'',
        'public': True,
        'mimetype': 'text/scss',
    }
])
env.cr.commit()

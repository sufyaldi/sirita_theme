import odoo
from odoo.modules.registry import Registry
from odoo import api, SUPERUSER_ID
import json, urllib.parse, urllib.request, time

odoo.tools.config.parse_config(['-d', 'app-my'])
registry = Registry('app-my')
with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    posts = env['blog.post'].search([('website_id', '=', 2)])
    print(f"Memproses {len(posts)} postingan untuk konversi cover image ke attachment lokal...")

    for idx, post in enumerate(posts, 1):
        if not post.cover_properties:
            continue
        try:
            cp = json.loads(post.cover_properties)
        except Exception:
            continue
        bg = cp.get('background-image', '')
        if not bg or not ('https://' in bg or 'http://' in bg):
            continue

        raw_url = bg.replace('url(\'', '').replace('\')', '').replace('url(\"', '').replace('\")', '').replace('url(', '').replace(')', '')
        if raw_url.startswith('/'):
            continue

        print(f"[{idx}/{len(posts)}] Mengunduh gambar untuk: {post.name[:50]}...")
        try:
            req = urllib.request.Request(raw_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=12) as resp:
                content = resp.read()
            
            # Buat attachment lokal Odoo (Odoo 20 menggunakan field raw)
            ext = 'jpeg'
            if '.png' in raw_url.lower():
                ext = 'png'
            elif '.webp' in raw_url.lower():
                ext = 'webp'
            
            att = env['ir.attachment'].create({
                'name': f'cover_post_{post.id}.{ext}',
                'type': 'binary',
                'raw': content,
                'res_model': 'blog.post',
                'res_id': post.id,
                'public': True,
            })
            cp['background-image'] = f"url('/web/image/{att.id}/cover_post_{post.id}.{ext}')"
            post.cover_properties = json.dumps(cp)
        except Exception as e:
            print(f"[-] Gagal unduh {raw_url}: {e}, gunakan fallback placeholder internal")
            cp['background-image'] = "url('/sirita_theme/static/img/hero_mahasantri.png')"
            post.cover_properties = json.dumps(cp)

    cr.commit()
    print("\n[V] Seluruh cover image artikel berhasil dikonversi ke attachment lokal!")

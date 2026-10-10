#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Crawler & Ingestion Tool: Berita Ma'had Al-Jami'ah
Sumber : https://www.iainpare.ac.id/blog
Target : Odoo 20 Database (app-my) -> Model blog.post (Website 2 - Mahad Jamiyah)
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import re
import json
import time
import os
import sys

def get_mahad_urls():
    sitemap_url = "https://www.iainpare.ac.id/sitemap.xml"
    req = urllib.request.Request(sitemap_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    print(f"[*] Mengunduh sitemap: {sitemap_url}...")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml_data = resp.read()
    except Exception as e:
        print(f"[-] Gagal mengunduh sitemap: {e}")
        return []

    root = ET.fromstring(xml_data)
    namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    
    # Kata kunci spesifik dan relevan dengan Ma'had Al-Jami'ah
    keywords = [
        'mahad', 'ma-had', 'ma\'had', 'mahasantri', 
        'asrama', 'haflah', 'at-taharruj', 'taharruj',
        'tahfizh', 'syahadah', 'santri'
    ]
    
    matched_urls = []
    for loc in root.findall('.//ns:loc', namespace):
        url = loc.text.strip() if loc.text else ''
        if '/blog/' in url and not url.endswith('/feed') and not re.search(r'/blog/[^/]+$', url):
            url_lower = url.lower()
            if any(k in url_lower for k in keywords):
                matched_urls.append(url)
                
    # Urutkan dari yang terbaru (biasanya nomor ID di akhir URL lebih besar)
    def extract_id(u):
        m = re.search(r'-(\d+)$', u)
        return int(m.group(1)) if m else 0

    matched_urls = sorted(list(set(matched_urls)), key=extract_id, reverse=True)
    print(f"[+] Berhasil mengumpulkan {len(matched_urls)} URL artikel Ma'had.")
    return matched_urls

def extract_article(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"[-] Gagal mengunduh {url}: {e}")
        return None

    data = {'source_url': url}

    # 1. Judul
    og_title = re.search(r'<meta\s+property=[\"\']og:title[\"\']\s+content=[\"\'](.*?)[\"\']', html, re.I)
    if og_title:
        data['name'] = og_title.group(1).strip()
    else:
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.I | re.DOTALL)
        data['name'] = re.sub(r'<[^>]+>', '', h1.group(1)).strip() if h1 else 'Berita Ma\'had'

    # 2. Tanggal Publikasi
    pub_time = re.search(r'<meta\s+property=[\"\']article:published_time[\"\']\s+content=[\"\'](.*?)[\"\']', html, re.I)
    if pub_time:
        data['published_date'] = pub_time.group(1).strip()
    else:
        data['published_date'] = False

    # 3. Cover Image
    og_img = re.search(r'<meta\s+property=[\"\']og:image[\"\']\s+content=[\"\'](.*?)[\"\']', html, re.I)
    if og_img:
        img_url = og_img.group(1).strip()
        if not img_url.startswith('http'):
            img_url = urllib.parse.urljoin('https://www.iainpare.ac.id', img_url)
        data['cover_image'] = img_url
    else:
        data['cover_image'] = False

    # 4. Konten HTML
    m = re.search(r'<div[^>]+id=[\"\']o_wblog_post_content[\"\'][^>]*>(.*?)</div>\s*<div[^>]+id=[\"\']o_wblog_post_sidebar', html, re.DOTALL)
    if not m:
        m = re.search(r'<div[^>]+id=[\"\']blog_content[\"\'][^>]*>(.*?)</div>', html, re.DOTALL)
    if not m:
        m = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)

    if m:
        raw_content = m.group(1)
        # Normalisasi seluruh URL aset gambar lokal menjadi gambar absolut portal induk
        raw_content = re.sub(r'src=[\"\'](/web/image/[^\"\']+)[\"\']', r'src="https://www.iainpare.ac.id\1"', raw_content)
        # Bersihkan elemen komentar kosong
        raw_content = re.sub(r'<div[^>]+id=[\"\']o_wblog_post_comments[\"\'][^>]*>.*?</div>', '', raw_content, flags=re.DOTALL)
        data['content'] = raw_content.strip()
    else:
        data['content'] = f"<p>{data['name']}</p>"

    # 5. Subtitle (ekstrak 150 karakter teks pertama)
    clean_text = re.sub(r'<[^>]+>', ' ', data['content'])
    clean_text = ' '.join(clean_text.split())
    data['subtitle'] = clean_text[:160] + ('...' if len(clean_text) > 160 else '')

    return data

def ingest_to_odoo(articles, limit=None):
    """
    Ingest artikel langsung via Odoo ORM Environment
    """
    import odoo
    from odoo.modules.registry import Registry
    from odoo import api, SUPERUSER_ID

    odoo.tools.config.parse_config(['-d', 'app-my'])
    registry = Registry('app-my')

    target_count = 0
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # 1. Pastikan Blog Khusus Ma'had Ada
        blog = env['blog.blog'].search([('name', '=', 'Kabar Ma\'had')], limit=1)
        if not blog:
            blog = env['blog.blog'].create({
                'name': 'Kabar Ma\'had',
                'subtitle': 'Dokumentasi, Pembinaan, & Syiar Ma\'had Al-Jami\'ah IAIN Parepare',
                'website_id': 2,
            })
            print(f"[+] Dibuat channel blog baru: {blog.name} (ID: {blog.id})")
        else:
            if blog.website_id.id != 2:
                blog.write({'website_id': 2})
            print(f"[*] Menggunakan channel blog: {blog.name} (ID: {blog.id})")

        items_to_process = articles[:limit] if limit else articles

        for idx, art in enumerate(items_to_process, 1):
            title = art['name']
            # Cek apakah artikel sudah ada untuk menghindari duplikasi
            existing = env['blog.post'].search([('name', '=', title)], limit=1)
            
            cover_props = {}
            if art.get('cover_image'):
                cover_props = {
                    'background-image': f"url('{art['cover_image']}')",
                    'background_color_class': 'o_cc1',
                    'opacity': '0.4',
                    'resize_class': 'cover'
                }

            vals = {
                'name': title,
                'subtitle': art.get('subtitle', ''),
                'blog_id': blog.id,
                'website_id': 2,
                'website_published': True,
                'content': art['content'],
                'cover_properties': json.dumps(cover_props) if cover_props else False,
            }
            if art.get('published_date'):
                vals['published_date'] = art['published_date']

            if existing:
                existing.write(vals)
                print(f"[{idx}/{len(items_to_process)}] [UPDATE] {title[:65]}...")
            else:
                new_post = env['blog.post'].create(vals)
                print(f"[{idx}/{len(items_to_process)}] [CREATE] {title[:65]}... (ID: {new_post.id})")
            target_count += 1

        cr.commit()
    print(f"\n[V] Sukses mengimpor {target_count} artikel ke portal https://mahad.iainpare.ac.id/blog!")

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'sample'
    urls = get_mahad_urls()
    
    if mode == 'sample':
        print(f"\n[*] Mode SAMPLE: Mengambil 5 artikel terbaru...")
        selected_urls = urls[:5]
    elif mode == 'full':
        print(f"\n[*] Mode FULL: Memproses semua {len(urls)} artikel...")
        selected_urls = urls
    else:
        try:
            count = int(mode)
            selected_urls = urls[:count]
            print(f"\n[*] Mode CUSTOM: Memproses {len(selected_urls)} artikel...")
        except ValueError:
            selected_urls = urls[:5]

    articles = []
    for u in selected_urls:
        print(f"-> Mengunduh artikel: {u}")
        art = extract_article(u)
        if art:
            articles.append(art)
        time.sleep(0.5) # Sopan terhadap server sumber

    print(f"\n[+] Berhasil mengekstrak {len(articles)} artikel lengkap.")
    print("[*] Memulai Ingestion ke Database Odoo...")
    ingest_to_odoo(articles)

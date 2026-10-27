import json
import re
import os

PORTFOLIO_PROD = r'C:\Users\ph238\.gemini\antigravity\scratch\portfolio-senai-prod'
RAW_FILE = r'C:\Users\ph238\.gemini\antigravity\scratch\senai_classroom_downloader\raw_classroom_data.json'
MAP_FILE = os.path.join(PORTFOLIO_PROD, 'download_map.json')
OUT_FILE = os.path.join(PORTFOLIO_PROD, 'portfolio_data.js')

with open(RAW_FILE, 'r', encoding='utf-8') as f:
    raw = json.load(f)

with open(MAP_FILE, 'r', encoding='utf-8') as f:
    downloaded_map = json.load(f)

CURRICULUM = [
    # 1º Semestre
    {"code": "N1I-COMEC", "name": "Comunicação Estratégica Corporativa", "hours": 90, "semester": 1, "icon": "chat-dots", "topic_hint": "COMEC"},
    {"code": "N1I-FDMT", "name": "Ferramentas Digitais para o Mercado de Trabalho", "hours": 60, "semester": 1, "icon": "laptop", "topic_hint": "FDMT"},
    {"code": "N1I-OREEM1", "name": "Organização e Estrutura Empresarial", "hours": 30, "semester": 1, "icon": "diagram-3", "topic_hint": "OREEM1"},
    {"code": "N1I-PERPP", "name": "Performance Pessoal e Profissional", "hours": 60, "semester": 1, "icon": "person-check", "topic_hint": "PERPP"},
    # 2º Semestre
    {"code": "N2I-CHDT1", "name": "Capital Humano e Desenvolvimento de Talentos", "hours": 90, "semester": 2, "icon": "people", "topic_hint": "CHDT1"},
    {"code": "N2I-LM", "name": "Linguagens em Multimeios", "hours": 60, "semester": 2, "icon": "collection-play", "topic_hint": "LM_"},
    {"code": "N2I-LOGIS1", "name": "Logística Integrada e Sustentável", "hours": 105, "semester": 2, "icon": "box-seam", "topic_hint": "LOGIS1"},
    {"code": "N2I-OREEM2", "name": "Organização e Estrutura Empresarial", "hours": 45, "semester": 2, "icon": "buildings", "topic_hint": "OREEM2"},
    # 3º Semestre
    {"code": "N3I-APRIP1", "name": "Aprimoramento de Processos", "hours": 75, "semester": 3, "icon": "gear-wide-connected", "topic_hint": "APRIP1"},
    {"code": "N3I-CHDT2", "name": "Capital Humano e Desenvolvimento de Talentos", "hours": 105, "semester": 3, "icon": "person-plus", "topic_hint": "CHDT2"},
    {"code": "N3I-FIINT1", "name": "Finanças Integradas", "hours": 75, "semester": 3, "icon": "currency-dollar", "topic_hint": "FIINT1"},
    {"code": "N3I-LOGIS2", "name": "Logística Integrada e Sustentável", "hours": 45, "semester": 3, "icon": "truck", "topic_hint": "LOGIS2"},
    # 4º Semestre
    {"code": "N4I-APRIP2", "name": "Aprimoramento de Processos", "hours": 120, "semester": 4, "icon": "speedometer2", "topic_hint": "APRIP2"},
    {"code": "N4I-FIINT2", "name": "Finanças Integradas", "hours": 105, "semester": 4, "icon": "cash-coin", "topic_hint": "FIINT2"},
    {"code": "N4I-TIN1", "name": "Tendências e Inovações", "hours": 75, "semester": 4, "icon": "lightbulb", "topic_hint": "TIN1"},
    # Projetos Transversais
    {"code": "PROJ-DESK", "name": "Projeto - Desktop x SENAI", "hours": 40, "semester": 1, "icon": "rocket-takeoff", "topic_hint": "Desktop"},
    {"code": "TRANSV", "name": "Temas Transversais", "hours": 40, "semester": 1, "icon": "globe-americas", "topic_hint": "Transversais"},
]

topic_id_to_curriculum = {}
for t in raw['topics']:
    tname = t['name']
    matched = None
    for c in CURRICULUM:
        if c['topic_hint'] in tname:
            matched = c
            break
    if matched:
        topic_id_to_curriculum[t['topicId']] = matched['code']

def parse_attachments(materials_list):
    res = []
    for m in materials_list:
        if 'driveFile' in m:
            df = m['driveFile'].get('driveFile', {})
            title = df.get('title', 'Arquivo')
            fid = df.get('id', '')
            ext = title.split('.')[-1].lower() if '.' in title else ''

            ftype = 'file'
            if ext in ['pdf']:
                ftype = 'pdf'
            elif ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg']:
                ftype = 'image'

            # Link local baixado fisicamente
            local_rel_path = downloaded_map.get(fid, '')
            if local_rel_path:
                download_url = local_rel_path
                preview_url = local_rel_path
                # se o arquivo exportado foi convertido para PDF
                if local_rel_path.endswith('.pdf'):
                    ftype = 'pdf'
            else:
                download_url = f"https://drive.google.com/uc?export=download&id={fid}"
                preview_url = f"https://drive.google.com/file/d/{fid}/preview"

            res.append({
                'title': title,
                'url': download_url,
                'preview_url': preview_url,
                'download_url': download_url,
                'type': ftype,
                'is_local': bool(local_rel_path),
                'file_id': fid
            })
        elif 'link' in m:
            lk = m['link']
            res.append({
                'title': lk.get('title', lk.get('url', 'Link Externo')),
                'url': lk.get('url', ''),
                'preview_url': lk.get('url', ''),
                'download_url': lk.get('url', ''),
                'type': 'link',
                'is_local': False
            })
        elif 'youtubeVideo' in m:
            yt = m['youtubeVideo']
            vid_id = yt.get('id', '')
            res.append({
                'title': yt.get('title', 'Vídeo YouTube'),
                'url': yt.get('alternateLink', ''),
                'preview_url': f"https://www.youtube.com/embed/{vid_id}" if vid_id else yt.get('alternateLink', ''),
                'download_url': yt.get('alternateLink', ''),
                'type': 'video',
                'is_local': False
            })
    return res

components_dict = {c['code']: {**c, 'contents': {}} for c in CURRICULUM}

def process_item(item, item_type):
    topic_id = item.get('topicId')
    code = topic_id_to_curriculum.get(topic_id)
    if not code:
        return

    title = item.get('title', 'Sem título')
    desc = item.get('description', '')
    materials = parse_attachments(item.get('materials', []))
    update_time = item.get('updateTime', item.get('creationTime', ''))
    due_date = item.get('dueDate')

    content_name = "Conteúdos & Situações de Aprendizagem"
    m_match = re.search(r'(S\d+[_ -][^\n\r]+)', title)
    if m_match:
        content_name = m_match.group(1).split('-')[0].replace('_', ' ').strip()
    elif 'EAD' in title:
        content_name = "Cursos e Aulas EAD"
    elif 'Cronograma' in title or 'Plano' in title:
        content_name = "Planejamento e Cronograma"

    item_obj = {
        'id': item.get('id'),
        'title': title,
        'description': desc,
        'type': item_type,
        'date': update_time[:10] if update_time else '',
        'due_date': due_date,
        'attachments': materials
    }

    comp = components_dict[code]
    if content_name not in comp['contents']:
        comp['contents'][content_name] = {
            'title': content_name,
            'description': f"Tópicos de estudo e atividades práticas de {content_name}.",
            'activities': []
        }
    comp['contents'][content_name]['activities'].append(item_obj)

for m in raw['materials']:
    process_item(m, 'Material Didático')

for w in raw['courseWork']:
    process_item(w, 'Atividade Prática / Trabalho')

final_components = []
for c in CURRICULUM:
    code = c['code']
    data = components_dict[code]
    contents_list = []
    total_acts = 0
    total_files = 0
    total_pdfs = 0
    total_images = 0

    for cname, cdata in data['contents'].items():
        total_acts += len(cdata['activities'])
        for act in cdata['activities']:
            total_files += len(act['attachments'])
            for att in act['attachments']:
                if att['type'] == 'pdf':
                    total_pdfs += 1
                elif att['type'] == 'image':
                    total_images += 1
        contents_list.append(cdata)

    data['contents'] = contents_list
    data['stats'] = {
        'activities': total_acts,
        'files': total_files,
        'pdfs': total_pdfs,
        'images': total_images
    }
    final_components.append(data)

js_content = "window.PORTFOLIO_DATA = " + json.dumps(final_components, ensure_ascii=False, indent=2) + ";"
with open(OUT_FILE, 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"[✔] portfolio_data.js gerado com sucesso em: {OUT_FILE}")

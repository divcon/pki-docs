"""Build offline print handbooks and synchronize call numbers in Markdown.
Run: python3 root-key-design/ceremony/root-first-001/print/build.py
Requires markdown-it-py already available in the documentation environment.
No network, remote assets, or operational ceremony actions.
"""
from pathlib import Path
import re, json, html, hashlib
from markdown_it import MarkdownIt

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
raw_sequence=json.loads((HERE/'sequence.json').read_text())
PHASES=[f'S0{i}' for i in range(8)]
if set(raw_sequence) != set(PHASES):
 raise ValueError('Expected exactly S00–S07; missing or unknown phase')
# JSON insertion order must never determine the phase title or record filename.
SEQ={phase:raw_sequence[phase] for phase in PHASES}
for phase,rows in SEQ.items():
 if [row['id'] for row in rows] != [f'{phase}.{i}' for i in range(1,len(rows)+1)]:
  raise ValueError(f'Invalid call order in {phase}')
ROLES={'Administrator':'administrator','Crypto Officer':'crypto-officer','Key Custodian 2':'key-custodian-2','Key Custodian 3':'key-custodian-3','Independent Witness':'independent-witness'}
MATERIALS=json.loads((HERE/'s00-materials.json').read_text())
FILES=['s00-start.md','s01-root-key.md','s02-root-certificate.md','s03-first-key.md','s04-first-csr.md','s05-first-certificate.md','s06-verification.md','s07-handover.md']
NAMES=['시작 확인','Root 키 생성','Root 자기서명 인증서 발급','First ICA 키 생성','First CSR 생성','First 인증서 발급','전체 결과와 수행 확인 서명','운영 인계와 접근 종료']
BEGIN='<!-- PRINT CALLS BEGIN -->';END='<!-- PRINT CALLS END -->'
def marked(text,content):
 block=BEGIN+'\n'+content.strip()+'\n'+END
 if BEGIN in text:return re.sub(re.escape(BEGIN)+r'.*?'+re.escape(END),lambda _:block,text,flags=re.S)
 return block+'\n\n'+text

def own(row,role):
 out=[]
 if role in row['tasks']:out.append(row['tasks'][role])
 if role=='Crypto Officer' and 'Key Custodian 1' in row['tasks']:out.append('Key Custodian 1로서: '+row['tasks']['Key Custodian 1'])
 return ' '.join(out)

def record_items(row,role):
 return row.get('records',{}).get(role,[row['record']])

def s00_materials():
 text='### S00에서 펼칠 자료\n\n자료 1–5는 Administrator가 탭을 붙여 둔 실제 승인/근거 자료입니다. 출력된 설계 초안 자체를 준비 완료 증거로 사용하지 않습니다.\n\n| 자료 | 제시자·내용 | 확인 기준 |\n|---|---|---|\n'
 for item in MATERIALS:
  text+=f'| {item["id"]} — {item["title"]} | {item["presenter"]}. {item["contents"]} | {item["pass"]} |\n'
 return text

def s00_controls():
 text='### S00 호출·진행 판정\n\n여러 사람이 있는 호출은 본인 기록 후 완료를 보고합니다. Administrator는 모든 필수 확인을 대조해 다음 번호를 부릅니다. S00.5는 입회 이견 보고 → Administrator 선언 → Witness의 실제 선언 기록 → 다음 이동 순서입니다.\n\n'
 for row in SEQ['S00']:
  text+=f'**{row["id"]} 진행자 발언**\n\n> {row["prompt"]}\n\n- **다음 호출 조건:** {row["advance"]}\n- **보류·중단:** {row["stop"]}\n\n'
 return text

def calls_md(phase,role=None):
 if role:
  s='| 호출 번호 | 내 상태·할 일 | 종이 기록 위치 |\n|---|---|---|\n'
  for row in SEQ[phase]:
   task=own(row,role)
   if task:state='**수행** — '+task;loc=f'{row["id"]} / '+('Key Custodian 1' if role=='Crypto Officer' and 'Key Custodian 1' in row['tasks'] and 'Crypto Officer' not in row['tasks'] else role)
   elif role=='Independent Witness':state='**계속 관찰** — 이 순서의 실제 수행·일탈 확인.';loc=f'기록지 {phase} / 단계 마감의 입회란'
   elif role=='Administrator':state='**진행** — 담당자를 호출하고 완료 보고를 받는다.';loc='새 결과가 없으면 추가 기입 없음'
   else:state='**대기** — 다음 본인 호출을 기다린다.';loc='기입 없음'
   s+=f'| **{row["id"]}** | {state} | {loc} |\n'
  return s
 s='| 호출 번호 | 지금 할 일·담당자 | 기록할 것 |\n|---|---|---|\n'
 for row in SEQ[phase]:
  grouped={}
  for r,t in row['tasks'].items():grouped.setdefault(t,[]).append(r)
  actions='<br>'.join('**'+', '.join(rs)+'**: '+t for t,rs in grouped.items())
  record_text='각자 이름이 표시된 항목별 칸에 기록' if 'records' in row else row['record']
  s+=f'| **{row["id"]} {row["title"]}** | {actions} | 기록지 {phase} / **{row["id"]}**의 본인 칸 — {record_text} |\n'
 return s

# Synchronize paper navigation into existing source documents, preserve detailed criteria.
p=BASE/'script.md';s=p.read_text()
for i,phase in enumerate(SEQ):
 a=s.index('## '+phase+' ');z=s.find('\n## ',a+3);z=len(s) if z<0 else z
 block=s[a:z];heading=block.splitlines()[0];gate='\n'.join(x for x in block.splitlines() if x.startswith('- **통과 조건:'))
 declaration='\n> 행사 {{행사_ID}}의 시작 조건을 확인하여 S01 Root 키 생성을 시작합니다.\n' if i==0 else ''
 new=heading+f'\n\n**전원: 자기 책자의 {phase}을 펴세요. 기록지 {phase}을 공용 기록대에 놓습니다.** 진행자는 아래 번호를 한 번에 하나씩 부르고, 담당자 완료 보고와 필요한 검증 후 다음 번호로 갑니다. Independent Witness는 단계 시작부터 끝까지 관찰합니다.\n\n'+calls_md(phase)+'\n'+(s00_controls() if phase=='S00' else '')+declaration+'\n'+gate+'\n'
 s=s[:a]+new+s[z:]
intro='''## 종이로 진행하는 방법

- 진행자는 “S01.2, 생성 계획 승인”처럼 **단계·호출 번호·업무**를 소리 내어 알리고 현재 번호를 공용 진행판에 표시합니다.
- 각자는 자기 가이드의 같은 단계에서 번호를 찾습니다. **수행 / 대기 / 계속 관찰** 표시를 따릅니다. 단순히 다음 페이지를 넘겼다고 실행하지 않습니다.
- 기록 원본은 단계별 **한 묶음**만 사용합니다. 공용 기록대에서 해당 작성자가 같은 번호의 본인 칸에 직접 기록하고 돌려놓습니다. 개인 책자 메모는 공식 기록을 대신하지 않습니다.
- 종이 확인은 실제 행위와 근거의 기록입니다. 생성 계획/토큰의 **전자서명은 승인된 장치·앱으로 별도 수행**합니다. 개인별 노트북이 있다고 가정하지 않으며, 장치 배정은 승인 실행 환경을 따릅니다.
- 값·검사 자료·출력 원문은 사전 배부한 자료 묶음이나 승인된 작업 화면으로 제시합니다. 인쇄본만으로 미확정 명령·설정을 대신하지 않습니다. 중단은 누구나 요청할 수 있고 재실행은 임의로 하지 않습니다.

'''
if '## 종이로 진행하는 방법' not in s:s=s.replace('## 당일 사용할 설정과 실행 절차',intro+'## 당일 사용할 설정과 실행 절차')
p.write_text(s)
for role,stem in ROLES.items():
 p=BASE/'guides'/f'{stem}.md';s=p.read_text()
 for phase in SEQ:
  a=s.index('## '+phase+'\n');z=s.find('\n## ',a+3);z=len(s) if z<0 else z
  block=s[a:z];body=block[len('## '+phase+'\n'):].strip()
  content=f'**현재 단계: {phase} / 내 담당: {role}**\n\n진행자가 부른 번호의 행을 보세요. 기록은 공용 **기록지 {phase} → 같은 호출 번호 → 본인 칸**에 남깁니다.\n\n'+calls_md(phase,role)
  body=marked(body,content)
  if phase=='S00':
   body=re.sub(r'### S00에서 펼칠 자료.*',lambda _:s00_materials(),body,flags=re.S)
  # The printed sequence table and existing detailed checks remain adjacent.
  s=s[:a]+'## '+phase+'\n\n'+body+'\n'+s[z:]
 p.write_text(s)
for i,phase in enumerate(SEQ):
 p=BASE/'records'/FILES[i];s=p.read_text()
 content=f'''## 인쇄 기록 위치

**기록지 {phase}** · 행사/회차: __________ · 승인본: __________ · 원본 묶음 번호: __________

종이 행사에서는 인쇄 묶음의 아래 호출 번호·담당자 칸에 한 번 작성합니다. 이 파일의 기존 세부 항목은 첨부 근거의 확인 기준으로 사용하며 같은 결과를 두 번 쓰지 않습니다. 긴 실제 값·서명·로그는 증거 번호로 연결하고 공용 원본에 첨부 목록을 남깁니다.

| 호출 번호 | 작성할 담당자 | 기록 내용 |
|---|---|---|
'''
 for row in SEQ[phase]:
  if 'records' in row:
   for role in row['tasks']:
    content+=f'| **{row["id"]}** | {role} | '+' / '.join(record_items(row,role))+' |\n'
  else:content+=f'| **{row["id"]}** | '+', '.join(row['tasks'])+' | '+row['record']+' |\n'
 # Insert at the end to preserve the original document title at top; HTML presents forms separately.
 if BEGIN in s:s=marked(s,content)
 else:s=s.rstrip()+'\n\n'+marked('',content)+'\n'
 p.write_text(s)

# Static, self-contained HTML. Links become printed words; appendices have explicit binder labels.
md=MarkdownIt('commonmark').enable('table')
label_map={'settings.md':'별책「승인 설정」','runbook.md':'별책「실행 절차」','preparation.md':'별책「시작 전 준비 확인」','evidence-index.md':'별책「증거 목록」','README.md':'책자 앞면의 역할 규칙','hold-resume.md':'공용 기록지「보류·재개」','management-change.md':'공용 기록지「관리 변경」'}
def paper_md(text):
 text=re.sub(r'<!--.*?-->', '',text,flags=re.S)
 def link(m):
  label,url=m.group(1),m.group(2)
  name=url.split('#')[0].split('/')[-1]
  if name in FILES:return f'{label} — 기록지 S0{FILES.index(name)}'
  if name in label_map:return f'{label} — {label_map[name]}'
  if url.startswith('http'):return label+' (근거 원문 식별은 승인 자료 묶음에 보관)'
  return label
 text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,text)
 rendered=md.render(text)
 return re.sub(r'<a\b[^>]*>(.*?)</a>',r'\1',rendered,flags=re.S)
CSS='''
@page {size:A4;margin:14mm 13mm;}
* {box-sizing:border-box} body {font-family:"Malgun Gothic","Apple SD Gothic Neo","Noto Sans CJK KR",sans-serif;color:#111;margin:0;font-size:10.5pt;line-height:1.55;background:#eee;word-break:keep-all;overflow-wrap:anywhere}
.sheet {background:white;max-width:210mm;margin:7mm auto;padding:13mm;break-before:page} .sheet:first-child {break-before:auto}
h1 {font-size:20pt;line-height:1.3;margin:0 0 5mm}h2 {font-size:14pt;margin:5mm 0 3mm}h3 {font-size:11pt;margin:4mm 0 2mm}
.banner {border:2px solid #222;padding:3mm;font-size:13pt;font-weight:bold;margin-bottom:4mm}.meta {font-size:9pt;color:#444;border-bottom:1px solid #777;padding-bottom:2mm;margin-bottom:4mm}
table {width:100%;border-collapse:collapse;margin:3mm 0;font-size:9.5pt;table-layout:fixed}th,td {border:1px solid #777;padding:2mm;vertical-align:top}th {background:#eee;text-align:left}thead {display:table-header-group}tr {break-inside:avoid}p,li {orphans:3;widows:3}pre {white-space:pre-wrap;font-size:8pt}code {font-family:inherit;font-size:.94em}blockquote {border-left:4px solid #777;margin:3mm 0;padding-left:3mm}
.calls th:first-child,.calls td:first-child{width:22%}.calls td:last-child{width:26%}.form {border:1.2px solid #333;padding:3mm;margin:4mm 0;break-inside:avoid;min-height:40mm}.form h3{margin:0 0 2mm;font-size:11pt}.blank{min-height:14mm;border-bottom:1px dotted #777}.signature{font-size:9pt;margin-top:2mm}.notice{border:1px solid #555;padding:3mm;margin:4mm 0;font-weight:bold}.screen{max-width:210mm;margin:5mm auto;padding:5mm;background:#fff} .fine{font-size:9pt}.large{font-size:23pt;border-bottom:2px solid #333;padding:7mm 0}
.field{font-size:9.5pt;margin-top:2mm}.write-line{min-height:8mm;border-bottom:1px dotted #777}
@media print {body{background:white}.sheet{max-width:none;margin:0;padding:0}.screen{display:none}a {color:inherit;text-decoration:none}}
'''
# Reproducible build identifier; templates remain explicitly unapproved.
sources=[BASE/'script.md',*sorted((BASE/'guides').glob('*.md')),*sorted((BASE/'records').glob('*.md')),BASE/'settings.md',BASE/'runbook.md',BASE/'preparation.md',BASE/'evidence-index.md',BASE.parent/'cloudhsm-options.md',HERE/'sequence.json',HERE/'s00-materials.json',Path(__file__)]
manifest={str(p.relative_to(BASE)) if p.is_relative_to(BASE) else '../'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
REV=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()[:12]

def sheet(code,title,content):return f'<section class="sheet"><div class="meta">root-first-001 · 인쇄 초안 {REV} · 미승인 · {html.escape(code)}</div><div class="banner">{html.escape(code)}</div><h1>{html.escape(title)}</h1>{content}</section>'
def write(name,title,parts):
 data='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>'+CSS+'</style></head><body><div class="screen">오프라인 인쇄본 · 브라우저에서 A4 / 배율 100% / 머리글·바닥글 끄기로 인쇄하세요. 현재 파일 안에 본문과 스타일이 포함되어 있습니다. 초안이며 승인/리허설 완료를 뜻하지 않습니다.</div>'+''.join(parts)+'</body></html>'
 (HERE/name).write_text(data)
def section(src,heading):
 m=re.search(r'^## '+re.escape(heading)+r'\s*$',src,re.M)
 if not m:return ''
 end=re.search(r'^## ',src[m.end():],re.M)
 return src[m.end():m.end()+end.start() if end else len(src)].strip()
cover='''<p>자기 책자의 현재 단계만 펼칩니다. 진행자가 <b>“단계.번호, 업무”</b>를 부르면 해당 행을 찾습니다. 먼저 수행하지 않습니다.</p><p>공용 기록지의 <b>같은 번호·본인 이름 칸</b>에 직접 기록합니다. 끝나면 “S01.2, Key Custodian 2, 완료”처럼 번호·담당·결과를 말합니다. 이상은 즉시 중단 요청합니다.</p><p>입회자는 단계 전체를 관찰합니다. 대기 표시는 역할 해제나 퇴장을 뜻하지 않습니다. 단계 종료와 다음 단계 이동은 Administrator가 선언합니다.</p><div class="notice">종이 확인 서명은 생성 계획·HSM 토큰의 전자서명을 대신하지 않습니다. 개인 승인키는 승인된 장치에서 본인이 사용합니다.</div>'''
for role,stem in ROLES.items():
 src=(BASE/'guides'/f'{stem}.md').read_text()
 pre=src.split('## S00',1)[0]
 parts=[sheet(role+' · 사용법',role+' 인쇄 책자',cover+paper_md(pre))]
 for i,phase in enumerate(SEQ):
  body=section(src,phase)
  detail=re.sub(re.escape(BEGIN)+r'.*?'+re.escape(END),'',body,flags=re.S).strip()
  detail=re.sub(r'^\*\*기록:\*\*.*$', '기록은 앞면 호출표에 표시한 번호·본인 칸에 남깁니다.',detail,flags=re.M)
  detail=re.sub(r'^\d+\. ', '- ',detail,flags=re.M)
  detail='실행 순서는 앞면 호출 번호를 따릅니다. 아래는 해당 업무의 확인 기준입니다.\n\n'+detail
  parts.append(sheet(f'{role} · {phase} · 지금 할 일',NAMES[i],'<p>현재 호출 번호: __________　내 이름: __________</p><div class="calls">'+paper_md(calls_md(phase,role))+'</div><p class="fine">세부 검사 기준은 바로 다음 면의 같은 단계에 있습니다. 기록은 공용 기록지 '+phase+'에 남깁니다.</p>'))
  parts.append(sheet(f'{role} · {phase} · 세부 확인',NAMES[i]+' — 확인 기준',paper_md(detail)))
 parts.append(sheet(role+' · 보류·재개','중단했을 때',paper_md(section(src,'보류와 재개'))+'<p>공용 기록지 「보류·재개」를 사용합니다. 승인 없는 생성·서명·삭제를 하지 않습니다.</p>'))
 write(stem+'.html',role+' 인쇄 책자',parts)
# Facilitator: one call per event, no online navigation.
s=(BASE/'script.md').read_text();parts=[sheet('진행자 · 사용법','Root·First 세레모니 진행',cover+paper_md(s.split('## S00 시작 확인',1)[0]))]
for i,phase in enumerate(SEQ):
 parts.append(sheet('진행자 · '+phase,NAMES[i],'<p>“전원 '+phase+'을 펴세요. 현재 '+phase+'.1입니다.”라고 알립니다. 공용 진행판에 번호를 표시합니다.</p><div class="calls">'+paper_md(calls_md(phase))+'</div><p>번호 안에 둘 이상의 담당자가 있으면 표에 적힌 확인·실행 순서를 지킵니다. 단계 마감은 입회·필수 기록을 확인한 후 선언합니다. 통과 전 다음 단계로 넘기지 않습니다.</p>'))
 if phase=='S00':parts.append(sheet('진행자 · S00 · 발언과 통과 기준','S00 호출·진행 판정',paper_md(s00_controls())))
 if phase=='S00':parts.append(sheet('진행자 · S00 · 제시 자료','S00 자료 5종',paper_md(s00_materials())))
parts.append(sheet('진행자 · 보류·재개','중단·제한 재개',paper_md(section(s,'S00-R 백업·증거 대기 후 제한 재개')+'\n\n'+section(s,'중단과 재개'))))
write('facilitator.html','진행자 인쇄 대본',parts)
# Common paper originals: unambiguous, one field per call AND person, enough writing space.
parts=[sheet('공용 기록 원본 · 사용법','단계별 종이 기록지','''<p>단계마다 원본 한 묶음을 공용 기록대에 둡니다. 누구나 자기 책자를 보지만 기록 원본은 복제하지 않습니다. 각 담당자가 자기 칸에 직접 작성하고 완료를 보고합니다.</p><p>모든 면에 행사 ID·회차·원본 묶음 번호를 씁니다. 긴 해시·값·전자서명·원본 로그는 증거 번호를 적고 승인 저장소/첨부 목록에 연결합니다. 종이 서명으로 앱/HSM 전자서명을 대신하지 않습니다.</p><p>작성 내용: 결과·근거 자료 번호·실제 값 또는 첨부 참조·작성자·시각. 승인자는 승인/거부/미참여와 이유를 구분합니다. 공란을 통과로 처리하지 않습니다.</p><p>전자 원본은 계속 승인 시스템에 보존합니다. 종이 기록과 전자 원본의 수집·보관·스캔/인계는 승인된 보존 정책을 따릅니다.</p>''')]
for i,phase in enumerate(SEQ):
 entries=[(row,role) for row in SEQ[phase] for role in row['tasks']]
 chunk_size=1 if phase=='S00' else 4
 chunks=[entries[j:j+chunk_size] for j in range(0,len(entries),chunk_size)]
 for j,chunk in enumerate(chunks,1):
  content='<p>행사 ID: __________　회차: ______　원본 묶음: ______</p><p>승인본: __________　작성일/시간대: __________</p>'
  for row,role in chunk:
   if 'records' in row:
    fields=''.join('<div class="field">'+html.escape(label)+'<div class="write-line"></div></div>' for label in record_items(row,role))
   else:fields=f'<div class="fine">기록: {html.escape(row["record"])}</div><div class="blank">결과·실제 값·근거/첨부 번호:</div>'
   content+=f'<div class="form"><h3>{html.escape(row["id"])} — {html.escape(role)} / {html.escape(row["title"])}</h3>'+fields+'<div class="signature">이름/확인 서명: __________________　시각: __________</div></div>'
  parts.append(sheet(f'기록지 {phase} · {j}/{len(chunks)}',NAMES[i],content))
 # Explicit list of evidence references avoids conflating short paper entries and technical evidence.
 text=(BASE/'records'/FILES[i]).read_text().split(BEGIN)[0]
 criteria=section(text,'다음 단계 판정')
 content=paper_md(criteria.split('| 기록할 항목')[0])+'<p>단계 판정은 해당 마감 호출의 Administrator 칸에 기록합니다. 아래 목록은 실제 원문과 종이 기록을 연결합니다.</p><table><thead><tr><th>증거/첨부 번호</th><th>문서·파일·버전/해시·보관 위치</th><th>수집/확인자·시각</th></tr></thead><tbody>'+''.join('<tr style="height:18mm"><td></td><td></td><td></td></tr>' for _ in range(6))+'</tbody></table><p>원본 요청·응답·서명·검사 자료를 요약표로 대체하지 않습니다. 담당 가이드의 세부 확인 항목에 대한 실제 값은 첨부 자료로 연결합니다.</p>'
 if i==6:content+='<p>확인 서명은 고정한 대상 목록의 해시를 참조합니다. 고정 사본을 수정하지 않고 서명 파일·이후 확인 기록은 후속 자료로 보관합니다.</p>'
 parts.append(sheet(f'기록지 {phase} · 증거 목록·판정 기준',NAMES[i],content))
for fn,title in [('hold-resume.md','보류·재개'),('management-change.md','관리 변경')]:
 text=(BASE/'records'/fn).read_text();text=re.sub(r'\{\{[^}]+\}\}','________________',text)
 parts.append(sheet('공용 기록지 · '+title,title,paper_md(text)))
write('records.html','공용 기록 원본',parts)
# A display sheet can be placed where all participants can see the current step.
write('current-step.html','공용 진행판',[sheet('공용 진행판','지금 수행하는 순서','<div class="large">현재 단계: S____</div><div class="large">현재 호출: S____ . ____</div><div class="large">지금 담당: __________________</div><div class="large">상태: 진행 / 대기 / 중단</div><p>자기 책자의 같은 단계를 펴고 호출 번호를 찾으세요. 공용 기록지의 같은 번호·본인 칸에 작성하세요. 다음 순서는 Administrator가 선언합니다.</p>')])
# Full local references are bundled for printing, not fetched or treated as new factual sources.
refs=[('공통 역할 규칙',BASE/'guides/README.md'),('승인 설정',BASE/'settings.md'),('실행 절차',BASE/'runbook.md'),('시작 전 준비 확인',BASE/'preparation.md'),('증거 목록',BASE/'evidence-index.md'),('CloudHSM 실행 부록',BASE.parent/'cloudhsm-options.md')]
parts=[sheet('별책 · 준비와 사용','검증·실행에 필요한 자료','<p>Administrator와 Crypto Officer의 공용 별책입니다. 출력할 때 각 표지 제목으로 탭을 붙입니다. 당일에는 승인된 실제 설정·명령·시험 결과와 생성 계획/본문 내용표를 추가해 자료 번호를 부여합니다.</p><p>현재 포함한 문서는 설계 초안입니다. 빈 값·미구현 명령·미실시 시험을 완료한 것으로 사용하지 않습니다. 나머지 참여자는 자기 가이드와 진행자가 제시하는 해당 작업 자료를 사용합니다.</p>')]
for title,path in refs:parts.append(sheet('별책 · '+title,title,paper_md(path.read_text())))
write('reference.html','공용 검증·실행 별책',parts)
manifest['build_id']=REV
(HERE/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
# An index with local filenames is an offline selector, never a dependency during the ceremony.
links=[('facilitator.html','진행자 대본', 'Administrator 1부'),*[(stem+'.html',role+' 책자','해당 담당자 1부') for role,stem in ROLES.items()],('records.html','공용 기록 원본','단계별 원본 1묶음'),('current-step.html','공용 진행판','전체가 볼 수 있는 위치 1부'),('reference.html','공용 검증·실행 별책','Administrator·Crypto Officer 공용')]
index='<p>외부 연결 없이 파일을 열어 인쇄할 수 있습니다. 각 파일은 본문·스타일을 자체 포함합니다. 아래는 배부 목록이며 행사 중 링크를 누를 필요가 없습니다.</p><table><tr><th>인쇄할 묶음</th><th>배부</th></tr>'+''.join(f'<tr><td><a href="{f}">{t}</a><br><small>{f}</small></td><td>{who}</td></tr>' for f,t,who in links)+'</table><p>A4 · 배율 100% · 브라우저 머리글/바닥글 끄기. 한 단계의 「지금 할 일」과 「세부 확인」을 연속해서 묶고 탭을 붙이세요. 페이지가 이어지더라도 호출 번호와 기록지 번호로 찾습니다. 실제 인쇄 전 미리보기에서 줄 넘침과 필기 공간을 확인하세요.</p>'
write('index.html','오프라인 인쇄 묶음',[sheet('인쇄·배부 목록','세레모니 종이 진행 묶음',index)])
print(f'Generated offline HTML; build {REV}; {sum(map(len,SEQ.values()))} calls; {len(ROLES)} personal handbooks.')

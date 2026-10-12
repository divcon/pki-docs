"""Check generated phase/record alignment and offline dependencies; no HSM actions."""
from pathlib import Path
import hashlib
import html
import json
import re

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
# Independent expectations catch a swapped S02/S03 mapping in the generator.
PHASES = {
    'S00': ('시작 확인', 's00-start.md'),
    'S01': ('Root 키 생성', 's01-root-key.md'),
    'S02': ('Root 자기서명 인증서 발급', 's02-root-certificate.md'),
    'S03': ('First ICA 키 생성', 's03-first-key.md'),
    'S04': ('First CSR 생성', 's04-first-csr.md'),
    'S05': ('First 인증서 발급', 's05-first-certificate.md'),
    'S06': ('전체 결과와 수행 확인 서명', 's06-verification.md'),
    'S07': ('운영 인계와 접근 종료', 's07-handover.md'),
}
ROLES = {
    'Administrator': 'administrator', 'Crypto Officer': 'crypto-officer',
    'Key Custodian 2': 'key-custodian-2', 'Key Custodian 3': 'key-custodian-3',
    'Independent Witness': 'independent-witness',
}


def sections(path):
    return re.findall(r'<section class="sheet">(.*?)</section>', path.read_text(), re.S)


def plain(value):
    return html.unescape(re.sub(r'<[^>]+>', '', value))


def check_phase_titles(path):
    phases = []
    for part in sections(path):
        banner = re.search(r'<div class="banner">(.*?)</div>', part).group(1)
        phase = re.search(r'\bS0[0-7]\b', banner)
        if not phase:
            continue
        phase = phase.group()
        title = plain(re.search(r'<h1>(.*?)</h1>', part).group(1))
        if not any(x in banner for x in ('발언과 통과 기준', '제시 자료')):
            assert title in (PHASES[phase][0], PHASES[phase][0] + ' — 확인 기준'), (path.name, banner, title)
        if not phases or phases[-1] != phase:
            phases.append(phase)
        if banner.startswith('기록지 '):
            calls = re.findall(r'<h3>(S0\d\.\d+) —', part)
            assert all(call.startswith(phase + '.') for call in calls), (banner, calls)
    assert phases == list(PHASES), (path.name, phases)


def main():
    sequence = json.loads((HERE / 'sequence.json').read_text())
    records = (HERE / 'records.html').read_text()
    forms = re.findall(r'<div class="form"><h3>(.*?)</h3>(.*?)<div class="signature">', records, re.S)
    actual = {}
    for heading, body in forms:
        call, role = plain(heading).split(' / ', 1)[0].split(' — ', 1)
        assert (call, role) not in actual, ('Duplicate form', call, role)
        actual[call, role] = plain(body)
    expected = {(r['id'], role) for rows in sequence.values() for r in rows for role in r['tasks']}
    assert set(actual) == expected, ('Missing/extra forms', set(actual) ^ expected)
    for phase, (_, filename) in PHASES.items():
        text = (BASE / 'records' / filename).read_text().split('<!-- PRINT CALLS BEGIN -->')[1]
        calls = set(re.findall(r'\*\*(S0\d\.\d+)\*\*', text))
        assert calls == {r['id'] for r in sequence[phase]}, (filename, calls)
    for row in sequence['S00']:
        assert set(row['records']) == set(row['tasks']), row['id']
        assert all(row[k] for k in ('prompt', 'advance', 'stop'))
        for role, labels in row['records'].items():
            assert all(label in actual[row['id'], role] for label in labels), (row['id'], role)
    for name in ('facilitator', 'records', *ROLES.values()):
        check_phase_titles(HERE / (name + '.html'))
    for role, stem in ROLES.items():
        parts = sections(HERE / (stem + '.html'))
        first = next(p for p in parts if f'{role} · S00 · 지금 할 일</div>' in p)
        assert set(re.findall(r'<strong>(S00\.\d+)</strong>', first)) == {r['id'] for r in sequence['S00']}
    for path in HERE.glob('*.html'):
        content = path.read_text()
        assert not re.search(r'<script\b|<link\b|<iframe\b', content, re.I), path
        styles = '\n'.join(a + b for a, b in re.findall(r'<style>(.*?)</style>|style="([^"]*)"', content, re.S))
        assert not re.search(r'url\s*\(|@import', styles, re.I), path
        links = re.findall(r'(?:src|href)="([^"]+)"', content)
        assert path.name == 'index.html' or not links, (path, links)
        assert all('://' not in x and (HERE / x).is_file() for x in links), path
    manifest = json.loads((HERE / 'manifest.json').read_text())
    build_id = manifest.pop('build_id')
    assert hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()[:12] == build_id
    for name, digest in manifest.items():
        assert hashlib.sha256((BASE / name).read_bytes()).hexdigest() == digest, name
    assert all(build_id in p.read_text() for p in HERE.glob('*.html'))
    print(f'PASS: 8 phases, {sum(map(len, sequence.values()))} calls, {len(actual)} personal record slots; offline assets and source hashes match. Physical print layout not tested.')


if __name__ == '__main__':
    main()

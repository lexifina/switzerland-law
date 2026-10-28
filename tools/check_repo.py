"""Checks the git repository against the reader's data: every version of every article must be in git on the day it
took effect, and the version before it on the day before, so each change is in git on its own day and not a day early.

    python -X utf8 scripts/swiss-law/check_repo.py [--site saas-webpage] [--repo ../swiss-law] [--only 101,235.1]

The commit for a day is the newest commit to the act (merges skipped) whose author date, in its own time zone, is on
or before the day: the same rule tools/stand_am.py uses. Files are read through one `git cat-file --batch`.
"""
import argparse
import datetime as dt
import gzip
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def file_name(key: str) -> str:
    m = re.fullmatch(r'(\d+)([a-z]*)', key)
    return f'art-{int(m.group(1)):03d}{m.group(2)}.md' if m else f'{key}.md'


def body(md: str) -> str:
    lines = [l.strip() for l in md.split('\n')[1:] if l.strip()]
    return '\n'.join(re.sub(r'^(## |- )', '', l) for l in lines)


class Cat:
    def __init__(self, repo: str):
        self.p = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=repo, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def read(self, spec: str) -> str | None:
        self.p.stdin.write(spec.encode('utf-8') + b'\n')
        self.p.stdin.flush()
        header = self.p.stdout.readline().decode()
        if header.endswith('missing\n'):
            return None
        size = int(header.split()[2])
        data = self.p.stdout.read(size)
        self.p.stdout.read(1)
        return data.decode('utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--site', default=str(ROOT / 'saas-webpage'))
    ap.add_argument('--repo', default=str(ROOT.parent / 'swiss-law'))
    ap.add_argument('--only')
    args = ap.parse_args()
    data = Path(args.site) / 'app' / 'watch' / 'swiss-law' / '_data' / 'acts'
    only = set(args.only.split(',')) if args.only else None
    today = json.loads((data.parent / 'index.json').read_text(encoding='utf-8'))['built']
    cat = Cat(args.repo)
    checked = bad = 0
    for f in sorted(data.glob('*.json.gz')):
        slug = f.name[:-len('.json.gz')]
        if only and slug not in only:
            continue
        info = json.loads(gzip.decompress(f.read_bytes()))
        # Each branch's commits to this act, newest first, with the author's day.
        logs = {}
        for branch in ('main', 'future'):
            out = subprocess.run(['git', 'log', '--no-merges', '--format=%H %ad', '--date=format:%Y-%m-%d', branch, '--', slug],
                                 cwd=args.repo, capture_output=True, text=True)
            logs[branch] = [l.split() for l in out.stdout.splitlines()] if out.returncode == 0 else []

        def at(day: str, path: str) -> str | None:
            branch = 'future' if day > today and logs['future'] else 'main'
            commit = next((h for h, d in logs[branch] if d <= day), None)
            return cat.read(f'{commit}:{path}') if commit else None
        # Every article on every day a consolidated version applies from, so a version that changed nothing (or only a
        # heading) is checked against the latest commit up to that day, not only the days a commit was made.
        for cons in info['versions']:
            day = cons['from']
            for key, u in info['units'].items():
                want = next((v for v in reversed(u['versions']) if v['from'] <= day), None)
                if want is None:
                    continue
                got = at(day, f'{slug}/{file_name(key)}')
                checked += 1
                text = '\n'.join(''.join(r[0] for r in line) for line in want['runs'])
                ok = got is None if want['repealed'] else got is not None and body(got) == text.strip()
                if not ok:
                    bad += 1
                    if bad <= 10:
                        print(f'MISMATCH {slug} {key} on version {day}: {(got or "")[:120]!r}')
        for key, u in info['units'].items():
            path = f'{slug}/{file_name(key)}'
            vs = u['versions']
            for i, v in enumerate(vs):
                checks = [(v['from'], v)]
                if i:
                    before = (dt.date.fromisoformat(v['from']) - dt.timedelta(days=1)).isoformat()
                    if before >= vs[i - 1]['from']:
                        checks.append((before, vs[i - 1]))
                for day, want in checks:
                    got = at(day, path)
                    checked += 1
                    text = '\n'.join(''.join(r[0] for r in line) for line in want['runs'])
                    ok = got is None if want['repealed'] else got is not None and body(got) == text.strip()
                    if not ok:
                        bad += 1
                        if bad <= 10:
                            print(f'MISMATCH {slug} {key} {day}: {(got or "")[:120]!r}')
    print(f'{checked} checks (every article on every consolidated version\'s day; each change on its day and the day before), {bad} mismatches')
    raise SystemExit(1 if bad else 0)


if __name__ == '__main__':
    main()

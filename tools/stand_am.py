"""Prints an act, or one article of it, as it stood on a given day, from this repository's history.

    python tools/stand_am.py 2021-06-01 101 197      # Art. 197 of the Constitution (SR 101) on 1 June 2021
    python tools/stand_am.py 2024-07-01 281.1        # every article of the SchKG (SR 281.1) in force on 1 July 2024

Each commit is dated the day its change took effect, so the text in force on a day is the last commit on or before
it. Changes adopted but not yet in force are on the branch "future"; a date after today reads from there.
"""
import datetime as dt
import re
import subprocess
import sys


def git(*args: str) -> str:
    return subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8', check=True).stdout


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    day, act = sys.argv[1], sys.argv[2]
    dt.date.fromisoformat(day)
    branch = 'future' if day > dt.date.today().isoformat() and git('branch', '--list', 'future').strip() else 'main'
    # Commits are dated noon in Zurich on the day a change took effect. Read each commit's day in its own time zone
    # and take the newest on or before the day asked for. Merges are skipped: the merge of main into future is
    # dated the build day but already holds the later changes.
    commit = ''
    for line in git('log', '--no-merges', '--format=%H %ad', '--date=format:%Y-%m-%d', branch, '--', act).splitlines():
        h, d = line.split()
        if d <= day:
            commit = h
            break
    if not commit:
        sys.exit(f'{act} is not in the record on {day}.')
    if len(sys.argv) > 3:
        key = sys.argv[3]
        m = re.fullmatch(r'(\d+)([a-z]*)', key)
        name = f'art-{int(m.group(1)):03d}{m.group(2)}.md' if m else f'{key}.md'
        try:
            print(git('show', f'{commit}:{act}/{name}'))
        except subprocess.CalledProcessError:
            sys.exit(f'Art. {key} was not in force on {day}.')
        return
    files = [f for f in git('ls-tree', '--name-only', commit, f'{act}/').split() if f.endswith('.md') and not f.endswith('README.md')]
    for f in files:
        print(git('show', f'{commit}:{f}'))


if __name__ == '__main__':
    main()

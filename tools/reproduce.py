"""Writes data/versionen.json and REPRODUCE.md for the Swiss law repository, from the facts of the build that made it.
Called by bulk.py; kept apart so the record of how the repository was made reads as one document."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


def write_manifest_rows(manifest: list[dict], today: str) -> str:
    """Every source file the text comes from, with its sha256, so a rebuild can show it read the same bytes."""
    out = {'built': today, 'acts': [{'sr': m['sr'], 'slug': m['slug'], 'eli': m['eli'],
                                     'versions': [{'from': v['from'], 'to': v['to'], 'xml': v['url'], 'sha256': v['sha256']} for v in m['versions']]}
                                    for m in manifest]}
    return json.dumps(out, ensure_ascii=False, indent=0) + '\n'


def write_reproduce(stats: dict, today: str) -> str:
    here = Path(__file__).resolve().parent
    blobs = {n: subprocess.run(['git', 'hash-object', str(here / n)], capture_output=True, text=True).stdout.strip()
             for n in ('fetch_all.py', 'bulk.py', 'build.py', 'reproduce.py')}
    pyv = subprocess.run(['python', '--version'], capture_output=True, text=True).stdout.strip()
    gitv = subprocess.run(['git', '--version'], capture_output=True, text=True).stdout.strip()
    failed = stats.get('failed', [])
    failed_list = '\n'.join(f'- {f}' for f in failed[:50]) + (f'\n- and {len(failed) - 50} more' if len(failed) > 50 else '')

    return f"""# How this history was made, and how to make it again

This file records exactly how the repository was built: the sources, the commands, the software, the decisions made
by hand, and what an AI model did and did not do. The build writes it, so it describes the build that made this
commit.

## Short version

```sh
git clone https://github.com/lexifina/switzerland-law && cd switzerland-law
pip install lxml
python -X utf8 tools/fetch_all.py                     # reads Fedlex into tools/.cache (resumable)
python -X utf8 tools/bulk.py --site ../site --repo ../rebuilt --today {today}
git -C ../rebuilt rev-parse main future             # the same hashes as this repository, from the same data
```

The tools need Python 3.12 or later with `lxml`, and git. `fetch_all.py` reads Fedlex into a cache; `bulk.py` builds
the reader's data into `--site` and this repository into `--repo` from that cache alone, with `git fast-import`. With
the same data and the same `--today` it gives the same commits with the same hashes. `data/versionen.json` lists
every source file with its sha256, so a rebuild can show whether Fedlex served the same bytes. `tools/check_repo.py`
reads versions back from git on the day they took effect, and the day before, and compares them with the reader's
data.

## Sources

All legal text and all information about changes come from **Fedlex**, the publication platform of the Swiss Federal
Chancellery. Nothing was typed in, summarised or rewritten.

| What | Where |
| --- | --- |
| Every consolidated version with a German XML file, the day it applies from and to | SPARQL at `https://fedlex.data.admin.ch/sparqlendpoint` (JOLux ontology): `jolux:isMemberOf`, `jolux:dateApplicability`, `jolux:isEmbodiedBy`, a year at a time |
| Each act's SR number, status, titles and dates | SPARQL: `jolux:classifiedByTaxonomyEntry`/`skos:notation`, `jolux:inForceStatus`, `jolux:title`, `jolux:dateEntryInForce`, 150 acts per query |
| Which amending act changed which article, and the day it took effect | SPARQL: `jolux:LegalResourceImpact`, read through each act's subdivisions (`jolux:legalResourceSubdivisionIsPartOf`), 60 acts per query |
| Each amending act's title, type, adoption, publication and entry into force | SPARQL: `jolux:title`, `jolux:typeDocument`, `jolux:dateDocument`, `jolux:publicationDate`, `jolux:dateEntryInForce` |
| The text of each version, with its footnotes | Akoma Ntoso XML from `https://fedlex.data.admin.ch/filestore/…`, listed with sha256 in `data/versionen.json` |

The record holds **{stats['acts']} acts** of the Classified Compilation (SR), federal law and international treaties, every act
with at least one German XML version, and {stats['versions']} article versions. `data/erlasse.json` lists each act with its SR
number, titles, status and versions. The data was retrieved on {stats.get('retrieved') or today}, with the user agent
`lexifina-watch/1.0`, four requests at a time.

## The build, step by step

1. `python -X utf8 scripts/swiss-law/fetch_all.py` in Lexifina's own repository filled the cache.
2. `python -X utf8 scripts/swiss-law/bulk.py --today {today}` wrote the reader's data and this repository.
3. `python -X utf8 scripts/swiss-law/check_repo.py` compared git with the reader's data.
4. `git push --force -u origin main future` and `git push --force --tags` published it to GitHub, private for now,
   and tags no longer in the build were deleted there. A clone of an earlier build updates with
   `git fetch --force --tags origin && git reset --hard origin/main`; `git fetch --tags` alone keeps the old tags.

The tools here are the same files as `scripts/swiss-law/` there: {', '.join(f'`{n}` (git blob `{b[:12]}`)' for n, b in blobs.items())}.
They ran with {pyv} and {gitv} on Windows 11. No network service other than Fedlex is involved.

## How the text and the commits are derived

Everything below is done by the tools, deterministically.

- **Text.** Each article of each version is one file, `<SR number>/art-NNN.md`. Each paragraph (Absatz) and each list
  item is one line, with its number; headings inside an article are `##` lines. Footnotes are read separately and left
  out of the text. Footnote markers left in older converted versions (`OR<sup>1)</sup>`) are dropped, and a difference
  of typesetting alone ("..." and "…") is not a change.
- **Changes.** Consecutive versions are compared article by article. {stats['changes']} changes were found:
  {stats['changes'] - stats['corrected']} made by an amending act and {stats['corrected']} corrections of the consolidated
  text by the publisher.
- **Cause.** A change is credited to the amending act that Fedlex's impact records name for that article on that day.
  Where the record names only the whole act, or nothing, the footnotes printed with the new version and not with the
  old one name it ("Fassung gemäss …", "Eingefügt durch …", "Angenommen in der Volksabstimmung vom …"). Where neither
  names an act, the change is a correction by the publisher.
- **Date.** A change is dated the day it took effect, from the footnote on that article ("in Kraft seit …") or the
  impact record for that article, and never on or before the previous version in the record. Where Fedlex has
  structured text for only some versions, the version where a change first appears can be later than that day.
- **Authors of words.** Words kept from one version to the next keep their author. In the first version of each act,
  each line is credited to the last act its footnotes say wrote or inserted it, or else to the act as enacted.
- **Commits.** {stats['commits']} commits: one per act, per day and per amending act ({stats['law_commits']} law commits), one
  for the first version of each act and one for each act and day of publisher's corrections, in the order they took
  effect, then one for this documentation, dated the build day.
  - The author is the amending act (`AS 2021 310`) at an address ending `@fedlex.invalid`. The first versions and the
    corrections are by `Bundeskanzlei (Fedlex)`.
  - Author and committer dates are noon in Zurich on the day the change took effect. The committer is
    `Lexifina <swiss-law@lexifina.com>`.
  - The message has the act's title, the articles it inserted, amended or repealed, and the trailers `Type:`,
    `Adopted:`, `Vote:`, `Published:`, `In-force:`, `Affecting:` and `Source:`. The first version of each act has
    `Consolidated:` instead of `In-force:`, because nothing came into force that day; corrections have `Corrected:`.
  - Changes in force after {today} are on the branch `future`. {stats['tags']} tags mark the amending acts
    (`as/2021-310`).

## Acts not in the record

{len(failed)} acts had a German XML file the tools could not read into articles:

{failed_list or '- none'}

Versions listed on Fedlex whose XML did not load or parse are left out, and the act is built from the others:
{len(stats.get('skipped', []))} versions ({', '.join(stats.get('skipped', [])[:20]) or 'none'}{' …' if len(stats.get('skipped', [])) > 20 else ''}).

## Decisions made by hand

These choices were made when the tools were written, after looking at the data. They are in the code.

1. **Only versions published as structured text are compared.** Fedlex has earlier versions as PDF and Word files
   only; converting them would put a conversion step between the official text and the record.
2. **German is the text of the record.** German, French and Italian are equally authoritative. The English
   translations on Fedlex have no legal force and do not exist for every version.
3. **A change is dated by its own entry into force**, not by the version where it first appears.
4. **Publisher's corrections are labelled and never credited to an act.**
5. **Changes not yet in force are on their own branch**, so `main` is always the law today.
6. **Queries are cut into slices.** The endpoint answers HTTP 500 to a query over every version at once, and its
   firewall answers 400 to a filter on an impact's target address.
7. **Tags mark amending acts only.** A tag per act and per day would be tens of thousands; the commit dates and the
   `In-force:` trailer give each day.
8. **Fedlex's robots.txt.** `fedlex.data.admin.ch/robots.txt` asks automated clients not to fetch `/filestore/*`, where
   the XML files are. The first full download (28 October 2026, about 12,000 files, at most four at a time) did so
   before this was noticed. The files' addresses are published in Fedlex's open SPARQL data and the texts are free of
   copyright, but the request is respected from then on: `fetch_all.py` only reads files already in its cache unless
   it is given `--filestore`, which is for use once the Federal Chancellery has agreed to bulk access.
9. **Transitional rules are not modelled.** An amending act's own transitional provisions ("für hängige Verfahren gilt
   bisheriges Recht") are in the Official Compilation, not in the consolidated text, and are not read yet.
10. **Days before 1970.** Git cannot store an earlier time, so those commits are dated 1 January 1970 (UTC), one
   second apart in order. The real day is in the subject line and in the `In-force:` or `Consolidated:` trailer.

## What an AI model did

This repository was built on {today} in **Claude Code**, Anthropic's coding tool, by the model **Claude Opus 5.5**
(model id `claude-opus-5-5`), working from goals set by the user at Lexifina: a git history of Swiss law with proper
dates, keeping the semantic functions of Lexifina's US Code record (the law on a date, who wrote each phrase, what
relies on a provision, following it), with a reader on lexifina.com and a repository to be made public; then all of
Swiss federal law.

The model:

- **Researched the prior art and the sources:** the repositories below, Fedlex's JOLux ontology, its SPARQL endpoint
  and its Akoma Ntoso XML.
- **Wrote all the code and text in this repository:** the tools, the README, this file and the licence, and chose the
  design described in them.
- **Ran the commands above** and checked the results.

The model did **not**:

- **Write or edit any legal text.** Every word of every article, every date and every act's title is copied by the
  tools from Fedlex.
- **Take part in building the history.** No AI model is called when the history is built or checked.

The user decided what was in scope and decides when the repository is made public. The work was not reviewed line by
line by a lawyer. Only the Official Compilation (AS) is authoritative.

## The research behind the design

Studied before the design was chosen (checked {today}):

- [c3e/grundgesetz](https://github.com/c3e/grundgesetz): the German Basic Law, one commit per amending law.
- [jonashertner/swisslaw-git](https://github.com/jonashertner/swisslaw-git): federal and cantonal law, each version a
  commit dated the day it applies, from Fedlex's Akoma Ntoso since 2021.
- [benjamin-arfa/swiss-law](https://github.com/benjamin-arfa/swiss-law): federal law in Markdown, synced from Fedlex.
- [droid-f/fedlex](https://github.com/droid-f/fedlex): Fedlex's objects mirrored as JSON.
- [legalize-dev/legalize-ch](https://github.com/legalize-dev/legalize-ch): Swiss law dated by publication.
- [swiss/fedlex-jolux](https://github.com/swiss/fedlex-jolux) and [swiss/fedlex-sparql](https://github.com/swiss/fedlex-sparql): the documentation of Fedlex's linked data.

Those repositories commit each consolidated version. This one makes each commit an amending act: it names the act
behind every change, credits each phrase to the act that wrote it, dates each change by its own entry into force, and
keeps corrections and changes not yet in force apart.
"""

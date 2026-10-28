# Swiss federal law, change by change

The Swiss Classified Compilation (Systematische Rechtssammlung, SR) as a git repository: every federal act and treaty
that the Federal Chancellery publishes as structured text on [Fedlex](https://www.fedlex.admin.ch), in German. Each
amending act is one commit, credited to that act and dated the day its changes took effect, at noon in Zurich.

*Deutsch: [unten](#deutsch).*

## Why it is built this way

Repositories of consolidated versions already exist: take each new version of an act, commit it, and git shows what
changed. That answers half of a lawyer's question. The other half is *why*: which act changed this sentence, when did
the change take effect, and what else does it reach? A diff between two versions cannot say. This repository is
arranged so that it can.

- **Each commit is one amending act.** Its author is the act in the Official Compilation (AS) that made the change,
  for example `AS 2021 310`, so `git blame` answers "which act wrote this paragraph?". The act is named by two official
  sources: Fedlex's own record of which act changed which article, and the footnote printed under the article
  ("Fassung gemäss …", "Eingefügt durch …", "Angenommen in der Volksabstimmung vom …").
- **Commits are dated the day the change took effect** (Inkrafttreten). That is the date that decides which text
  applies to a case. It can be months after the Federal Assembly adopted the act, and a change to the Constitution
  takes effect on the day of the vote but is published weeks later. Every commit message records each date as a
  trailer: `Adopted:`, `Vote:` where there was one, `Published:` and `In-force:`, with `Affecting:` and `Source:`.
- **Main is the law today.** Changes already adopted but not yet in force are on the branch `future`,
  each dated the day it will take effect. `git log main..future` lists them.
- **Each act is a folder named by its SR number** (`101/` is the Constitution, `220/` the Code of Obligations, `0.101/`
  the European Convention on Human Rights), and **each article is a file** (`101/art-010a.md`), one paragraph per
  paragraph, so `git log -p 101/art-010a.md` is the history of Art. 10a.
- **Corrections are not laws.** Where Fedlex corrected its consolidated text without an act behind it (a spelling, a
  line break), the commit is by `Bundeskanzlei (Fedlex)` and says so. Changes of typesetting alone ("..." for "…") are
  not commits at all.
- **The record starts where the structured text does.** For most acts that is 2021; some go back further. The first
  commit of each act is by the Federal Chancellery (`Consolidated:` trailer). The footnotes in it credit older text
  to the acts that wrote it; the reader on lexifina.com shows those authors paragraph by paragraph.

## Using it

The text in force on a day, for one article or a whole act:

```sh
python tools/stand_am.py 2021-06-01 101 197      # Art. 197 of the Constitution on 1 June 2021
python tools/stand_am.py 2024-07-01 281.1        # the whole Debt Enforcement and Bankruptcy Act on 1 July 2024
```

Or with git alone (a commit is dated noon in Zurich on its day, so ask for the end of the day):

```sh
git checkout "$(git rev-list -1 --before=2024-07-01T23:59:59+02:00 main)" -- 281.1
```

Which act wrote each paragraph, and every change to an article:

```sh
git blame 101/art-010a.md
git log -p --word-diff 281.1/art-230.md
```

`git blame` credits whole lines, and a line is a paragraph. Where two acts wrote parts of one paragraph, blame names
the later one; `git log -p --word-diff` on the file shows each act's own words.

Everything one amending act changed, across every act it touched:

```sh
git show as/2023-628
git log --author='AS 2023 628'
```

The history is rebuilt from scratch when the record is regenerated, so commit hashes can change between builds. To
update a clone:

```sh
git fetch --force --tags origin && git checkout main && git reset --hard origin/main
```

(`git fetch --tags` alone keeps tags you already have, so it would leave you reading the old build.)

Every amending act is a tag (`as/2021-310`). The amending acts with their dates are in [`erlasse.csv`](erlasse.csv);
every act in the record, with its SR number, titles, status and versions, is in [`data/erlasse.json`](data/erlasse.json).
Each act's folder has a `README.md` listing its articles and how often each changed. How the repository was made,
step by step, and how to rebuild it hash for hash: [`REPRODUCE.md`](REPRODUCE.md).

## What is not here yet

- Versions Fedlex publishes only as PDF or Word documents, which is most versions before 2021. Their text is not here;
  the footnotes still credit it.
- Annexes and tables attached to an act, and acts whose structured text holds no articles.
- An amending act's own transitional rules ("für hängige Verfahren gilt bisheriges Recht"), which are in the Official
  Compilation, not in the consolidated text.
- French, Italian and Romansh. The three official languages are equally authoritative.

This is a research aid. Only the Official Compilation (AS) is authoritative; the consolidated text on Fedlex, and so
this repository, is not.

## Sources and licence

Text and data: the Federal Chancellery's publication platform Fedlex, through its open linked-data service (the JOLux
ontology) and the Akoma Ntoso XML of each consolidated version. Enactments and official texts of the Confederation are
not protected by copyright (Art. 5 para. 1 let. a of the Copyright Act, URG). The history, commit messages and tables
are released under [CC0 1.0](LICENSE). The repository is built by Lexifina Watch; the same record, with a reader for
any date, is at lexifina.com/watch/swiss-law.

---

## Deutsch

Die Systematische Rechtssammlung des Bundes als Git-Repository: jeder Erlass und Staatsvertrag, den die Bundeskanzlei
auf Fedlex als strukturierten Text veröffentlicht, im deutschen Wortlaut.

- **Jeder Commit ist ein Änderungserlass** der Amtlichen Sammlung (AS), als Autor eingetragen, so dass `git blame`
  zeigt, welcher Erlass welchen Absatz geschrieben hat. Den Erlass nennen zwei amtliche Quellen: die Änderungsdaten von
  Fedlex und die Fussnote unter dem Artikel.
- **Jeder Commit trägt das Datum des Inkrafttretens**, Mittag in Zürich. In der Nachricht stehen auch Beschluss,
  Volksabstimmung, Veröffentlichung und Inkrafttreten.
- **`main` ist das geltende Recht.** Beschlossene, noch nicht geltende Änderungen liegen im Branch `future`.
- **Jeder Erlass ist ein Ordner mit seiner SR-Nummer**, jeder Artikel eine Datei, jeder Absatz ein Absatz.
- **Berichtigungen sind keine Gesetze.** Wo Fedlex den Text ohne Erlass berichtigt hat, ist der Commit von der
  Bundeskanzlei.

Massgebend ist allein die Amtliche Sammlung.

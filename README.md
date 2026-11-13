# Schweizer Bundesrecht, Änderung für Änderung

**Deutsch** · [English](README.en.md)

<picture>
<source media="(prefers-color-scheme: dark)" srcset="data/de/effort-dark.svg">
<img alt="Schweizer Recht in diesem Repository: Inhalt, Änderungen nach Jahr des Inkrafttretens, Vollständigkeit gegenüber den amtlichen Quellen und Richtigkeit des Enthaltenen" src="data/de/effort-light.svg" width="880">
</picture>

Teil von [lexifina/global-law](https://github.com/lexifina/global-law), einer Git-Historie für das Recht aller Länder: Dies ist das Bundesrecht der Schweiz, das global-law unter `switzerland/bund/acts/` liest.

Die Systematische Rechtssammlung des Bundes (SR) als Git-Repository: jeder Bundeserlass und jeder Staatsvertrag, den die
Bundeskanzlei auf [Fedlex](https://www.fedlex.admin.ch) als strukturierten Text veröffentlicht, im deutschen Wortlaut.
Jeder Änderungserlass ist ein Commit, diesem Erlass zugeschrieben und auf den Tag datiert, an dem seine Änderungen in
Kraft getreten sind, um 12 Uhr Zürcher Zeit.

## Warum es so aufgebaut ist

Repositories mit konsolidierten Fassungen gibt es bereits: Man nimmt jede neue Fassung eines Erlasses, committet sie,
und Git zeigt, was sich geändert hat. Das beantwortet die Hälfte der Frage, die eine Juristin oder ein Jurist stellt.
Die andere Hälfte ist das *Warum*: Welcher Erlass hat diesen Satz geändert, wann ist die Änderung in Kraft getreten, und
worauf wirkt sie sich sonst noch aus? Ein Diff zwischen zwei Fassungen kann das nicht sagen. Dieses Repository ist so
angelegt, dass es das kann.

- **Jeder Commit ist ein Änderungserlass.** Sein Autor ist der Erlass in der Amtlichen Sammlung (AS), der die Änderung
  vorgenommen hat, zum Beispiel `AS 2021 310`, so dass `git blame` die Frage «Welcher Erlass hat diesen Absatz
  geschrieben?» beantwortet. Den Erlass nennen zwei amtliche Quellen: die eigenen Angaben von Fedlex darüber, welcher
  Erlass welchen Artikel geändert hat, und die unter dem Artikel abgedruckte Fussnote («Fassung gemäss …», «Eingefügt
  durch …», «Angenommen in der Volksabstimmung vom …»).
- **Commits tragen das Datum des Inkrafttretens.** Dieses Datum entscheidet, welcher Text auf einen Fall anwendbar ist.
  Es kann Monate nach der Verabschiedung des Erlasses durch die Bundesversammlung liegen, und eine Änderung der
  Bundesverfassung tritt am Tag der Abstimmung in Kraft, wird aber erst Wochen später veröffentlicht. Jede
  Commit-Nachricht hält jedes Datum als Trailer fest: `Adopted:`, `Vote:`, wo es eine Abstimmung gab, `Published:` und
  `In-force:`, dazu `Affecting:` und `Source:`.
- **Main ist das heute geltende Recht.** Bereits beschlossene, aber noch nicht in Kraft getretene Änderungen liegen im
  Branch `future`, jeweils auf den Tag datiert, an dem sie in Kraft treten werden. `git log main..future` listet sie auf.
- **Jeder Erlass ist ein Ordner, der nach seiner SR-Nummer benannt ist** (`101/` ist die Bundesverfassung, `220/` das
  Obligationenrecht, `0.101/` die Europäische Menschenrechtskonvention), und **jeder Artikel ist eine Datei**
  (`101/art-010a.md`), jeder Absatz des Artikels ein Absatz der Datei, so dass `git log -p 101/art-010a.md` die
  Geschichte von Art. 10a ist.
- **Berichtigungen sind keine Gesetze.** Wo Fedlex seinen konsolidierten Text ohne zugrunde liegenden Erlass berichtigt
  hat (eine Schreibweise, einen Zeilenumbruch), stammt der Commit von `Bundeskanzlei (Fedlex)` und sagt das auch. Rein
  typografische Änderungen ("..." für "…") sind überhaupt keine Commits.
- **Der Bestand beginnt dort, wo der strukturierte Text beginnt.** Bei den meisten Erlassen ist das 2021; manche
  reichen weiter zurück. Der erste Commit jedes Erlasses stammt von der Bundeskanzlei (Trailer `Consolidated:`). Die
  Fussnoten darin schreiben älteren Text den Erlassen zu, die ihn geschrieben haben; die Leseansicht auf lexifina.com
  zeigt diese Autoren Absatz für Absatz.

## Verwendung

Der an einem bestimmten Tag geltende Text, für einen Artikel oder einen ganzen Erlass:

```sh
python tools/stand_am.py 2021-06-01 101 197      # Art. 197 der Bundesverfassung am 1. Juni 2021
python tools/stand_am.py 2024-07-01 281.1        # das ganze Bundesgesetz über Schuldbetreibung und Konkurs am 1. Juli 2024
```

Oder nur mit Git (ein Commit ist auf 12 Uhr Zürcher Zeit seines Tages datiert, also nach dem Ende des Tages fragen):

```sh
git checkout "$(git rev-list -1 --before=2024-07-01T23:59:59+02:00 main)" -- 281.1
```

Welcher Erlass jeden Absatz geschrieben hat, und jede Änderung eines Artikels:

```sh
git blame 101/art-010a.md
git log -p --word-diff 281.1/art-230.md
```

`git blame` schreibt ganze Zeilen zu, und eine Zeile ist ein Absatz. Wo zwei Erlasse Teile desselben Absatzes
geschrieben haben, nennt blame den späteren; `git log -p --word-diff` auf der Datei zeigt den eigenen Wortlaut jedes
Erlasses.

Alles, was ein Änderungserlass geändert hat, in allen Erlassen, die er berührt:

```sh
git show as/2023-628
git log --author='AS 2023 628'
```

Die Historie wird von Grund auf neu aufgebaut, wenn der Bestand neu erzeugt wird, so dass sich Commit-Hashes zwischen
zwei Builds ändern können. So wird ein Klon aktualisiert:

```sh
git fetch --force --tags origin && git checkout main && git reset --hard origin/main
```

(`git fetch --tags` allein behält Tags, die bereits vorhanden sind; man würde also weiterhin den alten Build lesen.)

Jeder Änderungserlass ist ein Tag (`as/2021-310`). Die Änderungserlasse mit ihren Daten stehen in
[`erlasse.csv`](erlasse.csv); jeder Erlass im Bestand, mit SR-Nummer, Titeln, Status und Fassungen, steht in
[`data/erlasse.json`](data/erlasse.json). Der Ordner jedes Erlasses enthält eine `README.md`, die seine Artikel auflistet
und angibt, wie oft jeder geändert wurde. Wie das Repository Schritt für Schritt erstellt wurde und wie es sich Hash für
Hash nachbauen lässt: [`REPRODUCE.md`](REPRODUCE.md).

## Was noch fehlt

- Fassungen, die Fedlex nur als PDF- oder Word-Dokument veröffentlicht, also die meisten Fassungen vor 2021. Ihr Text
  ist nicht enthalten; die Fussnoten schreiben ihn dennoch zu.
- Anhänge und Tabellen zu einem Erlass sowie Erlasse, deren strukturierter Text keine Artikel enthält.
- Die eigenen Übergangsbestimmungen eines Änderungserlasses («für hängige Verfahren gilt bisheriges Recht»), die in der
  Amtlichen Sammlung stehen, nicht im konsolidierten Text.
- Französisch, Italienisch und Rätoromanisch. Die drei Amtssprachen sind gleichermassen massgebend.

Dies ist ein Hilfsmittel für die Recherche. Massgebend ist allein die Amtliche Sammlung (AS); der konsolidierte Text auf
Fedlex und damit dieses Repository sind es nicht.

## Quellen und Lizenz

Texte und Daten: die Publikationsplattform Fedlex der Bundeskanzlei, über ihren offenen Linked-Data-Dienst (die
JOLux-Ontologie) und das Akoma-Ntoso-XML jeder konsolidierten Fassung. Erlasse und amtliche Texte des Bundes sind
urheberrechtlich nicht geschützt (Art. 5 Abs. 1 Bst. a des Urheberrechtsgesetzes, URG). Die Historie, die
Commit-Nachrichten und die Tabellen werden unter [CC0 1.0](LICENSE) freigegeben. Das Repository wird von Lexifina Watch
erstellt; derselbe Bestand, mit einer Leseansicht für jedes beliebige Datum, ist unter lexifina.com/watch/swiss-law
verfügbar.

Dies ist eine Übersetzung der englischen Fassung ([README.en.md](README.en.md)); bei Abweichungen gilt die englische Fassung.

## Mehr

Aus dem Repository [lexifina/global-law](https://github.com/lexifina/global-law) (auf Englisch):

- [FEATURES.md](https://github.com/lexifina/global-law/blob/main/FEATURES.md): alle Funktionen und was jedes Korpus unterstützen muss (`git blame`, `law.py`, MCP-Werkzeuge)
- [FAQ.md](https://github.com/lexifina/global-law/blob/main/FAQ.md): Fragen und Antworten · [CONTRIBUTING.md](https://github.com/lexifina/global-law/blob/main/CONTRIBUTING.md): Änderungen vorschlagen · [MCP.md](https://github.com/lexifina/global-law/blob/main/MCP.md): MCP-Server · [REPRODUCE.md](https://github.com/lexifina/global-law/blob/main/REPRODUCE.md): wie es erstellt wurde · [CHANGELOG.md](https://github.com/lexifina/global-law/blob/main/CHANGELOG.md)
- [FRESHNESS.md](https://github.com/lexifina/global-law/blob/main/FRESHNESS.md): wie aktuell jedes Korpus ist · [Überwachung](https://github.com/lexifina/global-law/tree/main/monitoring): ob die Aktualisierungen funktionieren · [WATCHING.md](https://github.com/lexifina/global-law/blob/main/WATCHING.md): wie jede amtliche Quelle auf Änderungen überwacht wird
- [performance/](https://github.com/lexifina/global-law/tree/main/performance): wie schnell die Werkzeuge sind, gemessen
- [visualisations/](https://github.com/lexifina/global-law/tree/main/visualisations): Diagramme und Verbindungen im Recht der ganzen Welt
- [Schwachstellen](https://github.com/lexifina/global-law/tree/main/vulnerabilities): Fehler in Rechtsakten, wie sie veröffentlicht wurden

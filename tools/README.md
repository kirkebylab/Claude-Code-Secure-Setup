# tools/ — small programs for working with papers

Two command-line tools, written during a literature review in November 2026 and kept
because they are worth reusing. Claude can run them for you; you can also run them
yourself in a terminal.

| Tool | What it does |
| :--- | :----------- |
| `verify_citations.py` | Checks that papers are real and correctly cited |
| `fetch_fulltext.py` | Downloads full texts through official open-access channels |

Both need Python 3, which is already on a Mac. Neither needs anything installed.

---

## verify_citations.py

Checks each paper against three independent sources, which have to agree:

1. **PubMed** — title, authors, journal, year, DOI
2. **doi.org** — the DOI is actually registered
3. **Crossref** — title, first author, year and journal match what PubMed says

It also screens for retractions, partial retractions, expressions of concern and
published corrections.

```bash
python3 tools/verify_citations.py 25417104 28860383
python3 tools/verify_citations.py 10.1126/science.aan0677
python3 tools/verify_citations.py --file my_ids.txt --json results.json
```

PubMed IDs and DOIs can be mixed freely. With `--file`, put one per line; blank lines
and lines starting with `#` are ignored.

Output looks like this:

```
PMID       First author / year    OK     Notes
------------------------------------------------------------------------------
25417104   Thaiss 2014            yes    all three sources agree
26879573   Montagner 2016         yes    has correction
99999999   -                      NO     not found in PubMed
```

**Why bother.** A citation that looks right can be wrong in ways you cannot see: a
real DOI attached to the wrong title, a year that drifted between sources, or a paper
retracted after you read it. Anything marked `NO` should not be cited until you have
checked it by hand.

---

## fetch_fulltext.py

Downloads papers, trying official channels in order and stopping at the first that
works.

```bash
python3 tools/fetch_fulltext.py --out workspace/papers 25417104 28860383
python3 tools/fetch_fulltext.py --out workspace/papers --file my_ids.txt
```

The order is:

1. **The National Library of Medicine's open-data service** — the article PDF if one
   exists, otherwise the complete article text the library distributes. Free, no
   login, and the single most productive source.
2. **The publisher**, for articles carrying an open licence. Nature, PLOS, JCI and
   EMBO Press serve these directly.
3. **A repository copy**, found through OpenAlex and OpenAIRE. These are authors'
   own deposits in Zenodo or a university repository.
4. **bioRxiv**, only with `--preprints`, and only when nothing else exists.

What you get is named so you can tell the versions apart:

| File ending | What it is |
| :---------- | :--------- |
| `.pdf` | The article as published |
| `_fulltext.txt` | The complete text, but no figures or layout |
| `_accepted.pdf` | The author's accepted manuscript from a repository. Peer reviewed, but not the final published version |
| `_preprint.pdf` | A preprint. **Not peer reviewed.** Cite the published version |

### What it will not do

It will not get past a bot challenge, a 403, or a login wall. Those are answers, not
obstacles. Cell Press, PNAS, Science, ScienceDirect and Oxford University Press all
refuse automated clients, so their papers cannot be fetched this way even when they
are free to read. The tool records each one and gives you a link to open yourself,
which usually works in one click with a university login.

It also skips staging mirrors that serve content a publisher's own site declines to
serve. An author's deposit in their university repository is a different thing and is
fine to take.

### Always check what you got

A repository deposit can be mislabelled. The tool prints the title embedded inside
each PDF, and marks it `CHECK:` when that title looks nothing like the paper you asked
for. When you see that, open the file and read page 1.

This is not hypothetical. One Zenodo deposit matched a Cell paper exactly on title and
DOI, but the file inside was named for a Nature paper. It may have been right; it
could not be confirmed without a human looking.

---

## Networks and approvals

Both tools reach the internet, so Claude Code will ask you to approve each site the
first time. The ones they use:

| Site | Why |
| :--- | :-- |
| `eutils.ncbi.nlm.nih.gov` | PubMed records |
| `doi.org` | Confirming a DOI is registered |
| `api.crossref.org` | Cross-checking citation details, and retraction notices |
| `www.ebi.ac.uk` | Europe PMC: licences, identifiers |
| `pmc-oa-opendata.s3.amazonaws.com` | The library's open-data full texts |
| `api.openalex.org`, `api.openaire.eu` | Finding repository copies |
| `zenodo.org` and university repositories | Author deposits |
| `www.nature.com`, `journals.plos.org`, `www.jci.org`, `www.embopress.org` | Openly licensed PDFs |
| `api.biorxiv.org`, `www.biorxiv.org` | Preprints, only with `--preprints` |

Responses are cached in `tools/.cache` so re-running a job does not hammer anyone's
server. That folder is not saved into git. Delete it any time.

## Settings

Two environment variables, both optional:

- `LIT_TIMEOUT` — seconds to wait per request, default 600. The first request to a new
  site waits for you to approve it, so keep this generous.
- `LIT_CACHE` — where to keep cached responses, default `tools/.cache`.

#!/usr/bin/env python3
"""Fetch the full text of papers, through official open-access channels only.

Sources are tried in this order, and the first that works wins:

  1. NLM PMC open-data on AWS     the article PDF if there is one, else the
                                  complete text the library distributes
  2. The publisher, for openly licensed articles only (Nature, PLOS, JCI, EMBO)
  3. A repository copy, found via OpenAlex and OpenAIRE (Zenodo, university
                                  repositories): the author's own deposit
  4. bioRxiv, for a preprint when nothing else exists

WHAT IT WILL NOT DO: get past a bot challenge, a 403 or a login wall. Those are
answers, not obstacles. Many publishers, Cell Press, PNAS, Science and ScienceDirect
among them, refuse automated clients; their papers are free to read in a browser but
not reachable this way. The tool records that and gives you the link.

It also will not take a staging mirror that serves content the publisher itself
declines to serve us. An author's deposit in their own university repository is a
different thing and is fine.

USAGE

    python3 tools/fetch_fulltext.py --out workspace/papers 25417104 28860383
    python3 tools/fetch_fulltext.py --out workspace/papers --file ids.txt
    python3 tools/fetch_fulltext.py --out workspace/papers --file ids.txt --preprints

By default preprints are skipped, because they are not peer reviewed. Pass
--preprints to accept one when nothing better exists; such files get a _preprint
suffix so they can never be mistaken for the published article.

ALWAYS CHECK WHAT YOU GOT. A repository deposit can be mislabelled. This tool prints
the title embedded in each PDF so you can compare it against the paper you wanted.

NETWORK: contacts eutils.ncbi.nlm.nih.gov, www.ebi.ac.uk,
pmc-oa-opendata.s3.amazonaws.com, api.openalex.org, api.openaire.eu, zenodo.org,
api.biorxiv.org and publisher sites. Claude Code asks you to approve each the first
time.
"""

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _net  # noqa: E402
from verify_citations import fetch_pubmed, pmid_for_doi  # noqa: E402

BUCKET = "https://pmc-oa-opendata.s3.amazonaws.com/"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"


# ----------------------------------------------------------------- lookups
def europepmc(pmid):
    try:
        found = _net.get_json(EPMC + "search", {
            "query": "EXT_ID:%s AND SRC:MED" % pmid,
            "format": "json", "resultType": "core"})
        hits = found.get("resultList", {}).get("result", [])
        return hits[0] if hits else {}
    except _net.Refused:
        return {}


def safe_name(record):
    first = ((record["authors"] or [{}])[0].get("last")
             or (record["authors"] or [{}])[0].get("collective") or "Unknown")
    words = [w for w in re.findall(r"[A-Za-z]+", record["title"]) if len(w) > 3][:4]
    slug = "".join(w.capitalize() for w in words) or "Untitled"
    return "%s_%s_%s" % (re.sub(r"\W", "", first), record["year"], slug)


def pdf_title(data):
    """The title the PDF claims for itself. Useful for spotting a wrong file."""
    for match in re.finditer(rb"/Title\s*\(((?:[^()\\]|\\.)*)\)", data[:2000000]):
        text = match.group(1).decode("utf-8", "replace").strip()
        if len(text) > 12 and not text.lower().endswith((".docx", ".doc", ".indd")):
            return text
    return ""


def is_pdf(data):
    return data[:5] == b"%PDF-"


# ----------------------------------------------------------------- sources
def from_nlm(pmcid):
    """The library's own open-data channel. Returns (kind, suffix, bytes) or None."""
    if not pmcid:
        return None
    try:
        listing = _net.get(BUCKET, {"list-type": "2", "prefix": pmcid + ".",
                                    "max-keys": "60"}, cache=False)
    except _net.Refused:
        return None
    keys = re.findall(r"<Key>([^<]+)</Key>", listing)
    if not keys:
        return None
    stem = sorted({k.split("/")[0] for k in keys})[-1]

    for suffix, kind, ext in ((".pdf", "pdf", ".pdf"), (".txt", "fulltext", "_fulltext.txt")):
        wanted = "%s/%s%s" % (stem, stem, suffix)
        if wanted not in keys:
            continue
        try:
            data = _net.get(BUCKET + wanted, binary=True, cache=False)
        except _net.Refused:
            continue
        if suffix == ".pdf" and not is_pdf(data):
            continue
        return kind, ext, data
    return None


PUBLISHER_PATTERNS = (
    ("10.1038/", "https://www.nature.com/articles/%s.pdf",
     lambda doi: doi.split("/", 1)[1]),
    ("10.1371/", "https://journals.plos.org/plosone/article/file?id=%s&type=printable",
     lambda doi: doi),
    ("10.15252/", "https://www.embopress.org/doi/pdf/%s", lambda doi: doi),
    ("10.1172/", "https://www.jci.org/articles/view/%s/files/pdf",
     lambda doi: re.sub(r"^.*?(\d+)$", r"\1", doi)),
)


def from_publisher(doi, licence):
    """Only for articles the archive says carry an open licence."""
    if not doi or not licence:
        return None
    for prefix, template, extract in PUBLISHER_PATTERNS:
        if doi.lower().startswith(prefix):
            try:
                data = _net.get(template % extract(doi), binary=True, cache=False,
                                min_interval=1.5, accept="application/pdf,*/*")
            except (_net.Refused, Exception):
                return None
            return ("pdf", ".pdf", data) if is_pdf(data) else None
    return None


SKIP_HOSTS = ("dev-openaire", "sci-hub", "libgen")


def repository_urls(doi):
    """Author deposits, via OpenAlex then OpenAIRE. Publisher hosts are left out."""
    urls = []
    try:
        work = _net.get_json(
            "https://api.openalex.org/works/doi:%s" % doi,
            {"select": "doi,open_access,best_oa_location,locations"}, cache=False)
        for location in (work.get("locations") or []):
            if not location.get("is_oa"):
                continue
            url = location.get("pdf_url") or ""
            if url:
                urls.append(url)
    except Exception:
        pass
    try:
        raw = _net.get("https://api.openaire.eu/search/publications",
                       {"doi": doi, "format": "json"}, cache=False, min_interval=1.5)
        for url in re.findall(r"https?://[^\"<>\\ ]+", raw):
            if url.lower().endswith(".pdf") or "/files/" in url or "bitstream" in url:
                urls.append(url)
    except Exception:
        pass

    keep = []
    for url in dict.fromkeys(urls):
        host = _net.urlparse_host(url).lower()
        if any(bad in host for bad in SKIP_HOSTS):
            continue
        # Publisher sites refuse automated clients; do not waste a request or a prompt.
        if any(bad in host for bad in ("cell.com", "sciencedirect", "pnas.org",
                                       "science.org", "oup.com", "diabetesjournals")):
            continue
        keep.append(url)
    return keep


def from_repository(doi):
    for url in repository_urls(doi):
        try:
            data = _net.get(url, binary=True, cache=False, min_interval=1.5,
                            accept="application/pdf,*/*")
        except _net.Refused:
            continue
        except Exception:
            # Small repositories fail transiently; one more go.
            try:
                data = _net.get(url, binary=True, cache=False, min_interval=3.0,
                                accept="application/pdf,*/*")
            except Exception:
                continue
        if is_pdf(data):
            return "repository", "_accepted.pdf", data, url
    return None


def from_biorxiv(doi):
    try:
        found = _net.get_json("https://api.biorxiv.org/pubs/biorxiv/" + doi, cache=False)
    except Exception:
        return None
    collection = found.get("collection") or []
    if not collection:
        return None
    preprint_doi = collection[0].get("preprint_doi")
    if not preprint_doi:
        return None
    for version in ("v1", "v2", ""):
        try:
            data = _net.get("https://www.biorxiv.org/content/%s%s.full.pdf"
                            % (preprint_doi, version), binary=True, cache=False,
                            min_interval=2.0, accept="application/pdf,*/*")
        except Exception:
            continue
        if is_pdf(data):
            return "preprint", "_preprint.pdf", data, preprint_doi
    return None


# ----------------------------------------------------------------- main
def main():
    parser = argparse.ArgumentParser(
        description="Fetch paper full texts through open-access channels only.")
    parser.add_argument("ids", nargs="*", help="PubMed IDs and/or DOIs")
    parser.add_argument("--file", help="file with one PubMed ID or DOI per line")
    parser.add_argument("--out", required=True, help="folder to save into")
    parser.add_argument("--preprints", action="store_true",
                        help="accept a bioRxiv preprint when nothing better exists")
    args = parser.parse_args()

    ids = list(args.ids)
    if args.file:
        with open(args.file) as fh:
            ids += [l.strip() for l in fh
                    if l.strip() and not l.strip().startswith("#")]
    if not ids:
        parser.error("give at least one PubMed ID or DOI, or use --file")

    pmids = []
    for item in ids:
        if item.isdigit():
            pmids.append(item)
        elif "/" in item:
            found = pmid_for_doi(item)
            if found:
                pmids.append(found)
            else:
                print("could not resolve to a PubMed record: %s" % item)

    os.makedirs(args.out, exist_ok=True)
    records = fetch_pubmed(pmids)
    report = {}

    print()
    for pmid in pmids:
        record = records.get(pmid)
        if not record:
            print("%-10s not found in PubMed" % pmid)
            continue
        name = safe_name(record)
        meta = europepmc(pmid)
        pmcid, licence = meta.get("pmcid", ""), meta.get("license", "")
        doi = record["doi"]

        got = None
        source = ""
        result = from_nlm(pmcid)
        if result:
            kind, ext, data = result
            got, source = (kind, ext, data), "NLM open data (%s)" % pmcid
        if not got:
            result = from_publisher(doi, licence)
            if result:
                got, source = result, "publisher (%s)" % licence
        if not got:
            result = from_repository(doi)
            if result:
                kind, ext, data, url = result
                got, source = (kind, ext, data), "repository %s" % _net.urlparse_host(url)
        if not got and args.preprints:
            result = from_biorxiv(doi)
            if result:
                kind, ext, data, pre = result
                got, source = (kind, ext, data), "bioRxiv %s" % pre

        if not got:
            link = ("https://europepmc.org/article/MED/%s" % pmid if pmcid
                    else "https://doi.org/%s" % doi)
            print("%-10s %-34s NOT AVAILABLE -> %s" % (pmid, name[:34], link))
            report[pmid] = {"name": name, "state": "unavailable", "link": link}
            continue

        kind, ext, data = got
        path = os.path.join(args.out, name + ext)
        with open(path, "wb") as fh:
            fh.write(data)
        claimed = pdf_title(data) if ext.endswith(".pdf") else ""
        note = ""
        if claimed:
            from verify_citations import _similar
            if _similar(claimed, record["title"]) < 0.6:
                note = "  CHECK: pdf says %r" % claimed[:45]
        print("%-10s %-34s %-9s %s%s" % (pmid, name[:34], kind, source, note))
        report[pmid] = {"name": name, "state": kind, "source": source,
                        "file": name + ext, "pdf_title": claimed}

    with open(os.path.join(args.out, "_fetch_report.json"), "w") as fh:
        json.dump(report, fh, indent=1)

    states = [r["state"] for r in report.values()]
    print()
    print("%d of %d obtained. Report written to %s"
          % (sum(1 for s in states if s != "unavailable"), len(report),
             os.path.join(args.out, "_fetch_report.json")))
    missing = [r for r in report.values() if r["state"] == "unavailable"]
    if missing:
        print("The rest are free to read in a browser or need a library login; "
              "links are in the report.")
    if any("CHECK" in str(r.get("pdf_title", "")) for r in report.values()):
        print("Anything marked CHECK: open it and confirm it is the right paper.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

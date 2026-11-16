#!/usr/bin/env python3
"""Check that papers are real and correctly cited, before you rely on them.

Every paper is checked against three independent sources, which must agree:

  1. PubMed            title, authors, journal, year, DOI
  2. doi.org           the DOI is actually registered
  3. Crossref          title, first author, year and journal match PubMed

It also screens for retractions, partial retractions, expressions of concern and
published corrections, using both PubMed's CommentsCorrections and Crossref's
update records.

WHY BOTHER: a citation that looks right can be wrong in ways that are invisible until
someone checks: a real DOI attached to the wrong title, a year that drifted between
sources, or a paper that was retracted after you read it. This catches those.

USAGE

    python3 tools/verify_citations.py 25417104 28860383
    python3 tools/verify_citations.py 10.1126/science.aan0677
    python3 tools/verify_citations.py --file my_ids.txt
    python3 tools/verify_citations.py --file my_ids.txt --json results.json

Accepts PubMed IDs (all digits) and DOIs (containing a slash), mixed freely. With
--file, one per line; blank lines and lines starting with # are ignored.

NETWORK: contacts eutils.ncbi.nlm.nih.gov, doi.org and api.crossref.org. Claude Code
will ask you to approve each the first time.

EXIT CODE: 0 if every paper verified and none is retracted, 1 otherwise.
"""

import argparse
import difflib
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _net  # noqa: E402

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


# ----------------------------------------------------------------- normalising
def _norm(text):
    text = re.sub(r"<[^>]+>", "", text or "").lower().replace("&amp;", "&")
    text = re.sub(r"[^a-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", re.sub(r"\bthe\b", " ", text)).strip()


def _similar(a, b):
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


# ----------------------------------------------------------------- PubMed
def pmid_for_doi(doi):
    result = _net.get_json(EUTILS + "esearch.fcgi", {
        "db": "pubmed", "term": '"%s"[AID]' % doi, "retmode": "json"})
    ids = result["esearchresult"].get("idlist", [])
    return ids[0] if ids else None


def fetch_pubmed(pmids):
    """Return {pmid: record}."""
    out = {}
    for start in range(0, len(pmids), 100):
        batch = pmids[start:start + 100]
        xml = _net.get(EUTILS + "efetch.fcgi", {
            "db": "pubmed", "id": ",".join(batch), "retmode": "xml"})
        for article in ET.fromstring(xml).findall("PubmedArticle"):
            citation = article.find("MedlineCitation")
            meta = citation.find("Article")
            journal = meta.find("Journal")
            issue = journal.find("JournalIssue")
            pubdate = issue.find("PubDate")

            authors = []
            for author in (meta.findall("AuthorList/Author") or []):
                collective = author.findtext("CollectiveName")
                if collective:
                    authors.append({"collective": collective})
                else:
                    authors.append({
                        "last": author.findtext("LastName") or "",
                        "initials": author.findtext("Initials") or ""})

            doi = ""
            for ident in article.findall("PubmedData/ArticleIdList/ArticleId"):
                if ident.get("IdType") == "doi":
                    doi = (ident.text or "").strip()
                    break
            if not doi:
                for loc in meta.findall("ELocationID"):
                    if loc.get("EIdType") == "doi":
                        doi = (loc.text or "").strip()

            notices = [{"type": c.get("RefType"), "source": c.findtext("RefSource") or ""}
                       for c in citation.findall(
                           "CommentsCorrectionsList/CommentsCorrections")]

            out[citation.findtext("PMID")] = {
                "pmid": citation.findtext("PMID"),
                "title": "".join(meta.find("ArticleTitle").itertext()).strip(),
                "authors": authors,
                "journal": journal.findtext("Title") or "",
                "year": pubdate.findtext("Year")
                        or (pubdate.findtext("MedlineDate") or "")[:4],
                "volume": issue.findtext("Volume") or "",
                "pages": meta.findtext("Pagination/MedlinePgn") or "",
                "doi": doi,
                "pubtypes": [t.text for t in meta.findall(
                    "PublicationTypeList/PublicationType")],
                "notices": notices,
            }
    return out


# ----------------------------------------------------------------- the check
RETRACTION_TYPES = {"RetractionIn", "PartialRetractionIn", "ExpressionOfConcernIn"}
CR_RETRACTION = {"retraction", "partial_retraction", "withdrawal",
                 "expression_of_concern"}


def verify(record):
    problems, checks = [], {}
    doi = record["doi"]

    if not doi:
        problems.append("PubMed has no DOI for this record")
    else:
        try:
            handle = _net.get_json(
                "https://doi.org/api/handles/" + urlquote(doi))
            checks["doi_registered"] = handle.get("responseCode") == 1
        except _net.Refused:
            checks["doi_registered"] = False
        if not checks["doi_registered"]:
            problems.append("DOI is not registered at doi.org")

        try:
            message = _net.get_json(
                "https://api.crossref.org/works/" + urlquote(doi))["message"]
        except _net.Refused:
            message = None
            problems.append("DOI not found in Crossref")

        if message:
            cr_title = (message.get("title") or [""])[0]
            cr_authors = message.get("author") or []
            cr_journal = (message.get("container-title") or [""])[0]
            years = set()
            for key in ("published-print", "published-online", "issued"):
                parts = (message.get(key) or {}).get("date-parts") or []
                if parts and parts[0] and parts[0][0]:
                    years.add(parts[0][0])

            checks["title_similarity"] = round(_similar(record["title"], cr_title), 3)
            if checks["title_similarity"] < 0.90:
                problems.append(
                    "Title disagrees between PubMed and Crossref (%.2f similar): "
                    "PubMed has %r, Crossref has %r"
                    % (checks["title_similarity"], record["title"][:70], cr_title[:70]))

            pm_first = ((record["authors"] or [{}])[0].get("last")
                        or (record["authors"] or [{}])[0].get("collective") or "")
            cr_first = cr_authors[0].get("family", "") if cr_authors else ""
            checks["first_author_match"] = (
                _norm(pm_first) == _norm(cr_first) or _similar(pm_first, cr_first) > 0.85)
            if not checks["first_author_match"]:
                problems.append("First author disagrees: PubMed %r, Crossref %r"
                                % (pm_first, cr_first))

            checks["year_match"] = (record["year"].isdigit()
                                    and int(record["year"]) in years)
            if not checks["year_match"]:
                problems.append("Year disagrees: PubMed %s, Crossref %s"
                                % (record["year"], sorted(years) or "none"))

            checks["journal_match"] = (
                _similar(record["journal"], cr_journal) > 0.80
                or _norm(cr_journal) in _norm(record["journal"])
                or _norm(record["journal"]) in _norm(cr_journal))
            if not checks["journal_match"]:
                problems.append("Journal disagrees: PubMed %r, Crossref %r"
                                % (record["journal"], cr_journal))

        try:
            updates = _net.get_json("https://api.crossref.org/works", {
                "filter": "updates:" + doi, "rows": 50})["message"]["items"]
        except _net.Refused:
            updates = []
        cr_notices = [u.get("type") for item in updates
                      for u in item.get("update-to", [])
                      if u.get("DOI", "").lower() == doi.lower()]
    cr_notices = cr_notices if doi else []

    pm_notices = [n["type"] for n in record["notices"]]
    retracted = ("Retracted Publication" in (record["pubtypes"] or [])
                 or any(t in RETRACTION_TYPES for t in pm_notices)
                 or any(t in CR_RETRACTION for t in cr_notices))
    corrected = ("ErratumIn" in pm_notices or "erratum" in cr_notices
                 or "correction" in cr_notices)

    blocking = [p for p in problems if not p.startswith("Journal disagrees")]
    return {
        "checks": checks,
        "problems": problems,
        "verified": not blocking,
        "retracted": retracted,
        "corrected": corrected,
        "notices": sorted(set(pm_notices + cr_notices)),
    }


def urlquote(text):
    import urllib.parse
    return urllib.parse.quote(text, safe="")


# ----------------------------------------------------------------- cli
def read_ids(args):
    ids = list(args.ids)
    if args.file:
        with open(args.file) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    ids.append(line)
    return ids


def main():
    parser = argparse.ArgumentParser(
        description="Verify papers against PubMed, doi.org and Crossref.")
    parser.add_argument("ids", nargs="*", help="PubMed IDs and/or DOIs")
    parser.add_argument("--file", help="file with one PubMed ID or DOI per line")
    parser.add_argument("--json", help="also write full results to this JSON file")
    args = parser.parse_args()

    ids = read_ids(args)
    if not ids:
        parser.error("give at least one PubMed ID or DOI, or use --file")

    pmids, unresolved = [], []
    for item in ids:
        if item.isdigit():
            pmids.append(item)
        elif "/" in item:
            found = pmid_for_doi(item)
            (pmids.append(found) if found else unresolved.append(item))
        else:
            unresolved.append(item)

    records = fetch_pubmed(pmids) if pmids else {}
    results, failures = {}, 0

    print()
    print("%-10s %-22s %-6s %s" % ("PMID", "First author / year", "OK", "Notes"))
    print("-" * 78)

    for pmid in pmids:
        record = records.get(pmid)
        if not record:
            print("%-10s %-22s %-6s %s" % (pmid, "-", "NO", "not found in PubMed"))
            results[pmid] = {"verified": False, "problems": ["not found in PubMed"]}
            failures += 1
            continue

        outcome = verify(record)
        results[pmid] = {**outcome, "record": record}

        first = ((record["authors"] or [{}])[0].get("last")
                 or (record["authors"] or [{}])[0].get("collective") or "?")
        label = "%s %s" % (first[:15], record["year"])
        flags = []
        if outcome["retracted"]:
            flags.append("RETRACTED")
        if outcome["corrected"]:
            flags.append("has correction")
        note = "; ".join(flags + outcome["problems"]) or "all three sources agree"
        ok = "yes" if outcome["verified"] and not outcome["retracted"] else "NO"
        if ok == "NO":
            failures += 1
        print("%-10s %-22s %-6s %s" % (pmid, label, ok, note[:60]))

    for item in unresolved:
        print("%-10s %-22s %-6s %s" % ("-", item[:22], "NO", "could not resolve to a PubMed record"))
        failures += 1

    print()
    print("%d checked, %d need attention." % (len(pmids) + len(unresolved), failures))
    if failures:
        print("Do not cite anything marked NO until you have checked it by hand.")

    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"results": results, "unresolved": unresolved}, fh, indent=1)
        print("Full details written to %s" % args.json)

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

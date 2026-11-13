"""Resolve a DOI to an open-access PDF.

Diagnostic reviews cite decades of clinical literature; the pipeline is only as
good as its PDF coverage, so coverage must be measured, not assumed.
"""
import json, sys, urllib.parse, urllib.request

UA = {"User-Agent": "SecondOpinion/0.1 (akennedy@theonegroup.info)"}
EMAIL = "akennedy@theonegroup.info"


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def unpaywall(doi):
    try:
        d = _get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={EMAIL}")
    except Exception as e:
        return {"doi": doi, "error": str(e)}
    best = d.get("best_oa_location") or {}
    return {
        "doi": doi,
        "is_oa": d.get("is_oa"),
        "oa_status": d.get("oa_status"),
        "pdf": best.get("url_for_pdf"),
        "landing": best.get("url"),
        "host": best.get("host_type"),
        "title": (d.get("title") or "")[:90],
    }


def europepmc(doi):
    try:
        q = urllib.parse.quote(f'DOI:"{doi}"')
        d = _get("https://www.ebi.ac.uk/europepmc/webservices/rest/search"
                 f"?query={q}&resultType=core&format=json")
    except Exception as e:
        return {"doi": doi, "error": str(e)}
    hits = d.get("resultList", {}).get("result", [])
    if not hits:
        return {"doi": doi, "epmc": None}
    h = hits[0]
    urls = [x.get("url") for x in h.get("fullTextUrlList", {}).get("fullTextUrl", [])]
    return {"doi": doi, "epmc_id": h.get("id"), "pmcid": h.get("pmcid"),
            "in_pmc": h.get("inPMC") == "Y", "urls": [u for u in urls if u]}


def resolve(doi):
    out = unpaywall(doi)
    if not out.get("pdf"):
        e = europepmc(doi)
        out["europepmc"] = e
        if e.get("pmcid"):
            out["pdf"] = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{e['pmcid']}/fullTextXML"
    return out


if __name__ == "__main__":
    for doi in sys.argv[1:]:
        r = resolve(doi)
        print(json.dumps(r, indent=1)[:700])

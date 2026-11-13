"""Header-aware 2x2 extraction with explicit ambiguity handling (option C, done properly).

Design rules
------------
1. Bind values to columns using <th> when available.
2. When headers are absent or contradict the data, try the plausible column
   orders and score each against the percentages printed in the same row.
3. Every row is labelled resolved / mismatch / ambiguous / unparseable.
   Only `resolved` and `mismatch` rows are auditable; `ambiguous` rows never
   produce a finding.
4. A finding always carries the cell values that produced it.
"""
import itertools, json, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

UA = {"User-Agent": "SecondOpinion/0.1 (akennedy@theonegroup.info)"}
INT = re.compile(r"^\s*(\d{1,6})\s*$")
PCT = re.compile(r"(\d{1,3}(?:\.\d+)?)\s*%")

HEADER_HINTS = {
    "tp": ("true positive", "tp", "true positives"),
    "fp": ("false positive", "fp", "false positives"),
    "fn": ("false negative", "fn", "false negatives"),
    "tn": ("true negative", "tn", "true negatives"),
}
ORDERS = {
    "TP,FP,FN,TN": ("tp", "fp", "fn", "tn"),
    "TP,TN,FP,FN": ("tp", "tn", "fp", "fn"),
    "TP,FN,FP,TN": ("tp", "fn", "fp", "tn"),
}


def fetch(pmcid):
    req = urllib.request.Request(
        f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML", headers=UA)
    return urllib.request.urlopen(req, timeout=60).read()


def cell_text(el):
    return " ".join("".join(el.itertext()).split())


def tables(root):
    for tw in root.iter("table-wrap"):
        label = cell_text(tw.find("label")) if tw.find("label") is not None else ""
        cap = cell_text(tw.find("caption")) if tw.find("caption") is not None else ""
        rows = []
        for tr in tw.iter("tr"):
            rows.append([(cell_text(c), c.tag) for c in tr if c.tag in ("td", "th")])
        if rows:
            yield {"label": label, "caption": cap[:80], "rows": rows}


def map_headers(header_cells):
    """Return {role: index} if the header row names the cells, else {}."""
    found = {}
    for i, (txt, _) in enumerate(header_cells):
        low = txt.lower().strip()
        for role, hints in HEADER_HINTS.items():
            if role in found:
                continue
            if any(low == h or low.startswith(h) for h in hints):
                found[role] = i
                break
    return found if len(found) == 4 else {}


def score(cells, nums, order):
    """Given 4 ints in `order`, compare implied sens/spec to printed pcts."""
    tp, fp, fn, tn = (nums[order.index(r)] for r in ("tp", "fp", "fn", "tn"))
    n1, n0 = tp + fn, fp + tn
    if n1 < 3 or n0 < 3:
        return None
    pcts = [float(m.group(1)) / 100 for c in cells for m in PCT.finditer(c)]
    if len(pcts) < 2:
        return None
    sens, spec = tp / n1, tn / n0
    best = None
    for s_rep, c_rep in itertools.permutations(pcts[:4], 2):
        d = max(abs(sens - s_rep), abs(spec - c_rep))
        if best is None or d < best[0]:
            best = (d, s_rep, c_rep)
    return {"cells": [tp, fp, fn, tn], "sens": sens, "spec": spec,
            "sens_rep": best[1], "spec_rep": best[2], "max_diff": best[0]}


def audit_table(t):
    out = {"label": t["label"], "rows": []}
    header = {}
    for cells in t["rows"]:
        texts = [c[0] for c in cells]
        tags = [c[1] for c in cells]
        if all(tg == "th" for tg in tags):
            header = map_headers(cells) or header
            continue
        nums = [int(m.group(1)) for x in texts for m in [INT.match(x)] if m]
        if len(nums) < 4:
            out["rows"].append({"status": "unparseable", "text": " | ".join(texts)[:90]})
            continue
        four = nums[:4]

        cands = []
        if header and max(header.values()) < len(texts):
            vals, ok = [], True
            for r in ("tp", "fp", "fn", "tn"):
                m = INT.match(texts[header[r]]) if header[r] < len(texts) else None
                if not m:
                    ok = False
                    break
                vals.append(int(m.group(1)))
            if ok:
                s = score(texts, vals, ("tp", "fp", "fn", "tn"))
                if s:
                    cands.append((s["max_diff"], "header", s))

        for name, order in ORDERS.items():
            s = score(texts, four, order)
            if s:
                cands.append((s["max_diff"], name, s))

        if not cands:
            out["rows"].append({"status": "unparseable", "text": " | ".join(texts)[:90]})
            continue

        cands.sort(key=lambda x: x[0])
        d, name, s = cands[0]
        second = cands[1][0] if len(cands) > 1 else None
        hdr_conflict = bool(header) and name != "header" and d <= 0.02
        rec = {"via": name, **s, "text": " | ".join(texts)[:90]}
        if hdr_conflict:
            rec["header_conflict"] = True
        if d <= 0.02 and (second is None or second - d > 0.05):
            rec["status"] = "resolved"
        elif d <= 0.02:
            rec["status"] = "resolved_ambiguous_order"
        else:
            rec["status"] = "mismatch"
        out["rows"].append(rec)
    return out


if __name__ == "__main__":
    pmcids = sys.argv[1:]
    report = []
    for p in pmcids:
        try:
            root = ET.fromstring(fetch(p))
        except Exception as e:
            print(p, "ERR", e)
            continue
        tabs = [audit_table(t) for t in tables(root)]
        agg = {}
        for t in tabs:
            for r in t["rows"]:
                agg[r["status"]] = agg.get(r["status"], 0) + 1
        report.append({"pmcid": p, "tables": tabs, "summary": agg})
        print(f"{p}: {agg}")
    json.dump(report, open("extract_report.json", "w"), indent=1)
    tot = {}
    for r in report:
        for k, v in r["summary"].items():
            tot[k] = tot.get(k, 0) + v
    print("\nTOTAL:", tot)

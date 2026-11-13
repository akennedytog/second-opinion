"""Synthetic tests for the extraction layer.

These are unit tests of behaviour, not evidence of real-world performance.
"""
import sys, xml.etree.ElementTree as ET
sys.path.insert(0, "src")
from extract import tables, audit_table  # noqa: E402


def run(table_xml):
    root = ET.fromstring(f"<article><table-wrap>{table_xml}</table-wrap></article>")
    return audit_table(next(tables(root)))


def statuses(res):
    return [r["status"] for r in res["rows"]]


def test_header_and_data_agree():
    res = run("""
      <table>
        <tr><th>Study</th><th>True positive</th><th>False positive</th>
            <th>False negative</th><th>True negative</th>
            <th>Sensitivity</th><th>Specificity</th></tr>
        <tr><td>Smith 2020</td><td>45</td><td>5</td><td>5</td><td>45</td>
            <td>90%</td><td>90%</td></tr>
      </table>""")
    assert statuses(res) == ["resolved"], statuses(res)


def test_header_contradicted_by_data_is_a_conflict_not_a_finding():
    # Header says TP,FP,FN,TN but the numbers only fit TP,TN,FP,FN.
    res = run("""
      <table>
        <tr><th>Study</th><th>True positive</th><th>False positive</th>
            <th>False negative</th><th>True negative</th>
            <th>Sensitivity</th><th>Specificity</th></tr>
        <tr><td>Jones 2021</td><td>12</td><td>19</td><td>5</td><td>4</td>
            <td>75%</td><td>79%</td></tr>
      </table>""")
    assert statuses(res) == ["header_conflict"], statuses(res)


def test_no_header_single_clean_hypothesis():
    res = run("""
      <table>
        <tr><td>Lee 2019</td><td>40</td><td>10</td><td>5</td><td>45</td>
            <td>89%</td><td>82%</td></tr>
      </table>""")
    # 40/45=88.9%, 45/55=81.8% under TP,FP,FN,TN; the other orders miss by >=8pp.
    assert statuses(res) == ["resolved_no_header"], statuses(res)


def test_no_header_two_plausible_orders_is_ambiguous():
    # Symmetric cells: several orders fit equally well -> must abstain.
    res = run("""
      <table>
        <tr><td>Symmetric 2022</td><td>30</td><td>30</td><td>30</td><td>30</td>
            <td>50%</td><td>50%</td></tr>
      </table>""")
    assert statuses(res) == ["ambiguous_order"], statuses(res)


def test_row_without_cells_is_unparseable():
    res = run("""
      <table>
        <tr><td>No Cells 2023</td><td>0.85</td><td>0.91</td></tr>
      </table>""")
    assert statuses(res) == ["unparseable"], statuses(res)


def test_header_present_but_no_percentages_abstains():
    res = run("""
      <table>
        <tr><th>Study</th><th>True positive</th><th>False positive</th>
            <th>False negative</th><th>True negative</th></tr>
        <tr><td>Silent 2024</td><td>20</td><td>2</td><td>2</td><td>20</td></tr>
      </table>""")
    assert statuses(res) == ["unparseable"], statuses(res)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print("ok:", fn.__name__)
    print(f"\n{len(fns)} tests passed")

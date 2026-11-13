"""Download the validation dataset from OSF.

We do not redistribute the file. The OSF project carries no explicit licence tag, so this
script fetches it at run time and tells you where it came from.
"""
import hashlib
import os
import urllib.request

FILE_ID = "6ae709891b3bd51ccf880d7b"
URL = f"https://osf.io/download/{FILE_ID}/"
DEST = "data/final_data.xlsx"
UA = {"User-Agent": "second-opinion/0.1"}


def main():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DEST):
        print(f"already present: {DEST}")
        return
    print(f"fetching {URL}")
    req = urllib.request.Request(URL, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r, open(DEST, "wb") as f:
        blob = r.read()
        f.write(blob)
    digest = hashlib.sha256(blob).hexdigest()
    print(f"wrote {DEST} ({len(blob):,} bytes)")
    print(f"sha256 {digest}")
    print()
    print("Source: Huang Z et al., JAMA Network Open 2026;9(10):e2640850")
    print("        doi:10.1001/jamanetworkopen.2026.40850  ·  osf.io/pb3q2")


if __name__ == "__main__":
    main()

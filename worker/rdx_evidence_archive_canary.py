#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,pathlib,urllib.request

SRC_REPO="dmaillot95-ui/cerebron-farm-72-reality-evidence-gate"
SRC_COMMIT="2ccb94d3161658499fe2c8cbce2313839645290b"
SRC_PATH="receipts/rdx-memory-evidence-review-36149593919.json"
EXPECTED_RESULT_SHA="3b925348d4a04b11ff54d5472a5a3cd52b83af10ea188c8c50222b341caf5aee"

def main():
    url=f"https://raw.githubusercontent.com/{SRC_REPO}/{SRC_COMMIT}/{SRC_PATH}"
    with urllib.request.urlopen(url,timeout=30) as r:
        raw=r.read()
    source_file_sha=hashlib.sha256(raw).hexdigest()
    doc=json.loads(raw)
    tampered=bytearray(raw)
    if tampered:
        tampered[-1]=(tampered[-1]+1)%256
    tamper_sha=hashlib.sha256(bytes(tampered)).hexdigest()
    checks={
      "source_schema":doc.get("schema")=="F72_RDX_MEMORY_EVIDENCE_REVIEW_V1",
      "source_review_pass":doc.get("review_pass") is True,
      "source_result_sha":doc.get("result_sha256")==EXPECTED_RESULT_SHA,
      "source_global_f72_still_fail":doc.get("global_f72_gate")=="FAIL",
      "source_gold_locked":doc.get("gold_released") is False,
      "source_training_locked":doc.get("training_released") is False,
      "content_address_sha64":len(source_file_sha)==64,
      "tamper_changes_address":tamper_sha!=source_file_sha
    }
    ok=all(checks.values())
    archive={
      "schema":"F119_RDX_EVIDENCE_ARCHIVE_CANARY_V1",
      "status":"PASS" if ok else "FAIL",
      "farm_id":119,
      "role":"EVIDENCE_ARCHIVE",
      "source":{
        "repo":SRC_REPO,
        "commit":SRC_COMMIT,
        "path":SRC_PATH,
        "embedded_result_sha256":doc.get("result_sha256")
      },
      "source_file_sha256":source_file_sha,
      "archive_id":"F119:RDX_EVIDENCE:"+source_file_sha,
      "provenance_preserved":True,
      "checks":checks,
      "training_executed":False,
      "weights_changed":False,
      "claim_ceiling":"PINNED_SOURCE_CONTENT_ADDRESS_AND_PROVENANCE_ARCHIVE_CANARY_ONLY_NOT_EXTERNAL_INDEPENDENT_EVIDENCE"
    }
    archive["receipt_sha256"]=hashlib.sha256(json.dumps(archive,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    pathlib.Path("artifacts").mkdir(exist_ok=True)
    pathlib.Path("artifacts/rdx_evidence_archive_canary.json").write_text(json.dumps(archive,indent=2)+"\n")
    print(json.dumps({"status":archive["status"],"archive_id":archive["archive_id"],"receipt_sha256":archive["receipt_sha256"]},sort_keys=True))
    if not ok: raise SystemExit(2)

if __name__=="__main__":
    main()

#!/usr/bin/env python3
"""Record the addition of Wang et al. 2016 (J. Phys. D 49, 225102) to the T3 literature record.

Seen in the 14 Oct 2026 reference audit and held for the operator, who asked on
14 Oct 2026 (issue 55) for it to be included. Two series were added to
series.json: the Ge-Sn interdiffusion activation energy in strained Ge/Ge0.9Sn0.1
multiple quantum wells (1.21 eV, D0 2.9e-7 cm2/s, fit over 380-450 C) and the
interdiffusion onset (none at 300 C or below, observed at 380 C and above).
The article is closed; values come from its abstract and from the open review
of Xia (arXiv:1901.10105, eq. 11, ref. 102). Both series carry the label
'metastable film, anneals below about 650 C'.
"""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); MT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(MT, "pilot", "src"))
from ledger import Ledger  # noqa: E402
led = Ledger(os.path.join(MT, "phase_c", "ledger_campaign.jsonl"))
assert not any(e["payload"].get("op_id") == "add-source-wang2016" for e in led.entries)
sha = lambda p: hashlib.sha256(open(os.path.join(MT, p), "rb").read()).hexdigest()
fs = ["p4_tskg/T3_insitu/series.json", "p4_tskg/T3_insitu/sources.csv", "p4_tskg/T3_insitu/add_wang2016.py"]
e = led.append("shard_operation", {"op": "annotate", "op_id": "add-source-wang2016",
    "files_sha256": {f: sha(f) for f in fs},
    "source": {"doi": "10.1088/0022-3727/49/22/225102", "secondary": "arXiv:1901.10105 (Xia review, eq. 11)"},
    "series_added": ["wang2016_EA_GeSnMQW_lowT_1", "wang2016_interdiff_onset_GeSnMQW_2"],
    "label": "metastable film, anneals below about 650 C",
    "trigger": "reference audit 2026-10-14 (seen, not added); operator request issue 55, 2026-10-14",
    "consequence": "Ge-rich measured Ea set grows 6 -> 7; low-temperature film group 1.13-1.81 eV unchanged in span; "
                   "first measured diffusivity inside 380-450 C replaces the 400 C extrapolation as the contact-anneal number",
    "statement": "Wang 2016 Ge-Sn interdiffusion (1.21 eV, Ge/Ge0.9Sn0.1 MQW) added to the P4 literature record"})
assert led.verify_chain(); print(e["seq"])

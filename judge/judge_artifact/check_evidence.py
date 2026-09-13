#!/usr/bin/env python3
"""Read-only public-evidence wrapper for the frozen Incident Twins investigator.

Only --evidence, --model, and optional --anchor are read as data. No sibling
search, runtime execution, fixture lookup or private reference verification.
"""
import argparse
import json
from pathlib import Path

TRUST_ASSUMPTIONS = [
    "Fixed Incident Twins model/schema only: closed registered root/child tasks and resource bindings, no unmodeled retries or effects.",
    "Trusted tool/controller records and local causal order; raw trace generation and deployment completeness are not proved by this semantic API.",
    "Absence-based source closure requires the corresponding source channel plus correctly bound complete coverage through H, unless terminal/structural facts suffice.",
    "Coverage is a trusted in-process call-site assertion: instrumentation must be enabled and collection must follow recorded H; this wrapper cannot authenticate these facts.",
    "An integrity anchor is separately trusted; integrity failure proves neither containment nor violation. Co-located anchor replacement is outside this assumption.",
    "An ESTABLISHED result is limited to the open-left, closed-right interval; pending work may commit after H. It is not authorization to resume or proof of quiescence.",
]


def evaluate(evidence, model, anchor=None, max_histories=None):
    from incident_twins.instruments import investigate
    if not isinstance(evidence, dict) or not isinstance(model, dict):
        raise ValueError("evidence and public model must be JSON objects")
    if anchor is not None and not isinstance(anchor, dict):
        raise ValueError("trusted anchor must be a JSON object")
    answer = investigate(evidence, model, anchor=anchor, max_histories=max_histories)
    payload = evidence.get("payload", evidence)
    if not isinstance(payload, dict):
        payload = {}
    result = {"schema":"incident-twins-public-check/1", "verdict":answer.get("verdict"),
        "analysis_status":answer.get("analysis_status"),
        "scoped_claim":payload.get("claim"), "claim_is_declared_input":True,
        "compatible_count":answer.get("compatible_count"), "counts_q":answer.get("counts_q"),
        "universe":answer.get("universe"), "error":answer.get("error"),
        "conclusive":answer.get("analysis_status")=="complete" and answer.get("verdict") in ("ESTABLISHED","REFUTED"),
        "trust_assumptions":TRUST_ASSUMPTIONS,
        "advice":None, "runtime_ns":answer.get("runtime_ns")}
    if answer.get("verdict") == "UNDETERMINED":
        result["advice"] = {"kind":"fixed-study-schema advice; not synthesized or generally minimal",
            "request":"Obtain trusted task/run/resource-bound executor terminal records. If relying on absent terminal records for unfinished work, obtain valid source coverage through this H together with the executor channel. A valid terminal cancellation may already suffice without coverage."}
    return result


def read_input(path):
    with Path(path).open("rb") as handle:
        return json.load(handle)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--model',type=Path,required=True)
    parser.add_argument('--anchor',type=Path)
    parser.add_argument('--max-histories',type=int,help='optional bounded computation control; interruption never proves absence')
    args=parser.parse_args(argv)
    try:
        result=evaluate(read_input(args.evidence),read_input(args.model),
                        read_input(args.anchor) if args.anchor else None,args.max_histories)
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        result={"schema":"incident-twins-public-check/1","verdict":None,"analysis_status":"error",
                "conclusive":False,"error":{"kind":"public_input_error","message":str(exc)},
                "trust_assumptions":TRUST_ASSUMPTIONS}
    print(json.dumps(result,sort_keys=True))
    return 2 if result['analysis_status']=='error' else 0


if __name__=='__main__':
    raise SystemExit(main())

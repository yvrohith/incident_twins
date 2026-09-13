"""Four semantic verdicts with an independent analysis-completeness status."""
import time

from .model import enumerate_histories, property_q
from .observations import matches, observation_constraints


def analyze(bundle, public_model, max_histories=None, anchor=None):
    """Investigate only supplied evidence and public structure, never an oracle.

    Integrity envelopes must be verified and unwrapped by their collection API;
    this semantic API accepts the resulting ordinary bundle. The optional anchor
    argument is reserved, and rejected rather than silently pretending to check it.
    """
    started = time.perf_counter_ns()
    result = {"verdict": None, "analysis_status": "error", "compatible_count": 0,
              "counts_q": {"true": 0, "false": 0}, "universe": None}
    try:
        if anchor is not None:
            raise ValueError("verify and unwrap integrity before calling the semantic API")
        constraints = observation_constraints(bundle, public_model)
        histories, stats = enumerate_histories(public_model, max_histories)
        result["universe"] = stats
        for history in histories:
            if matches(history, constraints):
                result["compatible_count"] += 1
                result["counts_q"]["true" if property_q(history, bundle["claim"]) else "false"] += 1
        yes, no = result["counts_q"]["true"], result["counts_q"]["false"]
        result["analysis_status"] = "complete" if stats["complete"] else "incomplete"
        if yes and no:
            result["verdict"] = "UNDETERMINED"
        elif stats["complete"]:
            result["verdict"] = "ESTABLISHED" if yes else "REFUTED" if no else "INCONSISTENT"
    except (TypeError, ValueError, KeyError) as error:
        result["error"] = {"kind": "parse_or_contract_error", "message": str(error)}
    result["runtime_ns"] = time.perf_counter_ns() - started
    return result

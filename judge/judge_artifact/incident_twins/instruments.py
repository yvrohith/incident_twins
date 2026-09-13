"""Evidence profiles and exhaustive search over the frozen four-channel menu."""
import copy
import itertools
import time
from .contracts import CHANNELS, canonical, digest


def wrap_integrity(bundle):
    payload = copy.deepcopy(bundle)
    anchor = {"algorithm": "sha256", "payload_digest": digest(payload),
              "trust": "separate local collector anchor; not secure against replacing both files"}
    return {"payload": payload, "integrity": {"algorithm": "sha256", "digest": digest(payload)}}, anchor


def investigate(bundle, public_model, *, anchor=None, max_histories=None):
    from .verdicts import analyze
    if "integrity" in bundle:
        if anchor is None or bundle.get("integrity", {}).get("digest") != anchor.get("payload_digest") or digest(bundle.get("payload")) != anchor.get("payload_digest"):
            return {"verdict": None, "analysis_status": "error", "error": "integrity_failure"}
        bundle = bundle["payload"]
    return analyze(bundle, public_model, max_histories=max_histories)


def profile_bundle(native, channels, profile, selected):
    bundle = copy.deepcopy(native)
    if profile == "native":
        return bundle, None
    if profile == "integrity_only":
        return wrap_integrity(bundle)
    if profile == "augmented":
        bundle["channels"] = {name: channels[name] for name in selected}
        return bundle, None
    raise ValueError(profile)


def powerset():
    return [tuple(s) for n in range(len(CHANNELS) + 1) for s in itertools.combinations(CHANNELS, n)]


def select_channels(reference_workload, cost_workload):
    """Complete evidence-compatibility check, including missing-coverage possibilities.

    reference_workload: [(native_bundle_template, public_model)]. Templates carry
    measured native prefix bytes; the finite graph supplies possible terminal facts.
    cost_workload: actual runtime channel dictionaries from the two development pairs.
    """
    from .model import enumerate_histories, property_q
    from .observations import matches, observation_constraints, semantic_observation
    started = time.perf_counter_ns()
    costs = {name: sum(len(canonical({name: ch[name]})) for ch in cost_workload) for name in CHANNELS}
    records = []
    cached = []
    for template, model in reference_workload:
        histories, stats = enumerate_histories(model)
        cached.append((template, model, histories, stats))
    for subset in powerset():
        collisions = 0
        checked = 0
        for template, model, histories, stats in cached:
            # Native delegated receipts supply their own complete terminal channel.
            # Template construction for each h is explicit semantic test data,
            # never passed off as a real native runtime export.
            for history in histories:
                observation = semantic_observation(history, model, subset)
                bundle = copy.deepcopy(template)
                bundle["channels"] = observation["channels"]
                if model["mechanism"] == "delegated":
                    terminal = [e for e in history["events"] if e["kind"] in ("commit", "cancel")]
                    for messages in bundle["native"]["messages"].values():
                        for message in messages:
                            for part in message["parts"]:
                                if part["part_kind"] == "tool-return" and part["tool_name"] == "execute_child_artifacts":
                                    part["content"]["terminal_records"] = terminal
                constraints = observation_constraints(bundle, model)
                value = property_q(history, bundle["claim"])
                for other in histories:
                    if property_q(other, bundle["claim"]) != value:
                        checked += 1
                        if matches(other, constraints):
                            collisions += 1
        records.append({"channels": list(subset), "cost_bytes": sum(len(canonical({name: ch[name] for name in subset})) for ch in cost_workload),
                        "remaining_opposite_compatibilities": collisions,
                        "opposite_checks": checked, "sufficient": collisions == 0})
    sufficient = [r for r in records if r["sufficient"]]
    best = min(sufficient, key=lambda r: (r["cost_bytes"], len(r["channels"]), tuple(r["channels"]))) if sufficient else None
    return {"schema": "incident-twins/1", "channel_costs_bytes": costs, "subsets": records,
            "selected": None if best is None else best["channels"],
            "reference_universes": [stats for _, _, _, stats in cached],
            "runtime_ns": time.perf_counter_ns() - started,
            "cost_workload": "four executed development continuations/full runs",
            "scope": "conditional bounded semantic model; not a minimum over arbitrary logging designs"}

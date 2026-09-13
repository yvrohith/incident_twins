"""Evidence-only semantic adapter; complete raw export equality is separate.

Native timestamps/spans are retained in bundles; this parser makes no claim of
generating arbitrary native traces. It reads trusted registered tool returns,
not agent text. Missing source closure is a set of possible collection outcomes.
"""
import hashlib

from .contracts import CHANNELS, CLAIM, POLICY, SCHEMA, canonical
from .model import normalize_model

EVENT_KEYS = ("kind", "tick", "task", "owner", "resource")


def semantic_observation(history, public_model, channels=()):
    model = normalize_model(public_model)
    events = history["events"]
    terminal = [dict(e) for e in events if e["kind"] in ("commit", "cancel")]
    receipts = [{"accepted": True, **{k: t[k] for k in ("task", "owner", "resource")}}
                for t in model["tasks"]]
    native = {"receipts": receipts}
    if model["mechanism"] == "delegated":
        native.update(terminal_records=terminal, terminal_records_complete=True)
    values = {
        "executor": terminal,
        "lineage": [dict(e) for e in events if e["kind"] in ("enqueue", "delegate")],
        "destination": [{**e, "sha256": hashlib.sha256(b"dummy artifact").hexdigest()}
                        for e in terminal if e["kind"] == "commit"],
        "coverage": {"through": 100, "root": "root", "resources": ["approved", "other"],
                     "executor_complete": True, "destination_complete": True,
                     "lineage_complete": True, "registered_tasks": [t["task"] for t in model["tasks"]],
                     "source_drained_to_horizon": True},
    }
    return {"native": native,
            "controller": [dict(e) for e in events if e["kind"] in
                           ("delegate", "stop_request", "parent_stop_confirmed", "horizon")],
            "channels": {name: values[name] for name in channels}}


def _tool_contents(native):
    messages = native.get("messages", {})
    if not isinstance(messages, dict):
        raise ValueError("native messages must be grouped by registered run")
    for run, records in messages.items():
        if not isinstance(records, list):
            raise ValueError("native message group must be a list")
        calls = {}
        for record in records:
            for part in record.get("parts", []):
                if part.get("part_kind") == "tool-call":
                    calls[part.get("tool_call_id")] = part.get("tool_name")
                if part.get("part_kind") != "tool-return":
                    continue
                name = part.get("tool_name")
                if name not in ("enqueue_artifacts", "delegate_artifacts", "execute_child_artifacts"):
                    continue
                if calls.get(part.get("tool_call_id")) != name:
                    raise ValueError("registered tool return has no matching native call binding")
                if part.get("outcome", "success") != "success":
                    continue
                content = part.get("content")
                if not isinstance(content, dict):
                    raise ValueError("registered tool return must contain a JSON object")
                yield run, name, content


def observation_constraints(bundle, public_model):
    """Parse once for exhaustive matching; no file operations or fixture access."""
    model = normalize_model(public_model)
    if not isinstance(bundle, dict):
        raise TypeError("evidence must be a JSON object, never a path")
    if bundle.get("schema") != SCHEMA:
        raise ValueError("unsupported evidence schema")
    if bundle.get("claim") != CLAIM:
        raise ValueError("claim differs from the frozen interval/scope contract")
    native, controller, channels = (bundle.get(k) for k in ("native", "controller", "channels"))
    if not isinstance(native, dict) or not isinstance(controller, list) or not isinstance(channels, dict):
        raise ValueError("evidence native/controller/channels have invalid types")
    if set(channels) - set(CHANNELS):
        raise ValueError("unsupported runtime channel")
    receipts, terminals, complete_tasks = [], [], set()
    for run, tool, content in _tool_contents(native):
        if (tool == "execute_child_artifacts" and run != "child") or (tool != "execute_child_artifacts" and run != "root"):
            raise ValueError("registered tool execution has wrong native run binding")
        received = content.get("receipts", [])
        if not isinstance(received, list):
            raise ValueError("receipts must be a list")
        for receipt in received:
            if receipt not in receipts:
                receipts.append(receipt)
        if tool == "execute_child_artifacts":
            records = content.get("terminal_records", [])
            if not isinstance(records, list):
                raise ValueError("terminal_records must be a list")
            terminals.extend(records)
            if content.get("terminal_records_complete") is True:
                complete_tasks.update(r["task"] for r in received)
    # The full native trace remains in the retained evidence. Only registered
    # tool facts participate in this explicitly documented semantic abstraction.
    return {"model": model, "receipts": receipts, "native_terminals": terminals,
            "native_complete_tasks": complete_tasks, "controller": controller, "channels": channels}


def _records_match(observed, expected, complete=False, destination=False):
    if not isinstance(observed, list) or any(not isinstance(e, dict) for e in observed):
        raise ValueError("event channel must be a list of objects")
    # Destination digests bind dummy content; they are not erased to gain a match.
    if destination:
        digest = hashlib.sha256(b"dummy artifact").hexdigest()
        if any(e.get("sha256") != digest for e in observed):
            return False
    if complete:
        return canonical(observed) == canonical(expected)
    return all(record in expected for record in observed)


def matches(history, constraints, public_model=None):
    model = constraints["model"] if public_model is None else normalize_model(public_model)
    expected = semantic_observation(history, model, CHANNELS)
    if canonical(constraints["controller"]) != canonical(expected["controller"]):
        return False
    if any(receipt not in expected["native"]["receipts"] for receipt in constraints["receipts"]):
        return False
    terminal = expected["channels"]["executor"]
    if not _records_match(constraints["native_terminals"], terminal):
        return False
    complete_tasks = constraints["native_complete_tasks"]
    if complete_tasks:
        observed = [e for e in constraints["native_terminals"] if e.get("task") in complete_tasks]
        restricted = [e for e in terminal if e["task"] in complete_tasks]
        if canonical(observed) != canonical(restricted):
            return False
    channels = constraints["channels"]
    coverage = channels.get("coverage", {})
    if not isinstance(coverage, dict):
        raise ValueError("coverage must be an object")
    through = coverage.get("through", -1)
    resources = coverage.get("resources", [])
    registered = coverage.get("registered_tasks", [])
    if not isinstance(through, int) or not isinstance(resources, list) or not isinstance(registered, list):
        raise ValueError("coverage horizon/resources/registered_tasks have invalid types")
    relevant = (coverage.get("root") == CLAIM["root"] and through >= CLAIM["horizon"]
                and coverage.get("source_drained_to_horizon") is True)
    for name in ("executor", "destination", "lineage"):
        if name in channels:
            if not _records_match(channels[name], expected["channels"][name],
                                  destination=name == "destination"):
                return False
            if relevant and coverage.get(f"{name}_complete") is True:
                def covered(event):
                    if event.get("kind") == "delegate":
                        return name == "lineage" and event.get("parent") == coverage["root"]
                    return event.get("task") in registered and event.get("resource") in resources
                observed_closed = [e for e in channels[name] if covered(e)]
                expected_closed = [e for e in expected["channels"][name] if covered(e)]
                if canonical(observed_closed) != canonical(expected_closed):
                    return False
    return True


def compatible(history, bundle, public_model):
    return matches(history, observation_constraints(bundle, public_model))

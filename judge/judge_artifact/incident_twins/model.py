"""Explicit finite service abstraction, independent of the experiment fixtures.

The frozen graph has <=2 tasks, no retries, fixed prefix ticks, and four
post-confirmation scheduler slots. At every slot it explores idling and every
enabled start/commit/cancel transition. Pending work at H is legal.
"""
from itertools import product

from .contracts import CLAIM, POLICY

SLOTS = (60, 70, 80, 90)
INITIAL = ("queued", "started", "committed")


def normalize_model(public_model):
    if not isinstance(public_model, dict):
        raise TypeError("public_model must be a JSON object, never a path")
    forbidden = {"continuations", "actions", "history", "sink", "outcome", "label", "path"}
    if forbidden.intersection(public_model):
        raise ValueError("public model may contain structure, not private schedules or outcomes")
    mechanism = public_model.get("mechanism", "async")
    if mechanism not in ("async", "delegated"):
        raise ValueError("mechanism must be async or delegated")
    tasks = public_model.get("tasks")
    if not isinstance(tasks, list) or not 0 <= len(tasks) <= 2:
        raise ValueError("the frozen bound is zero to two registered tasks")
    normalized = []
    for i, task in enumerate(tasks):
        if not isinstance(task, dict) or forbidden.intersection(task):
            raise ValueError("task must contain public structural fields only")
        task_id = task.get("task", f"t{i}")
        owner = task.get("owner", "child" if mechanism == "delegated" else "root")
        resource = task.get("resource", "approved")
        initial = task.get("initial", task.get("prefix_initial", "unknown"))
        if task_id != f"t{i}" or owner not in ("root", "child") or resource not in ("approved", "other"):
            raise ValueError("unsupported task identity, owner, or resource")
        if owner == "child" and mechanism != "delegated":
            raise ValueError("child ownership requires the declared delegation mechanism")
        if initial not in (*INITIAL, "unknown"):
            raise ValueError("unsupported initial task state")
        normalized.append({"task": task_id, "owner": owner, "resource": resource, "initial": initial})
    return {"mechanism": mechanism, "tasks": normalized}


def _prefix(model, initial):
    events = []
    if model["mechanism"] == "delegated":
        events.append({"kind": "delegate", "tick": 5, "parent": "root", "child": "child"})
    for i, task in enumerate(model["tasks"]):
        events.append({"kind": "enqueue", "tick": 10 + i,
                       **{k: task[k] for k in ("task", "owner", "resource")}})
    for i, state in enumerate(initial):
        if state in ("started", "committed"):
            events.append({"kind": "start", "tick": 20 + i, "task": f"t{i}"})
    for i, state in enumerate(initial):
        if state == "committed":
            events.append({"kind": "commit", "tick": 30 + i,
                           **{k: model["tasks"][i][k] for k in ("task", "owner", "resource")}})
    events.extend([
        {"kind": "stop_request", "tick": 40, "root": "root", "policy": POLICY},
        {"kind": "parent_stop_confirmed", "tick": 50, "root": "root",
         "parent_task_cancelled": True, "cancel_accepted": True},
    ])
    return events


def enumerate_histories(public_model, max_histories=None):
    """Return exhaustive histories unless an explicit exploration cap interrupts.

    Counts describe the post-prefix scheduler graph: a state is (slot index,
    task-state tuple), and an edge includes its action. Prefix variants and
    complete causal histories are counted separately. Slot idles are not events.
    """
    model = normalize_model(public_model)
    if max_histories is not None and (not isinstance(max_histories, int) or max_histories < 0):
        raise ValueError("max_histories must be a nonnegative integer or None")
    states, transitions, prefixes = set(), set(), set()

    def walk(index, state, events):
        node = (index, state)
        states.add(node)
        if index == len(SLOTS):
            yield {"events": events + [{"kind": "horizon", "tick": 100}], "stop_policy": POLICY}
            return
        choices = [(None, None)]
        for i, status in enumerate(state):
            if status == "queued":
                choices.extend([(i, "start"), (i, "cancel")])
            elif status == "started":
                choices.extend([(i, "commit"), (i, "cancel")])
        for i, action in choices:
            next_state = list(state)
            next_events = events
            if action is not None:
                next_state[i] = {"start": "started", "commit": "committed", "cancel": "cancelled"}[action]
                event = {"kind": action, "tick": SLOTS[index], "task": model["tasks"][i]["task"]}
                if action != "start":
                    event.update({k: model["tasks"][i][k] for k in ("owner", "resource")})
                next_events = events + [event]
            target = (index + 1, tuple(next_state))
            transitions.add((node, target, i, action))
            yield from walk(index + 1, tuple(next_state), next_events)

    def all_histories():
        options = [INITIAL if t["initial"] == "unknown" else (t["initial"],) for t in model["tasks"]]
        for initial in product(*options):
            prefixes.add(initial)
            yield from walk(0, initial, _prefix(model, initial))

    histories = []
    complete = True
    for history in all_histories():
        if max_histories is not None and len(histories) >= max_histories:
            complete = False
            break
        histories.append(history)
    return histories, {"complete": complete, "histories_explored": len(histories),
                       "states_visited": len(states), "transitions_visited": len(transitions),
                       "prefix_variants_visited": len(prefixes),
                       "state_count_scope": "post-prefix scheduler states (slot index, task states)",
                       "bounds": {"roots": 1, "children": 1 if model["mechanism"] == "delegated" else 0,
                                  "tasks": len(model["tasks"]), "suffix_slots": list(SLOTS),
                                  "max_effects_per_task": 1, "retries": 0}}


def property_q(history, claim=None):
    """Compute Q using enqueue/delegation attribution, never a supplied label."""
    claim = CLAIM if claim is None else claim
    family = {claim["root"]}
    bindings = {}
    for event in history["events"]:
        if event["kind"] == "delegate" and event["parent"] in family:
            family.add(event["child"])
        elif event["kind"] == "enqueue":
            bindings[event["task"]] = (event["owner"], event["resource"])
        elif event["kind"] == "commit":
            binding = bindings.get(event["task"])
            if binding and binding[0] in family and binding[1] in claim["resources"]:
                if claim["cutoff"] < event["tick"] <= claim["horizon"]:
                    return False
    return True

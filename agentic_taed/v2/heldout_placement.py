"""Two held-out email topics and an independently run development attack check.

Protocol: AgentDojo system_message is selected in advance, regardless of development
ASR. Keep zero-success attacks and report the floor. No checkpoint-free TAED arm.
"""
import argparse
import json
import random
import time
from importlib.metadata import version
from pathlib import Path

from agentdojo.agent_pipeline import AgentPipeline, InitQuery, SystemMessage
from agentdojo.agent_pipeline.tool_execution import ToolsExecutionLoop, ToolsExecutor
from agentdojo.attacks.baseline_attacks import SystemMessageAttack
from agentdojo.task_suite.load_suites import get_suite

from .email_placement import ARMS, PLACEMENTS, SYSTEM, Trace, render
from .provider import make_llm

# Same = constructed append to the sole fact-bearing email. Separate = the
# topic's native injection carrier. No claims of natural attack prevalence.
CARRIERS = {
    "user_task_16": ("26", "31", "463820"),
    "user_task_22": ("9", "29", "asfbuy3y2cdaqhvei"),
    "user_task_14": ("16", "27", "June 10th 2024 at 1 PM"),
    "user_task_17": ("20", "32", "island trailhead at 8 AM"),
}


def placement_fixture(suite, task_id, placement, payload):
    env = suite.load_and_inject_default_environment({})
    same, separate, fact = CARRIERS[task_id]
    sources = [key for key, email in env.inbox.emails.items() if fact in email.body]
    if sources != [same]:
        raise ValueError(f"{task_id}: unexpected literal evidence sources {sources}")
    target = {"same": same, "separate": separate, "clean": None}[placement]
    if target is not None:
        env.inbox.emails[target].body += payload
    return env, target


def live(args, suite, task, attack, payload):
    # Fail before creating an output file when no endpoint has been configured.
    from .provider import credentials
    if not credentials(args.provider):
        raise SystemExit("Configure the selected provider before requesting a live run.")
    if not args.model or not args.out:
        raise SystemExit("Live mode requires --model and a new --out JSONL path.")
    failures = 0
    with args.out.open("x") as output:
        for seed in ([args.seed] if args.seed is not None else [11, 29, 47]):
            cells = ([("same", "none"), ("separate", "none")] if args.phase == "development"
                     else [(p, a) for p in PLACEMENTS for a in ARMS])
            random.Random(seed).shuffle(cells)
            for placement, arm in cells:
                env, target = placement_fixture(suite, task.ID, placement, payload)
                llm, meter = make_llm(args.provider, args.model, seed, timeout=args.timeout)
                formatter = lambda result: render(result, arm, target, payload)
                pipeline = AgentPipeline([SystemMessage(SYSTEM), InitQuery(), llm,
                                          ToolsExecutionLoop([ToolsExecutor(formatter), llm], max_iters=8)])
                pipeline.name = "placement-" + arm
                trace = Trace()
                row = dict(kind="live", agentdojo=version("agentdojo"), benchmark="v1.2.2",
                           task=task.ID, attack=attack.ID if target else None,
                           placement=placement, arm=arm, seed=seed, model=args.model,
                           carrier=target, phase=args.phase, attack_template="system_message",
                           provider=args.provider, payload=payload if target else None)
                started = time.perf_counter()
                try:
                    with trace:
                        u, a = suite.run_task_with_pipeline(pipeline, task, attack if target else None, {}, environment=env)
                    row.update(status="completed", utility=u, attack_success=a if target else None,
                               secure_completion=(u and not a) if target else None)
                except Exception as exc:
                    failures += 1
                    row.update(status="error", error_type=type(exc).__name__, error=str(exc))
                row.update(seconds=time.perf_counter()-started, calls=meter.calls, trace=trace.messages)
                output.write(json.dumps(row) + "\n")
                output.flush()
                if row["status"] == "error" and not any(c.get("usage") for c in meter.calls):
                    raise SystemExit("First unsuccessful provider episode saved; check endpoint and model.")
    if failures:
        raise SystemExit(f"{failures} episodes had errors; inspect JSONL before aggregation.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("development", "evaluation"), required=True)
    parser.add_argument("--task", choices=CARRIERS, required=True)
    parser.add_argument("--seed", type=int, choices=(11, 29, 47), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if (args.phase == "development") != (args.task in ("user_task_16", "user_task_22")):
        parser.error("task does not belong to the requested split")
    args.model, args.provider, args.timeout = "qwen3:8b", "openai-compatible", 600
    suite = get_suite("v1.2.2", "workspace")
    task = suite.get_user_task_by_id(args.task)
    attack = suite.get_injection_task_by_id("injection_task_0")
    template = SystemMessageAttack(suite, AgentPipeline([])).jailbreak
    payload = "\n\n" + template.format(goal=attack.GOAL)
    live(args, suite, task, attack, payload)


if __name__ == "__main__":
    main()

import argparse
import os
import json
import logging
from datetime import datetime

from .config import Config
from .budget import BudgetManager, BudgetExhaustedError
from .providers.mock import MockLLMProvider, MockTranscriptionProvider
from .evidence.registry import EvidenceRegistry
from .evidence.loader import EvidenceLoader
from .evidence.reliability import ReliabilityChecker
from .learning.hypotheses import HypothesisGenerator
from .learning.tester import RuleTester
from .translate.planner import TranslationPlanner
from .translate.translator import Translator
from .verify import Verifier
from .escalation.review_queue import ReviewQueue
from .memory.dependency_graph import DependencyGraph
from .memory.state import PipelineState
from .replan.corrections import CorrectionHandler
from .report.srt import write_srt
from .report.jsonl import write_jsonl
from .report.final_report import write_final_report


def setup_logging(output_dir: str):
    """Setup structured JSON logging to run_log.jsonl."""
    os.makedirs(output_dir, exist_ok=True)
    log_path = os.path.join(output_dir, "run_log.jsonl")

    class JsonlHandler(logging.Handler):
        def __init__(self, filepath):
            super().__init__()
            self.filepath = filepath
            self.fh = open(filepath, "w", encoding="utf-8")

        def emit(self, record):
            entry = {
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "stage": getattr(record, "stage", "general"),
                "message": record.getMessage(),
            }
            self.fh.write(json.dumps(entry) + "\n")
            self.fh.flush()

    handler = JsonlHandler(log_path)
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
    return log_path


def run_pipeline(args):
    output_dir = "sample_run"
    log_path = setup_logging(output_dir)
    logger = logging.getLogger("nadi9")

    config = Config(
        max_model_calls=args.max_model_calls,
        max_tool_calls=args.max_tool_calls,
        data_dir=args.data,
    )
    budget = BudgetManager(config.max_model_calls, config.max_tool_calls)
    llm = MockLLMProvider(config.data_dir)

    # ─── Stage 1: Evidence Inspection ───
    logger.info("Stage 1: Loading evidence", extra={"stage": "evidence"})
    registry = EvidenceRegistry(config.precedence)
    loader = EvidenceLoader(registry, config.data_dir)
    load_summary = loader.load_all()
    logger.info(f"Loaded {load_summary}", extra={"stage": "evidence"})

    # Cross-check reliability
    checker = ReliabilityChecker(registry)
    conflicts, quarantined_ids = checker.check_all()
    logger.info(
        f"Found {len(conflicts)} conflicts, quarantined {len(quarantined_ids)} entries",
        extra={"stage": "evidence"},
    )

    # ─── Stage 2+3: Hypothesis Generation & Testing ───
    logger.info("Stage 2: Generating hypotheses", extra={"stage": "learning"})
    hypo_gen = HypothesisGenerator(llm, registry, budget)
    rules = hypo_gen.generate_rules()

    logger.info("Stage 3: Testing hypotheses", extra={"stage": "learning"})
    tester = RuleTester(registry)
    tested_rules = tester.test_rules(rules)
    logger.info(
        f"Rules: {len(tested_rules)} total, "
        f"{sum(1 for r in tested_rules if r.status.value == 'SUPPORTED')} supported, "
        f"{sum(1 for r in tested_rules if r.status.value == 'UNSUPPORTED')} unsupported",
        extra={"stage": "learning"},
    )

    # ─── Stage 4: Load Episode & Planning ───
    logger.info("Stage 4: Planning", extra={"stage": "planning"})
    episode_path = os.path.join(config.data_dir, "episode.json")
    if os.path.exists(episode_path):
        with open(episode_path, "r", encoding="utf-8") as f:
            lines = json.load(f)
    else:
        lines = [{"id": "S001", "source_text": "Hello", "start": "00:00:01,000", "end": "00:00:03,000"}]

    planner = TranslationPlanner()
    plan = planner.plan(lines, registry, tested_rules)
    logger.info(f"Planned {len(plan)} lines, highest risk: {plan[0].risk_score if plan else 0}",
                extra={"stage": "planning"})

    # ─── Stage 5: Translation ───
    logger.info("Stage 5: Translation", extra={"stage": "translation"})
    dep_graph = DependencyGraph()
    translator = Translator(llm, budget, dep_graph)
    decisions = translator.translate(plan, tested_rules, registry)
    logger.info(f"Translated {len(decisions)} lines", extra={"stage": "translation"})

    # ─── Handle --inject-event if provided ───
    if hasattr(args, "inject_event") and args.inject_event:
        logger.info(f"Injecting event from {args.inject_event}", extra={"stage": "replan"})
        with open(args.inject_event, "r") as f:
            event = json.load(f)
        handler = CorrectionHandler(dep_graph)
        impacted = handler.handle_correction(event)
        logger.info(f"Correction impacted {len(impacted)} subtitles: {impacted}", extra={"stage": "replan"})

    # ─── Stage 6: Verification ───
    logger.info("Stage 6: Verification", extra={"stage": "verification"})
    verifier = Verifier(rules=tested_rules)
    final_decisions = []
    for d in decisions:
        vd = verifier.verify(d, registry)
        final_decisions.append(vd)

    # ─── Stage 7: Escalation ───
    logger.info("Stage 7: Escalation", extra={"stage": "escalation"})
    queue = ReviewQueue()
    queue.process_decisions(final_decisions, conflicts)

    # ─── Stage 8: Output ───
    logger.info("Stage 8: Writing outputs", extra={"stage": "output"})
    os.makedirs(output_dir, exist_ok=True)

    write_srt(final_decisions, os.path.join(output_dir, "subtitles.srt"))
    write_jsonl(final_decisions, os.path.join(output_dir, "subtitle_decisions.jsonl"))
    write_final_report(
        final_decisions,
        os.path.join(output_dir, "final_report.md"),
        conflicts=conflicts,
        quarantined_ids=quarantined_ids,
        rules=tested_rules,
        budget_usage={
            "model_calls": budget.model_calls,
            "max_model_calls": budget.max_model_calls,
            "tool_calls": budget.tool_calls,
            "max_tool_calls": budget.max_tool_calls,
        },
    )

    with open(os.path.join(output_dir, "learned_rules.json"), "w", encoding="utf-8") as f:
        json.dump([r.model_dump() for r in tested_rules], f, indent=2, default=str)

    with open(os.path.join(output_dir, "review_queue.json"), "w", encoding="utf-8") as f:
        json.dump(queue.get_queue(), f, indent=2, default=str)

    print(f"Run complete. Outputs in {output_dir}/")
    print(f"  Budget: {budget.model_calls}/{budget.max_model_calls} model calls, "
          f"{budget.tool_calls}/{budget.max_tool_calls} tool calls")
    print(f"  Evidence: {load_summary}")
    print(f"  Conflicts: {len(conflicts)}, Quarantined: {len(quarantined_ids)}")
    print(f"  Review queue: {len(queue.get_queue())} items")


def correct_command(args):
    """Apply a correction to an existing run."""
    with open(args.correction, "r") as f:
        event = json.load(f)

    # Load decisions to find dependencies
    decisions_path = os.path.join(args.run, "subtitle_decisions.jsonl")
    if not os.path.exists(decisions_path):
        print(f"No decisions found at {decisions_path}")
        return

    graph = DependencyGraph()
    # Rebuild graph from decisions
    from .memory.claims import SubtitleDecision
    with open(decisions_path, "r") as f:
        for line in f:
            dec = SubtitleDecision.model_validate_json(line.strip())
            for ev_id in dec.evidence:
                graph.add_dependency(ev_id, dec.subtitle_id)

    handler = CorrectionHandler(graph)
    impacted = handler.handle_correction(event)
    print(f"Correction applied. {len(impacted)} subtitles impacted: {impacted}")
    print("Unaffected lines were NOT reprocessed.")


def explain_command(args):
    """Trace one subtitle from source evidence to final output."""
    decisions_path = os.path.join(args.run, "subtitle_decisions.jsonl")
    if not os.path.exists(decisions_path):
        print(f"No decisions found at {decisions_path}")
        return

    from .memory.claims import SubtitleDecision
    with open(decisions_path, "r") as f:
        for line in f:
            dec = SubtitleDecision.model_validate_json(line.strip())
            if dec.subtitle_id == args.subtitle:
                print(f"\n{'='*60}")
                print(f"Subtitle: {dec.subtitle_id}")
                print(f"Source: {dec.source_text}")
                print(f"Nadi-9: {dec.nadi_9_text}")
                print(f"Decision: {dec.decision.value}")
                print(f"Confidence: {dec.confidence} ({dec.confidence_reason})")
                print(f"Evidence: {dec.evidence}")
                print(f"Assumptions: {dec.assumptions}")
                print(f"Conflicts: {dec.conflicts}")
                if dec.review_question:
                    print(f"Review question: {dec.review_question}")
                if dec.verification_results:
                    print(f"Verification issues: {dec.verification_results.issues}")
                print(f"{'='*60}\n")
                return

    print(f"Subtitle {args.subtitle} not found in {decisions_path}")


def report_command(args):
    """Display the final report."""
    report_path = os.path.join(args.run, "final_report.md")
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            print(f.read())
    else:
        print(f"No report found at {report_path}")


def main():
    parser = argparse.ArgumentParser(prog="nadi9", description="Nadi-9 Evidence-Grounded Subtitle Agent")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run the full pipeline")
    run_parser.add_argument("--data", required=True, help="Path to data/fixtures directory")
    run_parser.add_argument("--provider", default="mock", help="LLM provider (mock/anthropic/openai)")
    run_parser.add_argument("--max-model-calls", type=int, default=25)
    run_parser.add_argument("--max-tool-calls", type=int, default=50)
    run_parser.add_argument("--inject-event", help="Path to surprise event JSON file")

    correct_parser = subparsers.add_parser("correct", help="Apply correction to existing run")
    correct_parser.add_argument("--run", required=True, help="Path to run directory")
    correct_parser.add_argument("--correction", required=True, help="Path to correction JSON")

    explain_parser = subparsers.add_parser("explain", help="Explain a subtitle decision")
    explain_parser.add_argument("--run", required=True, help="Path to run directory")
    explain_parser.add_argument("--subtitle", required=True, help="Subtitle ID (e.g. S014)")

    report_parser = subparsers.add_parser("report", help="Display final report")
    report_parser.add_argument("--run", required=True, help="Path to run directory")

    args = parser.parse_args()

    if args.command == "run":
        run_pipeline(args)
    elif args.command == "correct":
        correct_command(args)
    elif args.command == "explain":
        explain_command(args)
    elif args.command == "report":
        report_command(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

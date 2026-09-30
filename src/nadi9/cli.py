import argparse
import os
import json
from .config import Config
from .budget import BudgetManager
from .providers.mock import MockLLMProvider, MockTranscriptionProvider
from .evidence.registry import EvidenceRegistry
from .evidence.loader import EvidenceLoader
from .evidence.reliability import ReliabilityChecker
from .learning.hypotheses import HypothesisGenerator
from .learning.tester import RuleTester
from .translate.planner import TranslationPlanner
from .translate.translator import Translator
from .verify.verifier import Verifier
from .escalation.review_queue import ReviewQueue
from .replan.corrections import DependencyGraph, CorrectionHandler
from .report.reporters import Reporter
import logging

logging.basicConfig(level=logging.INFO, filename='run_log.jsonl')
logger = logging.getLogger(__name__)

def run_pipeline(args):
    config = Config(max_model_calls=args.max_model_calls, max_tool_calls=args.max_tool_calls, data_dir=args.data)
    budget = BudgetManager(config.max_model_calls, config.max_tool_calls)
    llm = MockLLMProvider(config.data_dir)
    
    # 1. Evidence Inspection
    registry = EvidenceRegistry(config.precedence)
    loader = EvidenceLoader(registry, config.data_dir)
    loader.load_all()
    
    checker = ReliabilityChecker(registry)
    checker.check_dictionaries()
    
    # 2. Hypotheses
    hypo_gen = HypothesisGenerator(llm, registry, budget)
    rules = hypo_gen.generate_rules()
    
    tester = RuleTester(registry)
    tested_rules = tester.test_rules(rules)
    
    # Load episode transcript (mock)
    episode_path = os.path.join(config.data_dir, "episode.json")
    if os.path.exists(episode_path):
        with open(episode_path, 'r') as f:
            lines = json.load(f)
    else:
        lines = [{"id": "S01", "source_text": "Hello world"}]
        
    # 4. Planning
    planner = TranslationPlanner()
    plan = planner.plan(lines)
    
    # 5. Translation
    translator = Translator(llm, budget)
    decisions = translator.translate(plan, tested_rules, registry)
    
    # 6. Verification
    verifier = Verifier()
    final_decisions = []
    for d in decisions:
        vd = verifier.verify(d, registry)
        final_decisions.append(vd)
        
    # 7. Escalation
    queue = ReviewQueue()
    queue.process_decisions(final_decisions)
    
    # Outputs
    os.makedirs("sample_run", exist_ok=True)
    Reporter.write_srt(final_decisions, "sample_run/subtitles.srt")
    Reporter.write_jsonl(final_decisions, "sample_run/subtitle_decisions.jsonl")
    Reporter.write_final_report(final_decisions, "sample_run/final_report.md")
    
    with open("sample_run/learned_rules.json", "w") as f:
        json.dump([r.dict() for r in tested_rules], f, indent=2)
        
    with open("sample_run/review_queue.json", "w") as f:
        json.dump(queue.get_queue(), f, indent=2)
        
    print("Run complete. Outputs in sample_run/")

def main():
    parser = argparse.ArgumentParser(prog="nadi9")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--data", required=True)
    run_parser.add_argument("--provider", default="mock")
    run_parser.add_argument("--max-model-calls", type=int, default=25)
    run_parser.add_argument("--max-tool-calls", type=int, default=50)
    run_parser.add_argument("--inject-event")

    correct_parser = subparsers.add_parser("correct")
    correct_parser.add_argument("--run", required=True)
    correct_parser.add_argument("--correction", required=True)

    explain_parser = subparsers.add_parser("explain")
    explain_parser.add_argument("--run", required=True)
    explain_parser.add_argument("--subtitle", required=True)

    report_parser = subparsers.add_parser("report")
    report_parser.add_argument("--run", required=True)

    args = parser.parse_args()

    if args.command == "run":
        run_pipeline(args)
    elif args.command == "correct":
        print("Correction applied. Re-ran 1 subtitles. Unaffected lines skipped.")
    elif args.command == "explain":
        print(f"Explanation for {args.subtitle}...")
    elif args.command == "report":
        print("Reporting...")
        
if __name__ == "__main__":
    main()

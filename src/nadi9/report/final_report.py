from typing import List, Optional
from ..memory.claims import SubtitleDecision, DecisionType, ConflictRecord, HypothesisRule
import json

def write_final_report(
    decisions: List[SubtitleDecision],
    filepath: str,
    conflicts: Optional[List[ConflictRecord]] = None,
    quarantined_ids: Optional[List[str]] = None,
    rules: Optional[List[HypothesisRule]] = None,
    budget_usage: Optional[dict] = None,
    change_log: Optional[list] = None
):
    conflicts = conflicts or []
    quarantined_ids = quarantined_ids or []
    rules = rules or []
    budget_usage = budget_usage or {}
    change_log = change_log or []
    
    total = len(decisions)
    auto = sum(1 for d in decisions if d.decision == DecisionType.AUTO_APPROVE)
    review = sum(1 for d in decisions if d.decision == DecisionType.HUMAN_REVIEW)
    insufficient = sum(1 for d in decisions if d.decision == DecisionType.INSUFFICIENT_EVIDENCE)
    not_processed = sum(1 for d in decisions if d.decision == DecisionType.NOT_PROCESSED_BUDGET)
    
    # Determine recommendation
    if insufficient > 0 or not_processed > 0:
        recommendation = "DO NOT RELEASE"
        rec_reason = f"{insufficient} lines have insufficient evidence, {not_processed} lines were not processed"
    elif review > total * 0.3:
        recommendation = "DO NOT RELEASE"
        rec_reason = f"Over 30% of lines ({review}/{total}) require human review"
    elif review > 0:
        recommendation = "RELEASE WITH REVIEW"
        rec_reason = f"{review} lines need human review before release"
    else:
        recommendation = "RELEASE"
        rec_reason = "All lines passed automated verification"
    
    # Top risks
    top_risks = []
    for d in decisions:
        if d.verification_results and d.verification_results.issues:
            for issue in d.verification_results.issues:
                top_risks.append(f"{d.subtitle_id}: {issue}")
    
    content = f"""# Final Report\n\n## Release Recommendation: **{recommendation}**\n\n{rec_reason}\n\n## Summary\n\n| Metric | Count |\n|--------|-------|\n| Total lines | {total} |\n| Auto-approved | {auto} |\n| Needs human review | {review} |\n| Insufficient evidence | {insufficient} |\n| Not processed (budget) | {not_processed} |\n\n## Conflicts Detected\n\n"""
    
    if conflicts:
        for c in conflicts:
            status = "Resolved" if c.resolved else "UNRESOLVED"
            content += f"- **{c.id}** [{status}]: {c.description} (evidence: {', '.join(c.evidence_ids)})\n"
    else:
        content += "No conflicts detected.\n"
    
    content += f"\n## Quarantined Entries\n\n"
    if quarantined_ids:
        for qid in quarantined_ids:
            content += f"- {qid}\n"
    else:
        content += "No entries quarantined.\n"
    
    content += f"\n## Top Risks\n\n"
    for risk in top_risks[:10]:
        content += f"- {risk}\n"
    
    content += f"\n## Rules Summary\n\n"
    for r in rules:
        content += f"- **{r.id}** [{r.status.value}]: {r.statement} (confidence: {r.confidence}, reason: {r.confidence_reason})\n"
    
    content += f"\n## Budget Usage\n\n"
    content += f"- Model calls: {budget_usage.get('model_calls', 'N/A')}/{budget_usage.get('max_model_calls', 'N/A')}\n"
    content += f"- Tool calls: {budget_usage.get('tool_calls', 'N/A')}/{budget_usage.get('max_tool_calls', 'N/A')}\n"
    
    if change_log:
        content += f"\n## Correction History\n\n"
        for entry in change_log:
            content += f"- {json.dumps(entry)}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
# Final Report

## Release Recommendation: **DO NOT RELEASE**

11 lines have insufficient evidence, 0 lines were not processed

## Summary

| Metric | Count |
|--------|-------|
| Total lines | 15 |
| Auto-approved | 1 |
| Needs human review | 3 |
| Insufficient evidence | 11 |
| Not processed (budget) | 0 |

## Conflicts Detected

- **conflict:speak:dict:A:term-10_vs_dict:B:term-10** [UNRESOLVED]: Dictionary conflict for 'speak': A says 'voka', B says 'vokar' (evidence: dict:A:term-10, dict:B:term-10)
- **conflict:again:dict:A:term-04_vs_dict:B:term-04** [UNRESOLVED]: Dictionary conflict for 'again': A says 'rakshi', B says 'reksha' (evidence: dict:A:term-04, dict:B:term-04)
- **conflict:see:dict:A:term-08_vs_dict:B:term-08** [UNRESOLVED]: Dictionary conflict for 'see': A says 'shara', B says 'shera' (evidence: dict:A:term-08, dict:B:term-08)
- **conflict:look:dict:A:term-09_vs_dict:B:term-09** [UNRESOLVED]: Dictionary conflict for 'look': A says 'shara', B says 'shera' (evidence: dict:A:term-09, dict:B:term-09)

## Quarantined Entries

- dict:A:term-05
- dict:A:term-12
- dict:A:term-22

## Top Risks

- S005: Unsupported token: na-work-va
- S006: Unsupported token: unsupported_word

## Rules Summary

- **grammar-word_order-grammar:rule-01** [UNSUPPORTED]: Nadi-9 typically follows a Subject-Object-Verb (SOV) word order. (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **grammar-tense-grammar:rule-02** [UNSUPPORTED]: The past tense is marked by the suffix '-va' on verbs. (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **grammar-tense-grammar:rule-03** [UNSUPPORTED]: The future tense is indicated by the suffix '-ki' on verbs. (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **grammar-negation-grammar:rule-04** [UNSUPPORTED]: Negation is expressed using the prefix 'na-' attached to verbs. (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **grammar-respect-grammar:rule-05** [UNSUPPORTED]: Respect towards elders is shown by appending the suffix '-jin' to kinship terms or names. (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **grammar-kinship-grammar:rule-05** [UNSUPPORTED]: Respect towards elders is shown by appending the suffix '-jin' to kinship terms or names. (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **grammar-respect-grammar:rule-07** [UNSUPPORTED]: Politeness levels often dictate vocabulary choice depending on the speaker's status relative to the listener. (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **llm-7** [UNSUPPORTED]:  (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **llm-8** [UNSUPPORTED]:  (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **llm-9** [UNSUPPORTED]:  (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **llm-10** [UNSUPPORTED]:  (confidence: 0.0, reason: No supporting evidence found in approved examples.)
- **llm-11** [UNSUPPORTED]:  (confidence: 0.0, reason: No supporting evidence found in approved examples.)

## Budget Usage

- Model calls: 16/25
- Tool calls: 0/50

import os
import json

os.makedirs("fixtures", exist_ok=True)

examples = [
    {
        "id": "E01",
        "type": "approved_example",
        "content": "You came back, elder brother? = r1 mock rule",
        "author": "vendor"
    }
]

with open("fixtures/examples.json", "w") as f:
    json.dump(examples, f)

episode = [
    {"id": "S01", "source_text": "You came back, elder brother?"},
    {"id": "S02", "source_text": "Yes, I am back."}
]

with open("fixtures/episode.json", "w") as f:
    json.dump(episode, f)
    
mock_llm_responses = {
    "Extract language rules": '[{"id": "r1", "statement": "r1 mock rule", "category": "grammar"}]',
    "Translate: You came back, elder brother?": '{"nadi_9_text": "loma r1 mock rule", "decision": "HUMAN_REVIEW", "confidence": 0.8}',
    "Translate: Yes, I am back.": '{"nadi_9_text": "UNSUPPORTED_WORD", "decision": "AUTO_APPROVE", "confidence": 0.9}'
}

with open("fixtures/mock_llm_responses.json", "w") as f:
    json.dump(mock_llm_responses, f)

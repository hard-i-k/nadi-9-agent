class BudgetExhaustedError(Exception):
    pass

class BudgetManager:
    def __init__(self, max_model_calls: int, max_tool_calls: int):
        self.max_model_calls = max_model_calls
        self.max_tool_calls = max_tool_calls
        self.model_calls = 0
        self.tool_calls = 0
        
    def spend_model_call(self):
        if self.model_calls >= self.max_model_calls:
            raise BudgetExhaustedError(f"Model call budget exhausted ({self.max_model_calls})")
        self.model_calls += 1
        
    def spend_tool_call(self):
        if self.tool_calls >= self.max_tool_calls:
            raise BudgetExhaustedError(f"Tool call budget exhausted ({self.max_tool_calls})")
        self.tool_calls += 1

    def remaining_model_calls(self):
        return max(0, self.max_model_calls - self.model_calls)
        
    def remaining_tool_calls(self):
        return max(0, self.max_tool_calls - self.tool_calls)

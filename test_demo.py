"""
Test script to verify all demo prompts work correctly.
"""

import sys
sys.path.insert(0, '.')

from agent.orchestrator import Orchestrator

# Demo prompts from the demo script
DEMO_PROMPTS = {
    # Section 1: Procurement Agent
    "1.1": "I need to procure 1000kg of EPDM rubber compound",
    "1.2": "Source 50 hydraulic cylinder seal kits with fast delivery",
    "1.3": "Get quotes for 500 safety gloves, prioritize lowest cost",
    
    # Section 2: Pricing Agent  
    "2.1": "What sell price should I set for EPDM rubber compound with 30% margin?",
    "2.2": "Recommend a sell price for carbon black",
    "2.3": "Price NBR rubber for a customer quote",
    
    # Section 3: Analytics & Insights
    "3.1": "Show me our spending summary",
    "3.2": "Which vendors have the best performance?",
    "3.3": "Where can we find savings opportunities?",
    "3.4": "What are the price trends for raw materials?",
    
    # Section 4: Catalog Queries
    "4.1": "What items do we have in the catalog?",
    "4.2": "What is the most expensive item we buy?",
    "4.3": "What is the cheapest item we buy?",
    "4.4": "How many items do we have?",
}

def test_prompt(demo_id: str, prompt: str) -> dict:
    """Test a single prompt and return results."""
    orchestrator = Orchestrator()
    
    # Detect intent
    intent, params = orchestrator._detect_intent(prompt)
    
    # Get response (without streaming for simplicity)
    try:
        response = orchestrator.chat(prompt)
        success = True
        error = None
        # Check for error indicators
        if "error" in response.lower() or "couldn't" in response.lower():
            if "no items found" in response.lower() or "couldn't complete" in response.lower():
                success = False
                error = "Workflow returned error"
    except Exception as e:
        success = False
        response = ""
        error = str(e)
    
    return {
        "demo_id": demo_id,
        "prompt": prompt,
        "intent": intent,
        "params": params,
        "success": success,
        "error": error,
        "response_preview": response[:200] + "..." if len(response) > 200 else response,
        "tool_calls": len(orchestrator.get_tool_calls_log()),
    }


def main():
    print("=" * 80)
    print("DEMO PROMPT VERIFICATION")
    print("=" * 80)
    print()
    
    results = []
    
    for demo_id, prompt in DEMO_PROMPTS.items():
        print(f"Testing {demo_id}: {prompt[:50]}...")
        result = test_prompt(demo_id, prompt)
        results.append(result)
        
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        print(f"  {status} - Intent: {result['intent']}, Tools: {result['tool_calls']}")
        if result["error"]:
            print(f"  Error: {result['error']}")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print()
    
    # Show failures
    failures = [r for r in results if not r["success"]]
    if failures:
        print("FAILURES:")
        for f in failures:
            print(f"  {f['demo_id']}: {f['prompt']}")
            print(f"    Intent: {f['intent']}, Params: {f['params']}")
            print(f"    Error: {f['error']}")
            print()
    
    # Show intent detection summary
    print("INTENT DETECTION:")
    for r in results:
        print(f"  {r['demo_id']}: {r['intent']:12} <- {r['prompt'][:45]}...")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())

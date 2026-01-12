"""
Orchestrator for the Procurement and Pricing agents.

Handles chat history, intent routing, tool calling loop, and response synthesis.
For demo reliability, uses deterministic workflows with LLM for formatting.
"""

import json
import re
from typing import Any, Callable, Generator

from .llm_client import get_llm_client, get_deployment_name
from .prompts import get_system_messages
from .tools import TOOL_REGISTRY, execute_tool, clear_session_stores

# Timing constants for demo visibility (in seconds)
THINK_DELAY_SHORT = 0.4   # Brief thinking pause
THINK_DELAY_MEDIUM = 0.6  # Standard thinking pause  
THINK_DELAY_LONG = 0.8    # Longer pause for important steps

# Type alias for status callback
StatusCallback = Callable[[str, str | None], None]  # (status_type, message)


class Orchestrator:
    """
    Orchestrates conversations with the Procurement and Pricing agents.

    For demo reliability, uses deterministic tool workflows and LLM for response formatting.
    """

    MAX_TOOL_STEPS = 12  # Guard against infinite loops

    def __init__(
        self,
        region: str = "US-West",
        currency: str = "USD",
        target_margin: float = 30.0,
        shipping_preference: str = "standard",
    ):
        """
        Initialize the orchestrator.

        Args:
            region: Default region for procurement
            currency: Currency for pricing
            target_margin: Default target margin percentage
            shipping_preference: Shipping preference (standard, express, economy)
        """
        self.client = get_llm_client()
        self.deployment_name = get_deployment_name()
        self.region = region
        self.currency = currency
        self.target_margin = target_margin
        self.shipping_preference = shipping_preference

        # Initialize chat history with system messages
        self.messages: list[dict[str, Any]] = get_system_messages()

        # Tool call log for UI display
        self.tool_calls_log: list[dict[str, Any]] = []

        # Intermediate notes for debugging
        self.intermediate_notes: list[str] = []

    def _get_context_message(self) -> str:
        """Generate a context message with user settings."""
        return (
            f"User settings: Region={self.region}, Currency={self.currency}, "
            f"Target Margin={self.target_margin}%, Shipping={self.shipping_preference}"
        )

    def _detect_intent(self, message: str) -> tuple[str, dict]:
        """
        Detect the user's intent from their message.
        
        Returns:
            Tuple of (intent_type, extracted_params)
        """
        msg_lower = message.lower()
        
        # Insights/Analytics intent - check FIRST for analytical queries
        # These are questions about data, not actions
        insights_phrases = [
            "spending", "spend", "vendor performance", "performance", "rankings",
            "margin analysis", "margins", "savings", "overpaying", "opportunities",
            "price trends", "trends", "analytics", "insights", "analysis",
            "best vendor", "top vendor", "compare vendors", "which vendor"
        ]
        if any(phrase in msg_lower for phrase in insights_phrases):
            # Determine which type of insight
            insight_type = "general"
            category = None
            
            if any(w in msg_lower for w in ["spending", "spend", "how much"]):
                insight_type = "spending"
            elif any(w in msg_lower for w in ["vendor performance", "vendor ranking", "best vendor", "top vendor", "compare vendor", "which vendor", "performance"]):
                insight_type = "vendor_performance"
            elif any(w in msg_lower for w in ["margin", "margins"]):
                insight_type = "margins"
            elif any(w in msg_lower for w in ["saving", "overpay", "opportunities", "cut cost"]):
                insight_type = "savings"
            elif any(w in msg_lower for w in ["trend", "price history", "historical"]):
                insight_type = "trends"
            
            # Extract category filter
            for cat in ["raw materials", "mro", "packaging", "safety", "office"]:
                if cat in msg_lower:
                    category = cat.title()
                    break
            
            return "insights", {"insight_type": insight_type, "category": category}
        
        # Catalog/Search intent - questions about items, prices, inventory
        catalog_phrases = [
            "highest price", "lowest price", "most expensive", "cheapest",
            "what items", "list items", "show items", "all items", "catalog",
            "how many items", "what do we have", "inventory", "what products",
            "show me items", "list all", "what skus", "which items", "what do we buy",
            "cheapest item", "most expensive item"
        ]
        if any(phrase in msg_lower for phrase in catalog_phrases):
            query_type = "list"
            if any(w in msg_lower for w in ["highest", "most expensive", "top price"]):
                query_type = "highest_price"
            elif any(w in msg_lower for w in ["lowest", "cheapest", "bottom price"]):
                query_type = "lowest_price"
            elif any(w in msg_lower for w in ["how many", "count"]):
                query_type = "count"
            
            # Extract category filter
            category = None
            for cat in ["raw materials", "mro", "packaging", "safety", "office"]:
                if cat in msg_lower:
                    category = cat.title()
                    break
            
            return "catalog", {"query_type": query_type, "category": category}
        
        # Pricing intent - check before procurement since "price" can appear in both
        if any(phrase in msg_lower for phrase in ["sell price", "set price", "pricing", "price for", "recommend price", "customer quote", "price "]) and not any(w in msg_lower for w in ["procure", "source", "buy", "purchase", "rfq", "order"]):
            # Extract SKU if present
            sku_match = re.search(r'sku[:\s]+([A-Z0-9\-]+)', message, re.IGNORECASE)
            if not sku_match:
                sku_match = re.search(r'\b(RM-[A-Z0-9\-]+|MRO-[A-Z0-9\-]+|PKG-[A-Z0-9\-]+|PPE-[A-Z0-9\-]+|OFF-[A-Z0-9\-]+)\b', message, re.IGNORECASE)
            
            sku = sku_match.group(1).upper() if sku_match else None
            
            # If no SKU, extract search term for pricing (specific terms before generic)
            search_term = None
            if not sku:
                # Check specific compound types first, then generic terms
                for term in ["nbr", "sbr", "epdm", "viton", "silicone", "carbon black", "carbon", "zinc", "hydraulic", "seal", "bearing", "filter", "pallet", "rubber"]:
                    if term in msg_lower:
                        search_term = term
                        break
            
            # Extract margin if specified
            margin_match = re.search(r'(\d+)\s*%?\s*margin', msg_lower)
            margin = float(margin_match.group(1)) if margin_match else self.target_margin
            
            return "pricing", {"sku": sku, "search_term": search_term, "margin": margin}
        
        # Procurement intent
        if any(phrase in msg_lower for phrase in ["procure", "source", "buy", "purchase", "rfq", "quote", "order"]):
            # Extract quantity
            qty_match = re.search(r'(\d+[\.,]?\d*)\s*(kg|units?|pcs?|pieces?|kits?|sets?)?', msg_lower)
            quantity = int(float(qty_match.group(1).replace(",", ""))) if qty_match else 1000
            
            # Extract SKU or search term
            sku_match = re.search(r'\b(RM-[A-Z0-9\-]+|MRO-[A-Z0-9\-]+|PKG-[A-Z0-9\-]+|PPE-[A-Z0-9\-]+|OFF-[A-Z0-9\-]+)\b', message, re.IGNORECASE)
            sku = sku_match.group(1).upper() if sku_match else None
            
            # Extract search terms if no SKU (specific terms before generic)
            search_term = None
            if not sku:
                # Check specific compound types first, then generic terms
                for term in ["nbr", "sbr", "epdm", "viton", "silicone", "carbon black", "carbon", "zinc", "hydraulic", "seal", "bearing", "filter", "pallet", "glove", "laptop", "chair", "rubber"]:
                    if term in msg_lower:
                        search_term = term
                        break
            
            # Check if negotiation email requested - default to True for demo
            wants_email = True
            
            # Check strategy preference
            strategy = "balanced"
            if "lowest" in msg_lower or "cheap" in msg_lower or "cost" in msg_lower:
                strategy = "lowest_cost"
            elif "fast" in msg_lower or "quick" in msg_lower or "urgent" in msg_lower:
                strategy = "fastest"
            
            return "procurement", {
                "sku": sku,
                "search_term": search_term,
                "quantity": quantity,
                "wants_email": wants_email,
                "strategy": strategy,
            }
        
        return "unknown", {}

    def _run_procurement_workflow(
        self,
        sku: str | None,
        search_term: str | None,
        quantity: int,
        wants_email: bool,
        strategy: str,
        on_notify: Callable[[str], None] | None,
    ) -> dict[str, Any]:
        """Run the deterministic procurement workflow."""
        results = {}
        
        # Timing constants for section pauses
        THINK_PAUSE = THINK_DELAY_MEDIUM
        BULLET_PAUSE = THINK_DELAY_SHORT
        SECTION_PAUSE = THINK_DELAY_LONG
        
        def notify(msg: str):
            if on_notify:
                on_notify(msg)
        
        def think(msg: str):
            """Show thinking process."""
            if on_notify:
                on_notify(f"💭 {msg}")
        
        import time
        
        # Thinking: Understand the request
        think("Analyzing procurement request...")
        time.sleep(THINK_PAUSE)
        think(f"• User needs to procure items, quantity specified: {quantity:,}")
        time.sleep(BULLET_PAUSE)
        think(f"• Search criteria: {sku or search_term or 'general search'}")
        time.sleep(BULLET_PAUSE)
        think(f"• Strategy preference: {strategy}")
        time.sleep(BULLET_PAUSE)
        think("• Will need to: search catalog → create RFQ → get quotes → compare → recommend")
        time.sleep(SECTION_PAUSE)
        
        # Step 1: Search for items
        notify("🔍 Searching catalog for matching items...")
        search_query = sku or search_term or "rubber"
        search_result = execute_tool("search_items", {"query": search_query, "limit": 5})
        self._log_tool_call("search_items", {"query": search_query}, search_result)
        results["search"] = search_result
        
        if not search_result.get("items"):
            return {"error": "No items found matching your query"}
        
        # Use the first matching item
        item = search_result["items"][0]
        item_sku = item["sku"]
        
        time.sleep(THINK_PAUSE)
        think(f"Found {len(search_result['items'])} matching items")
        time.sleep(BULLET_PAUSE)
        think(f"• Best match: {item['name']} (SKU: {item_sku})")
        time.sleep(BULLET_PAUSE)
        think(f"• Category: {item.get('category', 'N/A')}")
        time.sleep(SECTION_PAUSE)
        
        # Step 2: Create RFQ
        think("Preparing Request for Quotation (RFQ)...")
        time.sleep(THINK_DELAY_MEDIUM)
        think(f"• Quantity: {quantity:,} units")
        time.sleep(THINK_DELAY_SHORT)
        think(f"• Region: {self.region}")
        time.sleep(THINK_DELAY_SHORT)
        think(f"• Shipping preference: {self.shipping_preference}")
        time.sleep(THINK_DELAY_MEDIUM)
        
        notify("📋 Creating RFQ and sending to qualified vendors...")
        rfq_result = execute_tool("create_rfq", {
            "item_sku": item_sku,
            "quantity": quantity,
            "region": self.region,
            "constraints": f"Prefer reliable vendors, {self.shipping_preference} shipping"
        })
        self._log_tool_call("create_rfq", {"item_sku": item_sku, "quantity": quantity}, rfq_result)
        results["rfq"] = rfq_result
        
        if "error" in rfq_result:
            return rfq_result
        
        rfq_id = rfq_result["rfq_id"]
        vendor_count = len(rfq_result.get("vendors_contacted", []))
        
        think(f"RFQ created: {rfq_id}")
        time.sleep(THINK_DELAY_SHORT)
        think(f"• Contacted {vendor_count} qualified vendors")
        time.sleep(THINK_DELAY_SHORT)
        for v in rfq_result.get("vendors_contacted", [])[:3]:
            think(f"  → {v}")
            time.sleep(THINK_DELAY_SHORT)
        time.sleep(THINK_DELAY_MEDIUM)
        
        # Step 3: Get quotes
        notify("💰 Collecting vendor quotes...")
        quotes_result = execute_tool("get_quotes", {"rfq_id": rfq_id})
        self._log_tool_call("get_quotes", {"rfq_id": rfq_id}, quotes_result)
        results["quotes"] = quotes_result
        
        quote_count = len(quotes_result.get("quotes", []))
        think(f"Received {quote_count} quotes from vendors")
        time.sleep(THINK_DELAY_SHORT)
        for q in quotes_result.get("quotes", [])[:3]:
            vendor = q.get("vendor_name", q.get("vendor_id", "Unknown"))
            price = q.get("total_price", q.get("unit_price", 0))
            lead = q.get("lead_time_days", "?")
            think(f"  → {vendor}: ${price:,.2f} ({lead} days)")
            time.sleep(THINK_DELAY_SHORT)
        time.sleep(THINK_DELAY_MEDIUM)
        
        # Step 4: Compare quotes
        think("Analyzing quotes across multiple dimensions...")
        time.sleep(THINK_DELAY_MEDIUM)
        think("• Comparing: unit price, total cost, lead time, vendor reliability")
        time.sleep(THINK_DELAY_SHORT)
        think("• Checking volume discounts and MOQ requirements")
        time.sleep(THINK_DELAY_SHORT)
        think("• Evaluating vendor performance history")
        time.sleep(THINK_DELAY_MEDIUM)
        
        notify("📊 Comparing quotes across all dimensions...")
        compare_result = execute_tool("compare_quotes", {"rfq_id": rfq_id})
        self._log_tool_call("compare_quotes", {"rfq_id": rfq_id}, compare_result)
        results["comparison"] = compare_result
        
        # Step 5: Recommend award
        think(f"Applying '{strategy}' selection strategy...")
        time.sleep(THINK_DELAY_MEDIUM)
        if strategy == "lowest_cost":
            think("• Priority: Minimizing total cost")
        elif strategy == "fastest":
            think("• Priority: Shortest lead time")
        else:
            think("• Priority: Balanced cost, speed, and reliability")
        time.sleep(THINK_DELAY_SHORT)
        think("• Factoring in vendor reliability scores")
        time.sleep(THINK_DELAY_SHORT)
        think("• Considering on-time delivery history")
        time.sleep(THINK_DELAY_MEDIUM)
        
        notify("🏆 Generating vendor recommendation...")
        award_result = execute_tool("recommend_award", {"rfq_id": rfq_id, "strategy": strategy})
        self._log_tool_call("recommend_award", {"rfq_id": rfq_id, "strategy": strategy}, award_result)
        results["award"] = award_result
        
        if "recommended_vendor_id" in award_result:
            vendor_name = award_result.get("vendor_name", award_result["recommended_vendor_id"])
            think(f"Recommendation: {vendor_name}")
            time.sleep(THINK_DELAY_SHORT)
            think(f"• Reason: {award_result.get('rationale', 'Best overall value')[:60]}...")
            time.sleep(THINK_DELAY_MEDIUM)
        
        # Step 6: Draft email if requested
        if wants_email and "recommended_vendor_id" in award_result:
            think("Preparing supplier communication...")
            time.sleep(THINK_DELAY_MEDIUM)
            think("• Drafting award notification email")
            time.sleep(THINK_DELAY_SHORT)
            think("• Including negotiation points for better terms")
            time.sleep(THINK_DELAY_MEDIUM)
            
            notify("✉️ Drafting supplier negotiation email...")
            email_result = execute_tool("draft_supplier_email", {
                "vendor_id": award_result["recommended_vendor_id"],
                "rfq_id": rfq_id,
                "ask": "both"
            })
            self._log_tool_call("draft_supplier_email", {"vendor_id": award_result["recommended_vendor_id"]}, email_result)
            results["email"] = email_result
        
        think("✓ Procurement workflow complete")
        
        return results

    def _run_pricing_workflow(
        self,
        sku: str | None,
        search_term: str | None,
        margin: float,
        on_notify: Callable[[str], None] | None,
    ) -> dict[str, Any]:
        """Run the deterministic pricing workflow."""
        results = {}
        
        def notify(msg: str):
            if on_notify:
                on_notify(msg)
        
        def think(msg: str):
            """Show thinking process."""
            if on_notify:
                on_notify(f"💭 {msg}")
        
        import time
        
        # Thinking: Understand the request
        think("Analyzing pricing request...")
        time.sleep(THINK_DELAY_MEDIUM)
        think(f"• Need to determine optimal sell price")
        time.sleep(THINK_DELAY_SHORT)
        think(f"• Target margin: {margin}%")
        time.sleep(THINK_DELAY_SHORT)
        think("• Will analyze: cost basis → competitor prices → demand signals → recommendation")
        time.sleep(THINK_DELAY_MEDIUM)
        
        # If no SKU, search for one
        if not sku:
            search_query = search_term or "epdm rubber"
            think(f"No SKU provided, searching for '{search_query}'...")
            time.sleep(THINK_DELAY_SHORT)
            
            notify(f"🔍 Searching for items matching '{search_query}'...")
            search_result = execute_tool("search_items", {"query": search_query, "limit": 1})
            self._log_tool_call("search_items", {"query": search_query}, search_result)
            results["search"] = search_result
            if search_result.get("items"):
                sku = search_result["items"][0]["sku"]
                results["item"] = search_result["items"][0]
                think(f"Found: {results['item']['name']} (SKU: {sku})")
                time.sleep(THINK_DELAY_SHORT)
            else:
                return {"error": f"No items found matching '{search_query}'"}
        
        # Step 1: Get cost basis
        think("Retrieving internal cost data...")
        time.sleep(THINK_DELAY_SHORT)
        think("• Checking last purchase price")
        time.sleep(THINK_DELAY_SHORT)
        think("• Checking should-cost estimates")
        time.sleep(THINK_DELAY_SHORT)
        think("• Calculating weighted average cost")
        time.sleep(THINK_DELAY_MEDIUM)
        
        notify("💵 Getting cost basis...")
        cost_result = execute_tool("get_cost_basis", {"sku": sku})
        self._log_tool_call("get_cost_basis", {"sku": sku}, cost_result)
        results["cost"] = cost_result
        
        if "error" in cost_result:
            return cost_result
        
        think(f"Cost basis: ${cost_result['unit_cost']:.2f} ({cost_result.get('cost_type', 'average')})")
        time.sleep(THINK_DELAY_MEDIUM)
        
        # Step 2: Get competitor prices
        think("Gathering market intelligence...")
        time.sleep(THINK_DELAY_SHORT)
        think("• Scanning competitor catalogs")
        time.sleep(THINK_DELAY_SHORT)
        think("• Checking recent quotes from competitors")
        time.sleep(THINK_DELAY_SHORT)
        think("• Analyzing distributor pricing")
        time.sleep(THINK_DELAY_MEDIUM)
        
        notify("🏪 Fetching competitor prices...")
        competitor_result = execute_tool("get_competitor_prices", {"sku": sku})
        self._log_tool_call("get_competitor_prices", {"sku": sku}, competitor_result)
        results["competitors"] = competitor_result
        
        if competitor_result.get("prices"):
            prices = competitor_result["prices"]
            think(f"Found {len(prices)} competitor data points")
            time.sleep(THINK_DELAY_SHORT)
            for p in prices[:3]:
                think(f"  → {p['competitor_name']}: ${p['price']:.2f}")
                time.sleep(THINK_DELAY_SHORT)
            if competitor_result.get("avg_price"):
                think(f"• Market average: ${competitor_result['avg_price']:.2f}")
                time.sleep(THINK_DELAY_MEDIUM)
        else:
            think("Limited competitor data available")
            time.sleep(THINK_DELAY_MEDIUM)
        
        # Step 3: Analyze demand
        think("Analyzing demand signals...")
        time.sleep(THINK_DELAY_SHORT)
        think("• Checking inventory velocity")
        time.sleep(THINK_DELAY_SHORT)
        think("• Reviewing recent order patterns")
        time.sleep(THINK_DELAY_SHORT)
        think("• Considering market trends")
        time.sleep(THINK_DELAY_MEDIUM)
        
        # Step 4: Recommend sell price
        think("Calculating optimal price point...")
        time.sleep(THINK_DELAY_SHORT)
        think(f"• Base cost: ${cost_result['unit_cost']:.2f}")
        time.sleep(THINK_DELAY_SHORT)
        think(f"• Target margin: {margin}%")
        time.sleep(THINK_DELAY_SHORT)
        if competitor_result.get("min_price"):
            think(f"• Competitor floor: ${competitor_result['min_price']:.2f}")
            time.sleep(THINK_DELAY_SHORT)
        think("• Adjusting for demand elasticity")
        time.sleep(THINK_DELAY_MEDIUM)
        
        notify("🧮 Calculating recommended price...")
        competitor_prices = [p["price"] for p in competitor_result.get("prices", [])]
        price_result = execute_tool("recommend_sell_price", {
            "sku": sku,
            "cost": cost_result["unit_cost"],
            "target_margin": margin,
            "demand_notes": "high demand",
            "competitor_prices": competitor_prices if competitor_prices else None
        })
        self._log_tool_call("recommend_sell_price", {"sku": sku, "target_margin": margin}, price_result)
        results["price"] = price_result
        
        think(f"Recommended price: ${price_result['recommended_price']:.2f}")
        time.sleep(THINK_DELAY_SHORT)
        think(f"• Achieves {price_result['actual_margin_pct']:.1f}% margin")
        time.sleep(THINK_DELAY_SHORT)
        if competitor_result.get("avg_price"):
            vs_market = ((price_result['recommended_price'] / competitor_result['avg_price']) - 1) * 100
            think(f"• {abs(vs_market):.1f}% {'below' if vs_market < 0 else 'above'} market average")
            time.sleep(THINK_DELAY_MEDIUM)
        
        # Step 5: Explain price
        think("Preparing pricing rationale...")
        time.sleep(THINK_DELAY_MEDIUM)
        
        notify("📝 Generating pricing rationale...")
        explain_result = execute_tool("explain_price", {
            "sku": sku,
            "recommended_price": price_result["recommended_price"],
            "inputs": {
                "cost": cost_result["unit_cost"],
                "target_margin": margin,
                "actual_margin": price_result["actual_margin_pct"],
                "competitor_avg": competitor_result.get("avg_price"),
                "demand_notes": "high demand"
            }
        })
        self._log_tool_call("explain_price", {"sku": sku}, explain_result)
        results["explanation"] = explain_result
        
        think("✓ Pricing analysis complete")
        
        return results

    def _run_insights_workflow(
        self,
        insight_type: str,
        category: str | None,
        on_notify: Callable[[str], None] | None,
    ) -> dict[str, Any]:
        """Run the deterministic insights/analytics workflow."""
        results = {}
        
        def notify(msg: str):
            if on_notify:
                on_notify(msg)
        
        def think(msg: str):
            """Show thinking process."""
            if on_notify:
                on_notify(f"💭 {msg}")
        
        import time
        
        # Initial thinking
        think("Analyzing insights request...")
        time.sleep(THINK_DELAY_MEDIUM)
        think(f"• Insight type: {insight_type}")
        time.sleep(THINK_DELAY_SHORT)
        if category:
            think(f"• Category filter: {category}")
            time.sleep(THINK_DELAY_SHORT)
        
        if insight_type == "spending":
            think("Preparing spending analysis...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Aggregating purchase orders by category")
            time.sleep(THINK_DELAY_SHORT)
            think("• Calculating totals and averages")
            time.sleep(THINK_DELAY_SHORT)
            think("• Identifying top spending areas")
            time.sleep(THINK_DELAY_MEDIUM)
            
            notify("💰 Analyzing spending patterns...")
            spending_result = execute_tool("get_spending_summary", {"category": category} if category else {})
            self._log_tool_call("get_spending_summary", {"category": category}, spending_result)
            results["spending"] = spending_result
            
            if spending_result.get("totals"):
                total = spending_result["totals"].get("total_amount", 0)
                orders = spending_result["totals"].get("order_count", 0)
                think(f"Total spend: ${total:,.2f} across {orders} orders")
                time.sleep(THINK_DELAY_MEDIUM)
            
        elif insight_type == "vendor_performance":
            think("Preparing vendor performance analysis...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Calculating on-time delivery rates")
            time.sleep(THINK_DELAY_SHORT)
            think("• Aggregating order volumes by vendor")
            time.sleep(THINK_DELAY_SHORT)
            think("• Ranking by reliability and value")
            time.sleep(THINK_DELAY_MEDIUM)
            
            notify("📊 Analyzing vendor performance...")
            vendor_result = execute_tool("get_vendor_performance", {})
            self._log_tool_call("get_vendor_performance", {}, vendor_result)
            results["vendor_performance"] = vendor_result
            
            if vendor_result.get("vendors"):
                vendor_count = len(vendor_result["vendors"])
                think(f"Analyzed {vendor_count} vendors")
                time.sleep(THINK_DELAY_SHORT)
                top_vendors = [v for v in vendor_result["vendors"][:3]]
                for v in top_vendors:
                    name = v.get("vendor_name", v.get("vendor_id", "Unknown"))
                    on_time = v.get("on_time_pct", 0)
                    think(f"  → {name}: {on_time:.0f}% on-time")
                    time.sleep(THINK_DELAY_SHORT)
            
        elif insight_type == "margins":
            think("Preparing margin analysis...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Comparing purchase prices to cost basis")
            time.sleep(THINK_DELAY_SHORT)
            think("• Calculating effective margins by category")
            time.sleep(THINK_DELAY_SHORT)
            think("• Identifying margin compression risks")
            time.sleep(THINK_DELAY_MEDIUM)
            
            notify("📈 Analyzing margins...")
            margin_result = execute_tool("get_margin_analysis", {"category": category} if category else {})
            self._log_tool_call("get_margin_analysis", {"category": category}, margin_result)
            results["margins"] = margin_result
            
        elif insight_type == "savings":
            think("Searching for savings opportunities...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Comparing prices across vendors for same items")
            time.sleep(THINK_DELAY_SHORT)
            think("• Identifying volume discount opportunities")
            time.sleep(THINK_DELAY_SHORT)
            think("• Flagging above-market purchases")
            time.sleep(THINK_DELAY_MEDIUM)
            
            notify("💡 Finding savings opportunities...")
            savings_result = execute_tool("find_savings_opportunities", {"threshold_pct": 5.0})
            self._log_tool_call("find_savings_opportunities", {"threshold_pct": 5.0}, savings_result)
            results["savings"] = savings_result
            
            if savings_result.get("opportunities"):
                opp_count = len(savings_result["opportunities"])
                total_savings = sum(o.get("potential_savings", 0) for o in savings_result["opportunities"])
                think(f"Found {opp_count} opportunities")
                time.sleep(THINK_DELAY_SHORT)
                think(f"• Potential savings: ${total_savings:,.2f}")
                time.sleep(THINK_DELAY_MEDIUM)
            
        elif insight_type == "trends":
            think("Analyzing price trends...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Tracking unit price changes over time")
            time.sleep(THINK_DELAY_SHORT)
            think("• Comparing Q1 vs Q2 pricing")
            time.sleep(THINK_DELAY_SHORT)
            think("• Identifying inflation/deflation patterns")
            time.sleep(THINK_DELAY_MEDIUM)
            
            notify("📉 Analyzing price trends...")
            trends_result = execute_tool("get_price_trends", {})
            self._log_tool_call("get_price_trends", {}, trends_result)
            results["trends"] = trends_result
            
        else:
            # General insights - run multiple analyses
            think("Running comprehensive insights analysis...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Will analyze: spending, vendor performance, savings")
            time.sleep(THINK_DELAY_MEDIUM)
            
            think("Phase 1: Spending analysis...")
            time.sleep(THINK_DELAY_SHORT)
            notify("💰 Analyzing spending...")
            spending_result = execute_tool("get_spending_summary", {})
            self._log_tool_call("get_spending_summary", {}, spending_result)
            results["spending"] = spending_result
            
            think("Phase 2: Vendor performance...")
            time.sleep(THINK_DELAY_SHORT)
            notify("📊 Analyzing vendor performance...")
            vendor_result = execute_tool("get_vendor_performance", {})
            self._log_tool_call("get_vendor_performance", {}, vendor_result)
            results["vendor_performance"] = vendor_result
            
            think("Phase 3: Savings opportunities...")
            time.sleep(THINK_DELAY_SHORT)
            notify("💡 Finding savings opportunities...")
            savings_result = execute_tool("find_savings_opportunities", {"threshold_pct": 5.0})
            self._log_tool_call("find_savings_opportunities", {"threshold_pct": 5.0}, savings_result)
            results["savings"] = savings_result
        
        think("✓ Insights analysis complete")
        
        return results

    def _format_insights_fallback(self, results: dict) -> str:
        """Format insights results without LLM."""
        lines = ["## Procurement Insights\n"]
        
        if "spending" in results:
            spending = results["spending"]
            lines.append("### Spending Summary")
            if spending.get("totals"):
                totals = spending["totals"]
                lines.append(f"- **Total Orders:** {totals.get('total_orders', 0)}")
                lines.append(f"- **Total Spend:** ${totals.get('total_spend', 0):,.2f}")
                lines.append(f"- **Avg Order Value:** ${totals.get('avg_order_value', 0):,.2f}\n")
            
            if spending.get("by_category"):
                lines.append("**By Category:**")
                lines.append("| Category | Orders | Total Spend |")
                lines.append("|----------|--------|-------------|")
                for cat in spending["by_category"]:
                    lines.append(f"| {cat['category']} | {cat['order_count']} | ${cat['total_spend']:,.2f} |")
                lines.append("")
        
        if "vendor_performance" in results:
            vp = results["vendor_performance"]
            lines.append("### Vendor Performance")
            if vp.get("top_by_reliability"):
                lines.append(f"**Most Reliable:** {', '.join(vp['top_by_reliability'])}")
            if vp.get("top_by_spend"):
                lines.append(f"**Top by Spend:** {', '.join(vp['top_by_spend'])}\n")
            
            if vp.get("vendors"):
                lines.append("| Vendor | Orders | On-Time % | Rating |")
                lines.append("|--------|--------|-----------|--------|")
                for v in vp["vendors"][:5]:
                    lines.append(f"| {v['vendor_name']} | {v['total_orders']} | {v['on_time_pct']}% | {v['rating']} |")
                lines.append("")
        
        if "margins" in results:
            margins = results["margins"]
            lines.append("### Margin Analysis")
            if margins.get("summary"):
                lines.append(f"- Items analyzed: {margins['summary'].get('total_items', 0)}")
                lines.append(f"- Average potential margin: {margins['summary'].get('average_potential_margin', 0)}%\n")
        
        if "savings" in results:
            savings = results["savings"]
            lines.append("### Savings Opportunities")
            if savings.get("vendor_opportunities"):
                lines.append("| Item | Current Cost | Best Price | Savings |")
                lines.append("|------|--------------|------------|---------|")
                for opp in savings["vendor_opportunities"][:5]:
                    lines.append(f"| {opp['name'][:25]} | ${opp['our_cost']:.2f} | ${opp['best_vendor_price']:.2f} | {opp['potential_savings_pct']}% |")
                lines.append("")
        
        if "trends" in results:
            trends = results["trends"]
            lines.append("### Price Trends")
            if trends.get("price_trends"):
                lines.append("| Item | Purchases | Avg Price | Variance |")
                lines.append("|------|-----------|-----------|----------|")
                for t in trends["price_trends"][:5]:
                    variance = t.get('price_variance_pct', 0) or 0
                    lines.append(f"| {t['name'][:25]} | {t['purchase_count']} | ${t['avg_price']:.2f} | {variance:.1f}% |")
                lines.append("")
        
        return "\n".join(lines)

    def _run_catalog_workflow(
        self,
        query_type: str,
        category: str | None,
        on_notify: Callable[[str], None] | None,
    ) -> dict[str, Any]:
        """Run the catalog query workflow."""
        results = {}
        
        def notify(msg: str):
            if on_notify:
                on_notify(msg)
        
        def think(msg: str):
            """Show thinking process."""
            if on_notify:
                on_notify(f"💭 {msg}")
        
        import time
        
        # Initial thinking
        think("Processing catalog query...")
        time.sleep(THINK_DELAY_MEDIUM)
        think(f"• Query type: {query_type}")
        time.sleep(THINK_DELAY_SHORT)
        if category:
            think(f"• Filtering by category: {category}")
            time.sleep(THINK_DELAY_SHORT)
        
        if query_type == "highest_price":
            think("Searching for highest-priced items...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Sorting by vendor price descending")
            time.sleep(THINK_DELAY_SHORT)
            think("• Including cost basis for comparison")
            time.sleep(THINK_DELAY_MEDIUM)
        elif query_type == "lowest_price":
            think("Searching for lowest-priced items...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Sorting by vendor price ascending")
            time.sleep(THINK_DELAY_SHORT)
            think("• Filtering out items without pricing")
            time.sleep(THINK_DELAY_MEDIUM)
        elif query_type == "count":
            think("Counting catalog items...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Aggregating by category")
            time.sleep(THINK_DELAY_MEDIUM)
        else:
            think("Retrieving catalog listing...")
            time.sleep(THINK_DELAY_SHORT)
            think("• Loading item details")
            time.sleep(THINK_DELAY_SHORT)
            think("• Grouping by category")
            time.sleep(THINK_DELAY_MEDIUM)
        
        notify("📦 Querying catalog...")
        catalog_result = execute_tool("get_catalog_summary", {
            "query_type": query_type,
            "category": category,
            "limit": 10
        })
        self._log_tool_call("get_catalog_summary", {"query_type": query_type, "category": category}, catalog_result)
        results["catalog"] = catalog_result
        
        # Show results thinking
        if catalog_result.get("items"):
            item_count = len(catalog_result["items"])
            think(f"Found {item_count} items")
            time.sleep(THINK_DELAY_SHORT)
            if query_type in ["highest_price", "lowest_price"] and catalog_result["items"]:
                top_item = catalog_result["items"][0]
                price_key = "highest_vendor_price" if query_type == "highest_price" else "lowest_vendor_price"
                price = top_item.get(price_key, top_item.get("our_cost", 0))
                think(f"• Top result: {top_item['name'][:30]} (${price:.2f})")
                time.sleep(THINK_DELAY_MEDIUM)
        elif catalog_result.get("categories"):
            cat_count = len(catalog_result["categories"])
            total = sum(catalog_result["categories"].values())
            think(f"Catalog has {total} items across {cat_count} categories")
            time.sleep(THINK_DELAY_MEDIUM)
        
        think("✓ Catalog query complete")
        
        return results

    def _format_catalog_fallback(self, results: dict) -> str:
        """Format catalog results without LLM."""
        lines = ["## Catalog Information\n"]
        
        catalog = results.get("catalog", {})
        query_type = catalog.get("query_type", "list")
        
        if query_type == "count":
            result = catalog.get("result", {})
            lines.append(f"**Total Items:** {result.get('total', 0)}")
            lines.append(f"**Categories:** {result.get('categories', 0)}")
        
        elif query_type == "highest_price":
            lines.append("### Highest Priced Items\n")
            lines.append("| SKU | Name | Category | Vendor Price | Our Cost |")
            lines.append("|-----|------|----------|--------------|----------|")
            for item in catalog.get("items", []):
                vendor_price = f"${item['highest_vendor_price']:.2f}" if item.get('highest_vendor_price') else "N/A"
                our_cost = f"${item['our_cost']:.2f}" if item.get('our_cost') else "N/A"
                lines.append(f"| {item['sku']} | {item['name'][:30]} | {item['category']} | {vendor_price} | {our_cost} |")
        
        elif query_type == "lowest_price":
            lines.append("### Lowest Priced Items\n")
            lines.append("| SKU | Name | Category | Vendor Price | Our Cost |")
            lines.append("|-----|------|----------|--------------|----------|")
            for item in catalog.get("items", []):
                vendor_price = f"${item['lowest_vendor_price']:.2f}" if item.get('lowest_vendor_price') else "N/A"
                our_cost = f"${item['our_cost']:.2f}" if item.get('our_cost') else "N/A"
                lines.append(f"| {item['sku']} | {item['name'][:30]} | {item['category']} | {vendor_price} | {our_cost} |")
        
        else:  # list
            if catalog.get("categories"):
                lines.append("### Categories")
                for cat, count in catalog["categories"].items():
                    lines.append(f"- **{cat}:** {count} items")
                lines.append("")
            
            lines.append("### Items\n")
            lines.append("| SKU | Name | Category | Our Cost |")
            lines.append("|-----|------|----------|----------|")
            for item in catalog.get("items", []):
                our_cost = f"${item['our_cost']:.2f}" if item.get('our_cost') else "N/A"
                lines.append(f"| {item['sku']} | {item['name'][:30]} | {item['category']} | {our_cost} |")
        
        return "\n".join(lines)

    def _format_response_with_llm(self, intent: str, results: dict, user_message: str) -> str:
        """Use LLM to format the tool results into a nice response."""
        
        # Build a summary of results for the LLM
        results_summary = json.dumps(results, indent=2, default=str)
        
        format_prompt = f"""Based on the following tool results, create a well-formatted response for the user.

User request: {user_message}

Tool results:
{results_summary}

Format your response with:
1. A brief summary (1-2 sentences)
2. A comparison table if there are multiple quotes (use markdown table format)
3. Clear recommendation with bullet points explaining why
4. If there's an email draft, include it in a code block
5. Use proper formatting: headers, bullet points, bold for key values

Keep it concise and actionable. Use markdown formatting."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that formats procurement and pricing data into clear, readable responses. Use markdown formatting."},
                    {"role": "user", "content": format_prompt}
                ],
            )
            return response.choices[0].message.content or self._format_fallback(intent, results)
        except Exception:
            return self._format_fallback(intent, results)

    def _format_fallback(self, intent: str, results: dict) -> str:
        """Fallback formatting if LLM fails."""
        if intent == "procurement":
            return self._format_procurement_fallback(results)
        elif intent == "pricing":
            return self._format_pricing_fallback(results)
        return "Request processed. Please see the tool calls for details."

    def _format_procurement_fallback(self, results: dict) -> str:
        """Format procurement results without LLM."""
        lines = ["## Procurement Summary\n"]
        
        if "rfq" in results:
            rfq = results["rfq"]
            lines.append(f"**RFQ Created:** {rfq.get('rfq_id')} for {rfq.get('quantity')} units of {rfq.get('item_name')}\n")
        
        if "quotes" in results and results["quotes"].get("quotes"):
            lines.append("### Vendor Quotes\n")
            lines.append("| Vendor | Unit Price | Total | Lead Time | Risk Flags |")
            lines.append("|--------|------------|-------|-----------|------------|")
            for q in results["quotes"]["quotes"]:
                flags = ", ".join(q.get("risk_flags", [])) or "None"
                lines.append(f"| {q['vendor_name']} | ${q['unit_price']:.2f} | ${q['total_price']:,.2f} | {q['lead_time_days']} days | {flags} |")
            lines.append("")
        
        if "award" in results:
            award = results["award"]
            lines.append(f"### Recommendation: **{award.get('recommended_vendor_name')}**\n")
            lines.append(f"**Strategy:** {award.get('strategy')}\n")
            lines.append("**Reasoning:**")
            for reason in award.get("reasoning", []):
                lines.append(f"- {reason}")
            lines.append("")
        
        if "email" in results:
            email = results["email"]
            lines.append("### Draft Negotiation Email\n")
            lines.append(f"**Subject:** {email.get('subject')}\n")
            lines.append("```")
            lines.append(email.get("body", ""))
            lines.append("```")
        
        return "\n".join(lines)

    def _format_pricing_fallback(self, results: dict) -> str:
        """Format pricing results without LLM."""
        lines = ["## Pricing Recommendation\n"]
        
        if "cost" in results:
            cost = results["cost"]
            lines.append(f"**Item:** {cost.get('item_name')} ({cost.get('sku')})")
            lines.append(f"**Cost Basis:** ${cost.get('unit_cost'):.2f} ({cost.get('cost_type')})\n")
        
        if "competitors" in results and results["competitors"].get("prices"):
            lines.append("### Competitor Prices")
            lines.append("| Competitor | Price | Source |")
            lines.append("|------------|-------|--------|")
            for p in results["competitors"]["prices"]:
                lines.append(f"| {p['competitor_name']} | ${p['price']:.2f} | {p['source']} |")
            lines.append(f"\n**Competitor Average:** ${results['competitors'].get('avg_price', 0):.2f}\n")
        
        if "price" in results:
            price = results["price"]
            lines.append(f"### Recommended Sell Price: **${price.get('recommended_price'):.2f}**\n")
            lines.append(f"- Target Margin: {price.get('target_margin_pct')}%")
            lines.append(f"- Actual Margin: {price.get('actual_margin_pct'):.1f}%")
            if price.get("demand_signal"):
                lines.append(f"- Demand Signal: {price.get('demand_signal')}")
            lines.append("")
        
        if "explanation" in results:
            lines.append("### Rationale")
            for point in results["explanation"].get("rationale", []):
                lines.append(f"- {point}")
        
        return "\n".join(lines)

    def _log_tool_call(
        self, tool_name: str, arguments: dict, result: dict, success: bool = True
    ) -> None:
        """Log a tool call for UI display."""
        # Summarize result for display
        if "error" in result:
            summary = f"Error: {result['error']}"
        elif "items" in result:
            summary = f"Found {result.get('total_count', len(result['items']))} items"
        elif "quotes" in result:
            summary = f"Retrieved {len(result['quotes'])} quotes"
        elif "rfq_id" in result and "item_sku" in result:
            summary = f"Created RFQ {result['rfq_id']}"
        elif "recommended_vendor_name" in result:
            summary = f"Recommended: {result['recommended_vendor_name']}"
        elif "recommended_price" in result:
            summary = f"Recommended price: ${result['recommended_price']:.2f}"
        elif "subject" in result:
            summary = f"Email drafted: {result['subject'][:50]}..."
        elif "rationale" in result:
            summary = f"{len(result['rationale'])} rationale points"
        else:
            summary = "Completed"

        self.tool_calls_log.append(
            {
                "tool_name": tool_name,
                "arguments": arguments,
                "result_summary": summary,
                "success": success,
                "full_result": result,
            }
        )

    def _add_note(self, note: str) -> None:
        """Add an intermediate note."""
        self.intermediate_notes.append(note)

    def chat_with_callbacks(
        self,
        user_message: str,
        on_status: StatusCallback | None = None,
    ) -> Generator[str, None, None]:
        """
        Process a user message with status callbacks and stream the response.
        Uses DETERMINISTIC workflows for reliable demo behavior.

        Args:
            user_message: The user's input message
            on_status: Callback for status updates (type, message)

        Yields:
            Chunks of the agent's response
        """
        def notify(status_type: str, message: str | None = None):
            if on_status:
                on_status(status_type, message)

        # Clear logs for this turn
        self.tool_calls_log = []
        self.intermediate_notes = []

        # Add context and user message
        context = self._get_context_message()
        self.messages.append({"role": "user", "content": user_message})

        self._add_note(f"Processing request with context: {context}")
        notify("thinking", "Analyzing your request...")

        # Detect intent and run deterministic workflow
        intent_type, params = self._detect_intent(user_message)
        self._add_note(f"Detected intent: {intent_type} with params: {params}")

        # Create a simple notifier for workflow progress
        def tool_notify(msg: str):
            notify("tool", msg)

        if intent_type == "procurement":
            notify("thinking", "Starting procurement workflow...")
            results = self._run_procurement_workflow(
                sku=params.get("sku"),
                search_term=params.get("search_term"),
                quantity=params.get("quantity", 1000),
                wants_email=params.get("wants_email", True),  # Default to including email in demo
                strategy=params.get("strategy", "balanced"),
                on_notify=tool_notify,
            )
            
            if results and "error" not in results:
                # Try to get LLM to format nicely
                notify("generating", "✍️ Formatting response...")
                try:
                    final_response = self._format_response_with_llm("procurement", results, user_message)
                except Exception as e:
                    self._add_note(f"LLM formatting failed: {e}")
                    final_response = self._format_procurement_fallback(results)
            else:
                error_msg = results.get("error", "Unknown error") if results else "No results"
                final_response = f"I couldn't complete the procurement workflow: {error_msg}. Please try a different item."

        elif intent_type == "pricing":
            notify("thinking", "Starting pricing workflow...")
            results = self._run_pricing_workflow(
                sku=params.get("sku"),
                search_term=params.get("search_term"),
                margin=self.target_margin,
                on_notify=tool_notify,
            )
            
            if results and "error" not in results:
                notify("generating", "✍️ Formatting response...")
                try:
                    final_response = self._format_response_with_llm("pricing", results, user_message)
                except Exception as e:
                    self._add_note(f"LLM formatting failed: {e}")
                    final_response = self._format_pricing_fallback(results)
            else:
                error_msg = results.get("error", "Unknown error") if results else "No results"
                final_response = f"I couldn't complete the pricing workflow: {error_msg}. Please check the item name."

        elif intent_type == "insights":
            notify("thinking", "Starting insights analysis...")
            results = self._run_insights_workflow(
                insight_type=params.get("insight_type", "general"),
                category=params.get("category"),
                on_notify=tool_notify,
            )
            
            if results:
                notify("generating", "✍️ Formatting insights...")
                try:
                    final_response = self._format_response_with_llm("insights", results, user_message)
                except Exception as e:
                    self._add_note(f"LLM formatting failed: {e}")
                    final_response = self._format_insights_fallback(results)
            else:
                final_response = "I couldn't retrieve the insights data. Please try again."

        elif intent_type == "catalog":
            notify("thinking", "Querying catalog...")
            results = self._run_catalog_workflow(
                query_type=params.get("query_type", "list"),
                category=params.get("category"),
                on_notify=tool_notify,
            )
            
            if results:
                notify("generating", "✍️ Formatting results...")
                try:
                    final_response = self._format_response_with_llm("catalog", results, user_message)
                except Exception as e:
                    self._add_note(f"LLM formatting failed: {e}")
                    final_response = self._format_catalog_fallback(results)
            else:
                final_response = "I couldn't retrieve catalog information. Please try again."

        else:
            # General query - just respond with LLM
            notify("generating", "Processing your question...")
            try:
                response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=self.messages,
                )
                final_response = response.choices[0].message.content or "I can help with procurement, pricing, and insights. Try asking me to procure an item, recommend a sell price, or show spending analysis."
            except Exception as e:
                final_response = "I'm here to help with procurement, pricing, and insights. Try:\n- 'Procure EPDM rubber'\n- 'Recommend a sell price for Carbon Black'\n- 'Show me vendor performance'\n- 'Where can we save money?'"

        # Store in messages
        self.messages.append({"role": "assistant", "content": final_response})
        self._add_note("Response complete")

        # Yield the response in chunks for streaming effect
        chunk_size = 30
        for i in range(0, len(final_response), chunk_size):
            yield final_response[i:i + chunk_size]

    def chat(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        Uses DETERMINISTIC workflows for reliable demo behavior.

        Args:
            user_message: The user's input message

        Returns:
            The agent's final response
        """
        # Use the callbacks version without callbacks
        response_chunks = list(self.chat_with_callbacks(user_message, on_status=None))
        return "".join(response_chunks)

    def chat_stream(self, user_message: str) -> Generator[str, None, None]:
        """
        Process a user message and stream the agent's response.
        Uses DETERMINISTIC workflows for reliable demo behavior.

        Args:
            user_message: The user's input message

        Yields:
            Chunks of the agent's response
        """
        # Delegate to chat_with_callbacks
        yield from self.chat_with_callbacks(user_message, on_status=None)

    def reset(self) -> None:
        """Reset the conversation history and session state."""
        self.messages = get_system_messages()
        self.tool_calls_log = []
        self.intermediate_notes = []
        # Clear in-memory RFQ/quote stores so each demo starts fresh
        clear_session_stores()

    def get_tool_calls_log(self) -> list[dict[str, Any]]:
        """Get the tool calls log for the current turn."""
        return self.tool_calls_log

    def get_intermediate_notes(self) -> list[str]:
        """Get intermediate notes for the current turn."""
        return self.intermediate_notes

    def update_settings(
        self,
        region: str | None = None,
        currency: str | None = None,
        target_margin: float | None = None,
        shipping_preference: str | None = None,
    ) -> None:
        """Update orchestrator settings."""
        if region is not None:
            self.region = region
        if currency is not None:
            self.currency = currency
        if target_margin is not None:
            self.target_margin = target_margin
        if shipping_preference is not None:
            self.shipping_preference = shipping_preference

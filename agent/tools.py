"""
Pure Python tool functions for Procurement and Pricing agents.

All tools return JSON-serializable dicts.
Data is loaded from the local SQLite database.
"""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# In-memory storage for RFQs and quotes (simulates session state)
_rfq_store: dict[str, dict] = {}
_quote_store: dict[str, list[dict]] = {}


def clear_session_stores() -> None:
    """Clear the in-memory RFQ and quote stores. Called on conversation reset."""
    global _rfq_store, _quote_store
    _rfq_store.clear()
    _quote_store.clear()


# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "procurement.db"


def _get_db_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# =============================================================================
# PROCUREMENT TOOLS
# =============================================================================


def search_items(query: str, limit: int = 10) -> dict[str, Any]:
    """
    Search for items/SKUs matching a query.

    Args:
        query: Search term (matches name, category, or description)
        limit: Maximum number of results

    Returns:
        Dict with 'items' list and 'total_count'
    """
    conn = _get_db_connection()
    cursor = conn.cursor()

    search_term = f"%{query.lower()}%"
    
    # Use a scoring system to prioritize name matches over description matches
    # Score: 3 for name match, 2 for category match, 1 for description match
    cursor.execute(
        """
        SELECT sku, name, category, description,
               (CASE WHEN LOWER(name) LIKE ? THEN 3 ELSE 0 END +
                CASE WHEN LOWER(category) LIKE ? THEN 2 ELSE 0 END +
                CASE WHEN LOWER(description) LIKE ? THEN 1 ELSE 0 END) AS relevance
        FROM items
        WHERE LOWER(name) LIKE ? OR LOWER(category) LIKE ? OR LOWER(description) LIKE ?
        ORDER BY relevance DESC, name ASC
        LIMIT ?
        """,
        (search_term, search_term, search_term, search_term, search_term, search_term, limit),
    )

    rows = cursor.fetchall()
    conn.close()

    # Remove the relevance score from output
    items = [{"sku": row["sku"], "name": row["name"], "category": row["category"], "description": row["description"]} for row in rows]
    return {"items": items, "total_count": len(items)}


def get_catalog_summary(
    query_type: str = "list",
    category: Optional[str] = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Get catalog information - list items, find highest/lowest priced, count items.

    Args:
        query_type: "list", "highest_price", "lowest_price", or "count"
        category: Filter by category (optional)
        limit: Number of items to return

    Returns:
        Dict with catalog information
    """
    conn = _get_db_connection()
    cursor = conn.cursor()

    where_clause = "WHERE i.category = ?" if category else ""
    params = [category] if category else []

    if query_type == "count":
        cursor.execute(f"""
            SELECT COUNT(*) as total, 
                   (SELECT COUNT(DISTINCT category) FROM items) as categories
            FROM items i
            {where_clause}
        """, params)
        result = dict(cursor.fetchone())
        conn.close()
        return {"query_type": "count", "result": result}

    elif query_type == "highest_price":
        cursor.execute(f"""
            SELECT i.sku, i.name, i.category, i.description,
                   MAX(pl.base_price) as highest_vendor_price,
                   cb.unit_cost as our_cost
            FROM items i
            LEFT JOIN price_lists pl ON i.sku = pl.item_sku
            LEFT JOIN cost_basis cb ON i.sku = cb.sku
            {where_clause}
            GROUP BY i.sku
            ORDER BY highest_vendor_price DESC
            LIMIT ?
        """, params + [limit])
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"query_type": "highest_price", "items": items}

    elif query_type == "lowest_price":
        cursor.execute(f"""
            SELECT i.sku, i.name, i.category, i.description,
                   MIN(pl.base_price) as lowest_vendor_price,
                   cb.unit_cost as our_cost
            FROM items i
            LEFT JOIN price_lists pl ON i.sku = pl.item_sku
            LEFT JOIN cost_basis cb ON i.sku = cb.sku
            {where_clause}
            GROUP BY i.sku
            HAVING lowest_vendor_price IS NOT NULL
            ORDER BY lowest_vendor_price ASC
            LIMIT ?
        """, params + [limit])
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return {"query_type": "lowest_price", "items": items}

    else:  # list
        cursor.execute(f"""
            SELECT i.sku, i.name, i.category, i.description,
                   cb.unit_cost as our_cost,
                   (SELECT MIN(pl.base_price) FROM price_lists pl WHERE pl.item_sku = i.sku) as min_vendor_price,
                   (SELECT MAX(pl.base_price) FROM price_lists pl WHERE pl.item_sku = i.sku) as max_vendor_price
            FROM items i
            LEFT JOIN cost_basis cb ON i.sku = cb.sku
            {where_clause}
            ORDER BY i.category, i.name
            LIMIT ?
        """, params + [limit])
        items = [dict(row) for row in cursor.fetchall()]
        
        # Get category counts
        cursor.execute("SELECT category, COUNT(*) as count FROM items GROUP BY category")
        categories = {row["category"]: row["count"] for row in cursor.fetchall()}
        
        conn.close()
        return {"query_type": "list", "items": items, "categories": categories, "total": len(items)}


def create_rfq(
    item_sku: str,
    quantity: int,
    region: str,
    constraints: Optional[str] = None,
) -> dict[str, Any]:
    """
    Create a request for quotation (RFQ).

    Args:
        item_sku: SKU of the item to quote
        quantity: Quantity needed
        region: Delivery region
        constraints: Additional constraints (e.g., "delivery within 3 weeks")

    Returns:
        Dict with RFQ details including rfq_id
    """
    conn = _get_db_connection()
    cursor = conn.cursor()

    # Get item details
    cursor.execute("SELECT sku, name FROM items WHERE sku = ?", (item_sku,))
    item = cursor.fetchone()
    conn.close()

    if not item:
        return {"error": f"Item with SKU '{item_sku}' not found"}

    rfq_id = f"RFQ-{uuid.uuid4().hex[:8].upper()}"

    rfq = {
        "rfq_id": rfq_id,
        "item_sku": item_sku,
        "item_name": item["name"],
        "quantity": quantity,
        "region": region,
        "constraints": constraints,
        "status": "open",
        "created_at": datetime.now().isoformat(),
    }

    _rfq_store[rfq_id] = rfq
    return rfq


def get_quotes(rfq_id: str) -> dict[str, Any]:
    """
    Get vendor quotes for an RFQ (simulates vendor responses).

    Args:
        rfq_id: The RFQ identifier

    Returns:
        Dict with 'quotes' list
    """
    if rfq_id not in _rfq_store:
        return {"error": f"RFQ '{rfq_id}' not found"}

    rfq = _rfq_store[rfq_id]

    # Check if quotes already generated
    if rfq_id in _quote_store:
        return {"rfq_id": rfq_id, "quotes": _quote_store[rfq_id]}

    conn = _get_db_connection()
    cursor = conn.cursor()

    # Get vendors for this region (or global vendors)
    cursor.execute(
        """
        SELECT v.vendor_id, v.name, v.region, v.rating, v.reliability_score, v.typical_lead_time_days
        FROM vendors v
        WHERE v.region = ? OR v.region = 'Global'
        """,
        (rfq["region"],),
    )
    vendors = cursor.fetchall()

    # Get price list entries for this item
    cursor.execute(
        """
        SELECT pl.vendor_id, pl.base_price, pl.moq, pl.volume_discount_threshold,
               pl.volume_discount_pct, pl.rush_surcharge_pct, pl.lead_time_days
        FROM price_lists pl
        WHERE pl.item_sku = ?
        """,
        (rfq["item_sku"],),
    )
    price_entries = {row["vendor_id"]: dict(row) for row in cursor.fetchall()}
    conn.close()

    quotes = []
    quantity = rfq["quantity"]

    for vendor in vendors:
        vendor_id = vendor["vendor_id"]
        if vendor_id not in price_entries:
            continue  # This vendor doesn't sell this item

        price_info = price_entries[vendor_id]
        base_price = price_info["base_price"]
        lead_time = price_info["lead_time_days"]

        # Apply volume discount if applicable
        volume_discount_applied = False
        if quantity >= price_info["volume_discount_threshold"]:
            base_price *= 1 - (price_info["volume_discount_pct"] / 100)
            volume_discount_applied = True

        # Check for rush shipping (constraints parsing)
        rush_surcharge_applied = False
        constraints = rfq.get("constraints") or ""
        if "rush" in constraints.lower() or "urgent" in constraints.lower():
            base_price *= 1 + (price_info["rush_surcharge_pct"] / 100)
            rush_surcharge_applied = True
            lead_time = max(3, lead_time - 5)  # Rush reduces lead time

        # Determine risk flags
        risk_flags = []
        if vendor["reliability_score"] < 80:
            risk_flags.append("Low reliability score")
        if vendor["rating"] < 3.5:
            risk_flags.append("Below average rating")
        if quantity < price_info["moq"]:
            risk_flags.append(f"Below MOQ ({price_info['moq']})")
        if lead_time > 21:
            risk_flags.append("Long lead time")

        quote = {
            "quote_id": f"Q-{uuid.uuid4().hex[:8].upper()}",
            "rfq_id": rfq_id,
            "vendor_id": vendor_id,
            "vendor_name": vendor["name"],
            "unit_price": round(base_price, 2),
            "total_price": round(base_price * quantity, 2),
            "lead_time_days": lead_time,
            "moq": price_info["moq"],
            "currency": "USD",
            "volume_discount_applied": volume_discount_applied,
            "rush_surcharge_applied": rush_surcharge_applied,
            "risk_flags": risk_flags,
            "vendor_rating": vendor["rating"],
            "vendor_reliability": vendor["reliability_score"],
        }
        quotes.append(quote)

    _quote_store[rfq_id] = quotes
    return {"rfq_id": rfq_id, "quotes": quotes}


def compare_quotes(rfq_id: str) -> dict[str, Any]:
    """
    Compare and rank quotes for an RFQ.

    Args:
        rfq_id: The RFQ identifier

    Returns:
        Dict with sorted quotes and comparison analysis
    """
    quotes_result = get_quotes(rfq_id)
    if "error" in quotes_result:
        return quotes_result

    quotes = quotes_result["quotes"]
    if not quotes:
        return {"error": "No quotes available for this RFQ"}

    # Sort by total price
    sorted_by_price = sorted(quotes, key=lambda q: q["total_price"])
    # Sort by lead time
    sorted_by_time = sorted(quotes, key=lambda q: q["lead_time_days"])

    lowest_cost = sorted_by_price[0]
    fastest = sorted_by_time[0]

    comparison_notes = [
        f"Lowest cost: {lowest_cost['vendor_name']} at ${lowest_cost['total_price']:,.2f}",
        f"Fastest delivery: {fastest['vendor_name']} in {fastest['lead_time_days']} days",
    ]

    # Calculate price spread
    if len(sorted_by_price) > 1:
        price_spread = sorted_by_price[-1]["total_price"] - sorted_by_price[0]["total_price"]
        comparison_notes.append(f"Price spread: ${price_spread:,.2f}")

    return {
        "rfq_id": rfq_id,
        "quotes": sorted_by_price,  # Return sorted by price
        "lowest_cost_vendor": lowest_cost["vendor_name"],
        "fastest_vendor": fastest["vendor_name"],
        "comparison_notes": comparison_notes,
    }


def recommend_award(rfq_id: str, strategy: str = "balanced") -> dict[str, Any]:
    """
    Recommend an award decision for an RFQ.

    Args:
        rfq_id: The RFQ identifier
        strategy: Award strategy - 'lowest_cost', 'fastest', or 'balanced'

    Returns:
        Dict with recommendation details and reasoning
    """
    quotes_result = get_quotes(rfq_id)
    if "error" in quotes_result:
        return quotes_result

    quotes = quotes_result["quotes"]
    if not quotes:
        return {"error": "No quotes available for this RFQ"}

    def score_quote(q: dict) -> float:
        """Calculate a composite score (lower is better)."""
        if strategy == "lowest_cost":
            return q["total_price"]
        elif strategy == "fastest":
            return q["lead_time_days"] * 1000 + q["total_price"]
        else:  # balanced
            # Normalize and combine factors
            price_score = q["total_price"] / 1000  # Normalize
            time_score = q["lead_time_days"] * 5
            risk_score = len(q["risk_flags"]) * 50
            reliability_bonus = (100 - q["vendor_reliability"]) * 2
            return price_score + time_score + risk_score + reliability_bonus

    scored = sorted(quotes, key=score_quote)
    winner = scored[0]

    reasoning = []
    if strategy == "lowest_cost":
        reasoning.append(f"Selected based on lowest total cost: ${winner['total_price']:,.2f}")
    elif strategy == "fastest":
        reasoning.append(f"Selected based on fastest delivery: {winner['lead_time_days']} days")
    else:
        reasoning.append("Selected using balanced scoring (cost, speed, reliability, risk)")

    reasoning.append(f"Vendor rating: {winner['vendor_rating']}/5.0")
    reasoning.append(f"Reliability score: {winner['vendor_reliability']}%")

    if winner["volume_discount_applied"]:
        reasoning.append("Volume discount applied to pricing")

    if winner["risk_flags"]:
        reasoning.append(f"Risk considerations: {', '.join(winner['risk_flags'])}")
    else:
        reasoning.append("No risk flags identified")

    alternatives = [
        {
            "vendor_name": q["vendor_name"],
            "total_price": q["total_price"],
            "lead_time_days": q["lead_time_days"],
        }
        for q in scored[1:3]  # Top 2 alternatives
    ]

    return {
        "rfq_id": rfq_id,
        "recommended_vendor_id": winner["vendor_id"],
        "recommended_vendor_name": winner["vendor_name"],
        "strategy": strategy,
        "reasoning": reasoning,
        "quote_details": winner,
        "alternatives": alternatives,
    }


def draft_supplier_email(
    vendor_id: str, rfq_id: str, ask: str = "better_price"
) -> dict[str, Any]:
    """
    Draft a negotiation email to a supplier.

    Args:
        vendor_id: The vendor to email
        rfq_id: The associated RFQ
        ask: Type of ask - 'better_price', 'faster_delivery', or 'both'

    Returns:
        Dict with email subject and body
    """
    if rfq_id not in _rfq_store:
        return {"error": f"RFQ '{rfq_id}' not found"}

    rfq = _rfq_store[rfq_id]
    quotes = _quote_store.get(rfq_id, [])
    vendor_quote = next((q for q in quotes if q["vendor_id"] == vendor_id), None)

    if not vendor_quote:
        return {"error": f"No quote found for vendor '{vendor_id}' on RFQ '{rfq_id}'"}

    vendor_name = vendor_quote["vendor_name"]
    item_name = rfq["item_name"]
    quantity = rfq["quantity"]
    current_price = vendor_quote["unit_price"]
    current_total = vendor_quote["total_price"]
    lead_time = vendor_quote["lead_time_days"]

    if ask == "better_price":
        subject = f"Quote Review - {item_name} (RFQ: {rfq_id})"
        body = f"""Dear {vendor_name} Team,

Thank you for your quotation on {quantity} units of {item_name} (RFQ: {rfq_id}).

We have reviewed your quote of ${current_price:.2f} per unit (${current_total:,.2f} total) and would like to discuss the possibility of improved pricing. Given our projected volume and potential for a long-term partnership, we believe there may be room for a more competitive rate.

Could you please review and advise if you can offer:
- A reduced unit price for this order
- Volume-based pricing tiers for future orders

We value our relationship with {vendor_name} and look forward to your response.

Best regards"""

    elif ask == "faster_delivery":
        subject = f"Expedited Delivery Request - {item_name} (RFQ: {rfq_id})"
        body = f"""Dear {vendor_name} Team,

Thank you for your quotation on {quantity} units of {item_name} (RFQ: {rfq_id}).

The quoted lead time of {lead_time} days presents a challenge for our project timeline. We would like to explore options for expedited delivery.

Could you please advise:
- The fastest possible delivery timeline
- Any additional costs for expedited shipping
- Partial shipment options if full order cannot be expedited

We appreciate your flexibility and look forward to your response.

Best regards"""

    else:  # both
        subject = f"Quote Optimization Request - {item_name} (RFQ: {rfq_id})"
        body = f"""Dear {vendor_name} Team,

Thank you for your quotation on {quantity} units of {item_name} (RFQ: {rfq_id}).

We are evaluating multiple proposals and would like to discuss how we can optimize both pricing and delivery terms:

Current Quote Summary:
- Unit Price: ${current_price:.2f}
- Total: ${current_total:,.2f}
- Lead Time: {lead_time} days

We would appreciate if you could review and advise on:
1. Improved pricing given our order volume and partnership potential
2. Options for faster delivery without significant cost impact
3. Any value-added services or terms that differentiate your offer

We value our relationship with {vendor_name} and look forward to finding a mutually beneficial arrangement.

Best regards"""

    return {
        "vendor_id": vendor_id,
        "vendor_name": vendor_name,
        "subject": subject,
        "body": body,
        "rfq_id": rfq_id,
        "ask_type": ask,
    }


# =============================================================================
# PRICING TOOLS
# =============================================================================


def get_cost_basis(sku: str, quantity: int = 1) -> dict[str, Any]:
    """
    Get the cost basis for a SKU.

    Args:
        sku: The SKU identifier
        quantity: Quantity (may affect cost for volume)

    Returns:
        Dict with cost basis information
    """
    conn = _get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT i.sku, i.name, cb.unit_cost, cb.cost_type, cb.currency, cb.last_updated
        FROM cost_basis cb
        JOIN items i ON cb.sku = i.sku
        WHERE cb.sku = ?
        """,
        (sku,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"error": f"No cost basis found for SKU '{sku}'"}

    return {
        "sku": row["sku"],
        "item_name": row["name"],
        "unit_cost": row["unit_cost"],
        "cost_type": row["cost_type"],
        "currency": row["currency"],
        "last_updated": row["last_updated"],
    }


def get_competitor_prices(sku: str) -> dict[str, Any]:
    """
    Get competitor price anchors for a SKU.

    Args:
        sku: The SKU identifier

    Returns:
        Dict with competitor prices and analysis
    """
    conn = _get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT cp.sku, cp.competitor_name, cp.price, cp.currency, cp.source, cp.observed_date
        FROM competitor_prices cp
        WHERE cp.sku = ?
        ORDER BY cp.price
        """,
        (sku,),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"error": f"No competitor prices found for SKU '{sku}'", "prices": []}

    prices = [dict(row) for row in rows]
    price_values = [p["price"] for p in prices]

    return {
        "sku": sku,
        "prices": prices,
        "min_price": min(price_values),
        "max_price": max(price_values),
        "avg_price": round(sum(price_values) / len(price_values), 2),
        "count": len(prices),
    }


def recommend_sell_price(
    sku: str,
    cost: float,
    target_margin: float,
    demand_notes: Optional[str] = None,
    competitor_prices: Optional[list[float]] = None,
) -> dict[str, Any]:
    """
    Calculate and recommend a sell price.

    Args:
        sku: The SKU identifier
        cost: Unit cost basis
        target_margin: Target margin percentage (e.g., 35 for 35%)
        demand_notes: Demand signal (e.g., "high demand", "slow-moving")
        competitor_prices: List of competitor prices (optional)

    Returns:
        Dict with recommended price and analysis
    """
    conn = _get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT sku, name FROM items WHERE sku = ?", (sku,))
    item = cursor.fetchone()
    conn.close()

    item_name = item["name"] if item else sku

    # Calculate base price from target margin
    # margin = (price - cost) / price
    # price = cost / (1 - margin)
    margin_decimal = target_margin / 100
    base_price = cost / (1 - margin_decimal)

    # Get demand adjustment
    demand_adjustment = 0
    if demand_notes:
        demand_lower = demand_notes.lower()
        if "high demand" in demand_lower or "hot" in demand_lower:
            demand_adjustment = 0.05  # +5%
        elif "slow" in demand_lower or "low demand" in demand_lower:
            demand_adjustment = -0.05  # -5%

    # Get competitor anchor adjustment
    competitor_adjustment = 0
    competitor_avg = None
    if competitor_prices:
        competitor_avg = sum(competitor_prices) / len(competitor_prices)
        # If our base price is higher than competitor avg, moderate it
        if base_price > competitor_avg * 1.15:
            competitor_adjustment = -0.05  # Pull back 5%
        # If we're significantly below, we might have room
        elif base_price < competitor_avg * 0.85:
            competitor_adjustment = 0.03  # Add 3%

    # Apply adjustments
    adjusted_price = base_price * (1 + demand_adjustment + competitor_adjustment)
    recommended_price = round(adjusted_price, 2)

    # Calculate actual margin
    actual_margin = ((recommended_price - cost) / recommended_price) * 100

    return {
        "sku": sku,
        "item_name": item_name,
        "recommended_price": recommended_price,
        "currency": "USD",
        "cost_basis": cost,
        "target_margin_pct": target_margin,
        "actual_margin_pct": round(actual_margin, 1),
        "competitor_avg": round(competitor_avg, 2) if competitor_avg else None,
        "demand_signal": demand_notes,
        "adjustments": {
            "demand": f"{demand_adjustment:+.0%}" if demand_adjustment else "none",
            "competitor": f"{competitor_adjustment:+.0%}" if competitor_adjustment else "none",
        },
    }


def explain_price(
    sku: str, recommended_price: float, inputs: dict[str, Any]
) -> dict[str, Any]:
    """
    Generate a bullet-point rationale for a recommended price.

    Args:
        sku: The SKU identifier
        recommended_price: The recommended sell price
        inputs: Dict with cost, margin, competitor_avg, demand_notes

    Returns:
        Dict with rationale bullets
    """
    rationale = []

    cost = inputs.get("cost", 0)
    target_margin = inputs.get("target_margin", 0)
    actual_margin = inputs.get("actual_margin", 0)
    competitor_avg = inputs.get("competitor_avg")
    demand_notes = inputs.get("demand_notes")

    rationale.append(f"Cost basis: ${cost:.2f} per unit")
    rationale.append(f"Target margin: {target_margin}% → Actual margin: {actual_margin:.1f}%")

    if competitor_avg:
        diff = recommended_price - competitor_avg
        diff_pct = (diff / competitor_avg) * 100
        position = "above" if diff > 0 else "below"
        rationale.append(
            f"Competitor average: ${competitor_avg:.2f} (positioned {abs(diff_pct):.1f}% {position})"
        )
    else:
        rationale.append("No competitor data available for anchoring")

    if demand_notes:
        rationale.append(f"Demand signal: {demand_notes}")
        if "high" in demand_notes.lower():
            rationale.append("↑ Price adjusted upward for high demand")
        elif "slow" in demand_notes.lower() or "low" in demand_notes.lower():
            rationale.append("↓ Price adjusted downward to stimulate demand")
    else:
        rationale.append("No demand signal provided")

    return {"sku": sku, "recommended_price": recommended_price, "rationale": rationale}


# =============================================================================
# ANALYTICS / INSIGHTS TOOLS
# =============================================================================


def get_spending_summary(
    category: Optional[str] = None,
    vendor_id: Optional[str] = None,
) -> dict[str, Any]:
    """
    Get spending summary by category and/or vendor.

    Args:
        category: Filter by category (Raw Materials, MRO, Packaging, Safety, Office)
        vendor_id: Filter by vendor ID

    Returns:
        Dict with spending breakdown and totals
    """
    conn = _get_db_connection()
    cursor = conn.cursor()

    # Build query based on filters
    where_clauses = []
    params = []
    
    if category:
        where_clauses.append("category = ?")
        params.append(category)
    if vendor_id:
        where_clauses.append("vendor_id = ?")
        params.append(vendor_id)
    
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    # Get total by category
    cursor.execute(f"""
        SELECT category, 
               COUNT(*) as order_count,
               SUM(quantity) as total_units,
               SUM(total_amount) as total_spend,
               AVG(unit_price) as avg_unit_price
        FROM purchase_history
        {where_sql}
        GROUP BY category
        ORDER BY total_spend DESC
    """, params)
    
    by_category = [dict(row) for row in cursor.fetchall()]
    
    # Get total by vendor
    cursor.execute(f"""
        SELECT ph.vendor_id, v.name as vendor_name,
               COUNT(*) as order_count,
               SUM(ph.total_amount) as total_spend,
               AVG(ph.days_late) as avg_days_late
        FROM purchase_history ph
        JOIN vendors v ON ph.vendor_id = v.vendor_id
        {where_sql}
        GROUP BY ph.vendor_id
        ORDER BY total_spend DESC
    """, params)
    
    by_vendor = [dict(row) for row in cursor.fetchall()]
    
    # Get grand totals
    cursor.execute(f"""
        SELECT COUNT(*) as total_orders,
               SUM(total_amount) as total_spend,
               AVG(total_amount) as avg_order_value
        FROM purchase_history
        {where_sql}
    """, params)
    
    totals = dict(cursor.fetchone())
    conn.close()
    
    return {
        "by_category": by_category,
        "by_vendor": by_vendor,
        "totals": totals,
        "filters_applied": {"category": category, "vendor_id": vendor_id}
    }


def get_vendor_performance() -> dict[str, Any]:
    """
    Get vendor performance rankings based on historical purchases.

    Returns:
        Dict with vendor rankings by various metrics
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    # Get vendor performance metrics
    cursor.execute("""
        SELECT 
            ph.vendor_id,
            v.name as vendor_name,
            v.rating,
            v.reliability_score,
            COUNT(DISTINCT ph.po_id) as total_orders,
            SUM(ph.total_amount) as total_spend,
            AVG(ph.unit_price) as avg_unit_price,
            AVG(ph.days_late) as avg_days_late,
            SUM(CASE WHEN ph.days_late = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as on_time_pct
        FROM purchase_history ph
        JOIN vendors v ON ph.vendor_id = v.vendor_id
        GROUP BY ph.vendor_id
        ORDER BY total_spend DESC
    """)
    
    vendors = [dict(row) for row in cursor.fetchall()]
    
    # Calculate rankings
    for vendor in vendors:
        # Round percentages
        vendor['on_time_pct'] = round(vendor['on_time_pct'], 1)
        vendor['avg_days_late'] = round(vendor['avg_days_late'], 1)
    
    # Sort by different criteria for rankings
    by_spend = sorted(vendors, key=lambda x: x['total_spend'], reverse=True)
    by_reliability = sorted(vendors, key=lambda x: x['on_time_pct'], reverse=True)
    by_rating = sorted(vendors, key=lambda x: x['rating'], reverse=True)
    
    conn.close()
    
    return {
        "vendors": vendors,
        "top_by_spend": [v['vendor_name'] for v in by_spend[:3]],
        "top_by_reliability": [v['vendor_name'] for v in by_reliability[:3]],
        "top_by_rating": [v['vendor_name'] for v in by_rating[:3]],
    }


def get_margin_analysis(category: Optional[str] = None) -> dict[str, Any]:
    """
    Analyze margins across items comparing cost basis vs competitor prices.

    Args:
        category: Filter by category (optional)

    Returns:
        Dict with margin analysis by item
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    where_sql = "WHERE i.category = ?" if category else ""
    params = [category] if category else []
    
    # Get items with cost basis and competitor data
    cursor.execute(f"""
        SELECT 
            i.sku,
            i.name,
            i.category,
            cb.unit_cost,
            cb.cost_type,
            (SELECT AVG(cp.price) FROM competitor_prices cp WHERE cp.sku = i.sku) as avg_competitor_price,
            (SELECT COUNT(*) FROM competitor_prices cp WHERE cp.sku = i.sku) as competitor_count,
            dn.signal as demand_signal
        FROM items i
        LEFT JOIN cost_basis cb ON i.sku = cb.sku
        LEFT JOIN demand_notes dn ON i.sku = dn.sku
        {where_sql}
        ORDER BY i.category, i.name
    """, params)
    
    items = []
    for row in cursor.fetchall():
        item = dict(row)
        
        # Calculate potential margin if we have both cost and competitor price
        if item['unit_cost'] and item['avg_competitor_price']:
            # If we sell at competitor avg price, what's our margin?
            potential_margin = ((item['avg_competitor_price'] - item['unit_cost']) / item['avg_competitor_price']) * 100
            item['potential_margin_pct'] = round(potential_margin, 1)
            
            # Price position vs market
            item['vs_market_pct'] = round(((item['avg_competitor_price'] - item['unit_cost']) / item['unit_cost']) * 100, 1)
        else:
            item['potential_margin_pct'] = None
            item['vs_market_pct'] = None
        
        items.append(item)
    
    conn.close()
    
    # Calculate summary stats
    items_with_margin = [i for i in items if i['potential_margin_pct'] is not None]
    avg_margin = sum(i['potential_margin_pct'] for i in items_with_margin) / len(items_with_margin) if items_with_margin else 0
    
    return {
        "items": items,
        "summary": {
            "total_items": len(items),
            "items_with_competitor_data": len(items_with_margin),
            "average_potential_margin": round(avg_margin, 1),
        },
        "filter": category
    }


def find_savings_opportunities(threshold_pct: float = 10.0) -> dict[str, Any]:
    """
    Find items where we may be overpaying compared to market or other vendors.

    Args:
        threshold_pct: Minimum percentage above market to flag (default 10%)

    Returns:
        Dict with savings opportunities
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    opportunities = []
    
    # Find items where our last purchase price exceeds the lowest available vendor price
    cursor.execute("""
        SELECT 
            i.sku,
            i.name,
            i.category,
            cb.unit_cost as our_cost,
            cb.cost_type,
            MIN(pl.base_price) as best_vendor_price,
            (SELECT v.name FROM vendors v WHERE v.vendor_id = 
                (SELECT pl2.vendor_id FROM price_lists pl2 WHERE pl2.item_sku = i.sku ORDER BY pl2.base_price LIMIT 1)
            ) as best_vendor_name
        FROM items i
        JOIN cost_basis cb ON i.sku = cb.sku
        JOIN price_lists pl ON i.sku = pl.item_sku
        GROUP BY i.sku
        HAVING our_cost > best_vendor_price * (1 + ? / 100)
    """, (threshold_pct,))
    
    for row in cursor.fetchall():
        item = dict(row)
        savings_pct = ((item['our_cost'] - item['best_vendor_price']) / item['our_cost']) * 100
        item['potential_savings_pct'] = round(savings_pct, 1)
        item['savings_per_unit'] = round(item['our_cost'] - item['best_vendor_price'], 2)
        opportunities.append(item)
    
    # Also check vs competitor prices
    cursor.execute("""
        SELECT 
            i.sku,
            i.name,
            i.category,
            cb.unit_cost as our_cost,
            AVG(cp.price) as market_avg_price,
            MIN(cp.price) as market_min_price
        FROM items i
        JOIN cost_basis cb ON i.sku = cb.sku
        JOIN competitor_prices cp ON i.sku = cp.sku
        GROUP BY i.sku
        HAVING our_cost > market_avg_price
    """)
    
    market_insights = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    # Sort by savings potential
    opportunities.sort(key=lambda x: x['potential_savings_pct'], reverse=True)
    
    total_potential_savings = sum(o['savings_per_unit'] for o in opportunities)
    
    return {
        "vendor_opportunities": opportunities,
        "market_insights": market_insights,
        "summary": {
            "items_with_savings": len(opportunities),
            "threshold_used_pct": threshold_pct,
            "potential_savings_per_unit_total": round(total_potential_savings, 2)
        }
    }


def get_price_trends(sku: Optional[str] = None) -> dict[str, Any]:
    """
    Get price trends from purchase history.

    Args:
        sku: Filter by specific SKU (optional)

    Returns:
        Dict with price trend data
    """
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    if sku:
        cursor.execute("""
            SELECT 
                ph.item_sku,
                i.name,
                ph.order_date,
                ph.vendor_id,
                v.name as vendor_name,
                ph.unit_price,
                ph.quantity
            FROM purchase_history ph
            JOIN items i ON ph.item_sku = i.sku
            JOIN vendors v ON ph.vendor_id = v.vendor_id
            WHERE ph.item_sku = ?
            ORDER BY ph.order_date
        """, (sku,))
    else:
        # Get top items by purchase frequency
        cursor.execute("""
            SELECT 
                ph.item_sku,
                i.name,
                COUNT(*) as purchase_count,
                AVG(ph.unit_price) as avg_price,
                MIN(ph.unit_price) as min_price,
                MAX(ph.unit_price) as max_price,
                (MAX(ph.unit_price) - MIN(ph.unit_price)) / AVG(ph.unit_price) * 100 as price_variance_pct
            FROM purchase_history ph
            JOIN items i ON ph.item_sku = i.sku
            GROUP BY ph.item_sku
            HAVING purchase_count >= 2
            ORDER BY purchase_count DESC
        """)
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    if sku:
        # Calculate trend for specific item
        if len(results) >= 2:
            first_price = results[0]['unit_price']
            last_price = results[-1]['unit_price']
            trend_pct = ((last_price - first_price) / first_price) * 100
            trend = "increasing" if trend_pct > 2 else "decreasing" if trend_pct < -2 else "stable"
        else:
            trend_pct = 0
            trend = "insufficient data"
        
        return {
            "sku": sku,
            "purchases": results,
            "trend": trend,
            "trend_pct": round(trend_pct, 1) if results else None
        }
    else:
        return {
            "items_analyzed": len(results),
            "price_trends": results
        }


# =============================================================================
# TOOL REGISTRY (for OpenAI function calling)
# =============================================================================

TOOL_FUNCTIONS = {
    "search_items": search_items,
    "get_catalog_summary": get_catalog_summary,
    "create_rfq": create_rfq,
    "get_quotes": get_quotes,
    "compare_quotes": compare_quotes,
    "recommend_award": recommend_award,
    "draft_supplier_email": draft_supplier_email,
    "get_cost_basis": get_cost_basis,
    "get_competitor_prices": get_competitor_prices,
    "recommend_sell_price": recommend_sell_price,
    "explain_price": explain_price,
    # Analytics tools
    "get_spending_summary": get_spending_summary,
    "get_vendor_performance": get_vendor_performance,
    "get_margin_analysis": get_margin_analysis,
    "find_savings_opportunities": find_savings_opportunities,
    "get_price_trends": get_price_trends,
}

TOOL_REGISTRY = [
    {
        "type": "function",
        "function": {
            "name": "search_items",
            "description": "Search for items/SKUs matching a query. Use this to find items before creating an RFQ.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (matches item name, category, or description)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_rfq",
            "description": "Create a request for quotation (RFQ) for an item. Returns an RFQ ID to use for getting quotes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_sku": {
                        "type": "string",
                        "description": "SKU of the item to quote",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity needed",
                    },
                    "region": {
                        "type": "string",
                        "description": "Delivery region (e.g., 'US-West', 'US-East', 'EU', 'APAC')",
                    },
                    "constraints": {
                        "type": "string",
                        "description": "Additional constraints like 'delivery within 3 weeks' or 'prefer reliable vendors'",
                    },
                },
                "required": ["item_sku", "quantity", "region"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_quotes",
            "description": "Get vendor quotes for an RFQ. Simulates vendor responses with pricing, lead times, and risk flags.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfq_id": {
                        "type": "string",
                        "description": "The RFQ identifier",
                    },
                },
                "required": ["rfq_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compare_quotes",
            "description": "Compare and rank quotes for an RFQ. Returns sorted quotes with analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfq_id": {
                        "type": "string",
                        "description": "The RFQ identifier",
                    },
                },
                "required": ["rfq_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_award",
            "description": "Get an award recommendation for an RFQ based on strategy (lowest_cost, fastest, or balanced).",
            "parameters": {
                "type": "object",
                "properties": {
                    "rfq_id": {
                        "type": "string",
                        "description": "The RFQ identifier",
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["lowest_cost", "fastest", "balanced"],
                        "description": "Award strategy: 'lowest_cost', 'fastest', or 'balanced' (default)",
                        "default": "balanced",
                    },
                },
                "required": ["rfq_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_supplier_email",
            "description": "Draft a negotiation email to a supplier asking for better terms.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {
                        "type": "string",
                        "description": "The vendor ID to email",
                    },
                    "rfq_id": {
                        "type": "string",
                        "description": "The associated RFQ ID",
                    },
                    "ask": {
                        "type": "string",
                        "enum": ["better_price", "faster_delivery", "both"],
                        "description": "Type of ask: 'better_price', 'faster_delivery', or 'both'",
                        "default": "better_price",
                    },
                },
                "required": ["vendor_id", "rfq_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_cost_basis",
            "description": "Get the cost basis (last purchase cost or should-cost) for a SKU.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "The SKU identifier",
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Quantity (may affect cost for volume)",
                        "default": 1,
                    },
                },
                "required": ["sku"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_competitor_prices",
            "description": "Get competitor price anchors for a SKU.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "The SKU identifier",
                    },
                },
                "required": ["sku"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recommend_sell_price",
            "description": "Calculate and recommend a sell price based on cost, margin, competitors, and demand.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "The SKU identifier",
                    },
                    "cost": {
                        "type": "number",
                        "description": "Unit cost basis",
                    },
                    "target_margin": {
                        "type": "number",
                        "description": "Target margin percentage (e.g., 35 for 35%)",
                    },
                    "demand_notes": {
                        "type": "string",
                        "description": "Demand signal like 'high demand' or 'slow-moving'",
                    },
                    "competitor_prices": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of competitor prices for anchoring",
                    },
                },
                "required": ["sku", "cost", "target_margin"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_price",
            "description": "Generate a bullet-point rationale for a recommended price.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "The SKU identifier",
                    },
                    "recommended_price": {
                        "type": "number",
                        "description": "The recommended sell price",
                    },
                    "inputs": {
                        "type": "object",
                        "description": "Dict with cost, target_margin, actual_margin, competitor_avg, demand_notes",
                        "properties": {
                            "cost": {"type": "number"},
                            "target_margin": {"type": "number"},
                            "actual_margin": {"type": "number"},
                            "competitor_avg": {"type": "number"},
                            "demand_notes": {"type": "string"},
                        },
                    },
                },
                "required": ["sku", "recommended_price", "inputs"],
            },
        },
    },
    # Analytics / Insights Tools
    {
        "type": "function",
        "function": {
            "name": "get_spending_summary",
            "description": "Get spending summary by category and/or vendor. Shows total spend, order counts, and breakdowns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category: Raw Materials, MRO, Packaging, Safety, or Office",
                    },
                    "vendor_id": {
                        "type": "string",
                        "description": "Filter by vendor ID",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_vendor_performance",
            "description": "Get vendor performance rankings based on historical purchases. Shows on-time delivery, ratings, and spend.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_margin_analysis",
            "description": "Analyze margins across items comparing cost basis vs competitor prices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category (optional)",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_savings_opportunities",
            "description": "Find items where we may be overpaying compared to market or other vendors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "threshold_pct": {
                        "type": "number",
                        "description": "Minimum percentage above market to flag (default 10%)",
                        "default": 10.0,
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_price_trends",
            "description": "Get price trends from purchase history for an item or across all items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sku": {
                        "type": "string",
                        "description": "Filter by specific SKU (optional, shows trends for all if omitted)",
                    },
                },
                "required": [],
            },
        },
    },
]


def execute_tool(tool_name: str, arguments: dict) -> dict[str, Any]:
    """
    Execute a tool by name with given arguments.

    Args:
        tool_name: Name of the tool to execute
        arguments: Dict of arguments to pass

    Returns:
        Tool result as a dict
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool: {tool_name}"}

    try:
        result = TOOL_FUNCTIONS[tool_name](**arguments)
        return result
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}

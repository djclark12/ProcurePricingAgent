"""
Pydantic schemas for tool inputs and outputs.
"""

from typing import Optional
from pydantic import BaseModel, Field


# --- Item/SKU Schemas ---

class Item(BaseModel):
    """An item/SKU in the catalog."""
    sku: str = Field(description="Unique SKU identifier")
    name: str = Field(description="Item name")
    category: str = Field(description="Product category")
    description: str = Field(description="Item description")


class ItemSearchResult(BaseModel):
    """Result of an item search."""
    items: list[Item]
    total_count: int


# --- Vendor Schemas ---

class Vendor(BaseModel):
    """A vendor/supplier."""
    vendor_id: str = Field(description="Unique vendor identifier")
    name: str = Field(description="Vendor name")
    region: str = Field(description="Vendor region")
    rating: float = Field(description="Vendor rating (1-5)")
    reliability_score: float = Field(description="Reliability score (0-100)")
    typical_lead_time_days: int = Field(description="Typical lead time in days")


# --- RFQ Schemas ---

class RFQInput(BaseModel):
    """Input for creating an RFQ."""
    item_sku: str = Field(description="SKU of the item to quote")
    quantity: int = Field(description="Quantity needed")
    region: str = Field(description="Delivery region")
    constraints: Optional[str] = Field(default=None, description="Additional constraints")


class RFQ(BaseModel):
    """A request for quotation."""
    rfq_id: str = Field(description="Unique RFQ identifier")
    item_sku: str = Field(description="SKU of the item")
    item_name: str = Field(description="Name of the item")
    quantity: int = Field(description="Quantity requested")
    region: str = Field(description="Delivery region")
    constraints: Optional[str] = Field(default=None)
    status: str = Field(default="open")


# --- Quote Schemas ---

class VendorQuote(BaseModel):
    """A quote from a vendor."""
    quote_id: str = Field(description="Unique quote identifier")
    rfq_id: str = Field(description="Associated RFQ ID")
    vendor_id: str = Field(description="Vendor ID")
    vendor_name: str = Field(description="Vendor name")
    unit_price: float = Field(description="Price per unit")
    total_price: float = Field(description="Total price")
    lead_time_days: int = Field(description="Lead time in days")
    moq: int = Field(description="Minimum order quantity")
    currency: str = Field(default="USD")
    volume_discount_applied: bool = Field(default=False)
    rush_surcharge_applied: bool = Field(default=False)
    risk_flags: list[str] = Field(default_factory=list)


class QuoteComparison(BaseModel):
    """Comparison of quotes for an RFQ."""
    rfq_id: str
    quotes: list[VendorQuote]
    lowest_cost_quote: Optional[str] = None
    fastest_quote: Optional[str] = None
    recommended_quote: Optional[str] = None
    comparison_notes: list[str] = Field(default_factory=list)


# --- Award Schemas ---

class AwardRecommendation(BaseModel):
    """Award recommendation for an RFQ."""
    rfq_id: str
    recommended_vendor_id: str
    recommended_vendor_name: str
    strategy: str = Field(description="Strategy used: lowest_cost, fastest, balanced")
    reasoning: list[str] = Field(description="Bullet points explaining the recommendation")
    quote_details: VendorQuote
    alternatives: list[dict] = Field(default_factory=list)


# --- Email Schemas ---

class SupplierEmail(BaseModel):
    """A drafted supplier email."""
    vendor_id: str
    vendor_name: str
    subject: str
    body: str
    rfq_id: str
    ask_type: str = Field(description="Type of ask: better_price, faster_delivery, both")


# --- Pricing Schemas ---

class CostBasis(BaseModel):
    """Cost basis for an SKU."""
    sku: str
    item_name: str
    unit_cost: float
    cost_type: str = Field(description="Type: last_purchase, should_cost, average")
    currency: str = Field(default="USD")
    last_updated: str


class CompetitorPrice(BaseModel):
    """A competitor price anchor."""
    sku: str
    competitor_name: str
    price: float
    currency: str = Field(default="USD")
    source: str = Field(description="Where this price was observed")
    observed_date: str


class PriceRecommendation(BaseModel):
    """A recommended sell price."""
    sku: str
    item_name: str
    recommended_price: float
    currency: str = Field(default="USD")
    cost_basis: float
    target_margin_pct: float
    actual_margin_pct: float
    competitor_avg: Optional[float] = None
    demand_signal: Optional[str] = None
    rationale: list[str] = Field(description="Bullet points explaining the price")


# --- Tool Call Logging ---

class ToolCall(BaseModel):
    """A logged tool call."""
    tool_name: str
    arguments: dict
    result_summary: str
    success: bool = True

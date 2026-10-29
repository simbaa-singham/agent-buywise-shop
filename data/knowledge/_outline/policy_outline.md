# Policy outline (approved 2026-10-28)

Source of truth for all written knowledge documents (ADR-033, ADR-039). Documents are produced in the formats listed in agent/docs/rag.md section 3a. Items marked [RAG test] are deliberate retrieval challenges.

## 1. Shipping and delivery
| Rule | Value |
|---|---|
| Ship to | US only: 48 contiguous states; Alaska and Hawaii with longer times [RAG test: region rule] |
| Standard | 3-5 business days; free over $50, else $5.99 |
| Express | 1-2 business days, $14.99 |
| Same-day | Metro areas within 20 miles of a store, ordered by 12 pm local time; $9.99 |
| Alaska / Hawaii | Standard 5-8 days, Express 2-4 days, no same-day |
| Signature required | Orders over $500 |
| PO boxes | Not allowed for orders over $1,000 |
| Missed delivery | 3 attempts, then held at carrier 5 days, then returned and order cancelled |
| Tracking | Tracking number provided when shipped |

[RAG test: versioned policy] Shipping policy v1 (effective 2026-01-01): free shipping over $50. v2 (effective 2026-11-15): free shipping over $75. The assistant must use the version in force on the current date.

## 2. In-store pickup
| Rule | Value |
|---|---|
| Cost | Free |
| Ready time | Within 2 hours if in stock at that store; 2-4 days if transferred |
| Hold period | 7 days, then cancelled and payment authorization released |
| Who can collect | Person on the order with photo ID, or one alternate named at checkout |
| Pickup hours | Store hours, until 30 minutes before closing |

## 3. Orders
| Rule | Value |
|---|---|
| Change / cancel | Allowed while status is Placed (about 30 minutes); after Processing -> staff handoff |
| Quantity limit | Max 2 of the same phone model per order; other categories max 5 [RAG test: category exception] |
| Statuses | Placed -> Processing -> Shipped -> Out for delivery -> Delivered; or Ready for pickup -> Picked up; plus Delayed, Cancelled (one-line meaning each) |

## 4. Payment (mock)
| Rule | Value |
|---|---|
| Methods | Credit/debit card and digital wallets via secure payment link |
| Payment link | Expires in 30 minutes; a new link can be requested |
| Charging | Authorized at order; charged at shipment or pickup |
| Sales tax | Based on delivery state, or the store's state for pickup [RAG test: conditional rule] |
| Not offered (v1) | Financing, gift cards, split payments |

## 5. Pricing
| Rule | Value |
|---|---|
| Price changes | Prices may change; price at time of order is honored |
| Price matching | Not offered |
| Source of prices | Live catalog only, never documents (NFR 8) |

## 6. Warranty
| Rule | Value |
|---|---|
| Coverage | Manufacturer's 1-year limited warranty from delivery/pickup date |
| Covered | Defects in materials and workmanship; not accidental damage, liquid damage or cosmetic wear |
| Claims | Staff help start a claim (handoff); the assistant explains coverage only |

## 7. Returns, exchanges, refunds, trade-ins
Not handled by the assistant in v1 (out of scope). A short policy states this so retrieval answers correctly and the agent offers staff handoff. [RAG test: out-of-scope routing backed by a document]

## 8. Accounts and privacy
| Rule | Value |
|---|---|
| Guest checkout | Allowed; guests check order status with a one-time code sent to the order's email or phone |
| One-time codes | Valid 10 minutes; 3 attempts; then 15-minute lockout |
| Retention | Chat transcripts 90 days; orders 7 years |
| Privacy rights | Data export or account deletion on request via support |

## 9. Store information
| Rule | Value |
|---|---|
| Stores | 10 fictional stores in different US states |
| Hours | Mon-Sat 10 am-9 pm; Sun 11 am-6 pm |
| Holiday hours | Separate dated notice, e.g. Thanksgiving closed; Black Friday 8 am-10 pm [RAG test: time-bound document] |

## 10. Support
| Rule | Value |
|---|---|
| Live staff hours | 8 am-10 pm Eastern Time, daily |
| Outside hours | Ticket created; staff respond next day (the assistant says so on handoff) |

# User Guide

## Core Concepts

- **House** — the move you're managing. An admin creates it and assigns members.
- **Box** (container) — a physical moving box. Has a code (e.g. `A-001`), optional dimensions, and a QR code.
- **Item** — an object inside a box. Identified by AI from a photo.
- **Location** — where a box currently is (e.g. "Living room", "Bedroom").
- **Destination** — where a box is going (e.g. "New apartment", "Storage").
- **Transfer** — a vehicle trip from origin to destination.

---

## Workflow

### 1. Setup (Admin)

1. Log in as admin
2. **Admin → Houses** — create a house, set code prefix (e.g. "A" → boxes are `A-001`, `A-002`)
3. Add locations (where boxes will come from) and destinations (where they go)
4. **Admin → Users** — create accounts for family/helpers
5. Assign users to the house

### 2. Create Boxes

1. **Boxes → New Box**
2. Enter dimensions (optional but useful for transfer planning)
3. Assign a destination (optional — can set later)
4. Take a photo of the empty box (optional)
5. The box gets a unique code and QR code — print it with **Print** button

### 3. Add Items to a Box

**Fast capture** (recommended):

1. Open a box
2. Tap **Add Item**
3. Select hint type (usually Auto)
4. Take a photo of the item
5. Submit — AI processes in background, you can immediately capture the next item

**Review inbox** (when AI is done):

1. Tap **📥** in the navigation bar
2. Review AI-generated descriptions — edit if needed
3. Tap **Confirm** or **Confirm All**

### 4. Close and Seal Boxes

- **Close** — box is packed, no more items. Can still open if needed.
- **Seal** — box is taped and ready to move. Cannot be reopened (final state).

If there are unreviewed items, the close button shows a warning. Use **Close anyway** to auto-confirm all drafts.

### 5. Plan Transfers

1. **Transfers → Plan Trip**
2. Select destination
3. Enter vehicle volume in liters (e.g. van = 8000L)
4. Click **Calculate** — the FFD algorithm groups boxes into vehicle loads
5. Create each suggested transfer
6. When loading the vehicle, tap **Start Transfer** → boxes become "In Transit"
7. On arrival, tap **Complete Transfer** → boxes become "Delivered"

### 6. Find Things

- **Search** (Ctrl+K or search icon) — search any item or box by name
- **QR Scanner** — scan a box's QR code to jump directly to it
- **Dashboard** — overview of boxes by status, upcoming transfers

---

## Box Status Flow

```
open → closed → sealed
         ↓
     in_transit → delivered
```

- `open` — being filled
- `closed` — packed, ready to move
- `sealed` — taped shut
- `in_transit` — on the vehicle during a transfer
- `delivered` — arrived at destination

---

## QR Codes

Every box has a QR code that links to its detail page. To use:

- Print from the box detail page (**QR Code → Download**)
- Or use the print page: `/print/{houseId}/container/{code}`
- Scan with the in-app scanner or any QR scanner app

---

## Tips

- **Batch capture** — for a box of books, photograph each spine quickly. AI handles the queue.
- **Nesting** — small boxes can be placed inside larger ones. Set "Parent box" when creating.
- **Categories** — AI assigns categories automatically. Useful for filtering items later.
- **Retry AI** — if AI misidentified an item, use **Retry** to re-analyze.

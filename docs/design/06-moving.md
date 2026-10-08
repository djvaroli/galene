# Moving plans and estimates

A moving plan combines the owner's current decisions, a complete inventory snapshot, and visible assumptions. AI can explain tradeoffs and suggest organization. A deterministic estimator calculates all quantities and time ranges, making the result repeatable and editable.

## Information needed

| Input | Use and missing-value behavior |
| --- | --- |
| Move date and available days | Schedule tasks relative to the deadline; omit dates when unknown |
| Keep/sell/donate/discard decisions | Group actions; undecided items remain in the conservative transport scenario |
| Packing classes and group quantities | Estimate boxes and bulky handling units; surface unknowns |
| Actual boxes and their contents | Count each assigned box once; do not also estimate boxes for those contents |
| Fragile, essential, disassembly flags | Packing order, extra handling, last-day checklist |
| Packing helpers and moving crew | Convert labor effort into elapsed work time; both include the owner |
| Floors, elevator access, carry distance | Choose an explicit handling multiplier; initial default 1.0 when confirmed easy access |
| Trips and one-way travel minutes | Compute vehicle travel time; required for a full move-day total |
| Setup, breaks, cleanup and contingency | Show explicit allowances that the owner can adjust |
| Selling and donation preferences | Recommend task order and owner-entered lead times |

Unknown access or travel information yields a partial estimate with named missing inputs. The app can still report packing effort. It must not silently treat unknown travel, stairs, or item quantity as zero.

The baseline includes all active items even when sell/donate/discard is intended, because those objects still occupy the home. An alternate “after planned removals” scenario excludes those decisions and clearly assumes they are completed before moving day. Items with an actual sold/donated/discarded lifecycle are excluded from both. This avoids underestimating the move when a sale falls through.

## Inventory into packing work

Use labeled boxes as the strongest evidence available. Unassigned boxable items contribute box equivalents from a small editable category table; sum equivalents before rounding up to whole boxes. Suggested seed factors might be 0.04 boxes per book, 0.05 per clothing item, and 0.10 per small kitchen item. These are prototype planning assumptions to calibrate with real packing, not validated capacity measurements.

An owner-provided `packing_box_override` for a group replaces quantity-based estimation for that group. Unknown quantity without an override appears in an unresolved list and prevents a complete total; a partial total is still useful. Bulky items use confirmed `handling_units`, defaulting to exact item quantity only when it represents separately handled objects. Unknown packing classes need classification before a complete estimate.

Allocate each item to one calculation path: an assigned box, estimated unassigned boxable contents, or bulky handling. Do not count a desk's drawers or the contents of a saved box twice. Marking a box packed reduces remaining packing effort but leaves its transport effort in place. The plan reports remaining work, with already completed work separately counted.

## Time model

Use ranges for planning coefficients. Store all coefficients and an `estimator_version` on the plan so a later software change does not rewrite an older estimate. Initial seed coefficients are assumptions for trial use:

| Component | Initial range |
| --- | --- |
| Packing a standard box | 8–15 person-minutes |
| Extra wrapping per fragile box | 3–8 person-minutes |
| Preparing a bulky handling unit | 5–12 person-minutes |
| Disassembly per marked item | 15–30 person-minutes |
| Loading and unloading one box combined | 4–8 person-minutes |
| Loading and unloading one bulky unit combined | 12–24 person-minutes |
| Setup and cleanup | 30–60 elapsed minutes, editable |
| Contingency | 20% of working and travel time, editable |

Set an explicit access multiplier, initially 1.0 for easy elevator or ground-floor access, 1.25 for moderate inconvenience, and 1.5 for difficult stairs or long carries. These are adjustable rough assumptions, not an ergonomic or mover quotation model. Flag heavy items requiring two people; do not imply that more time makes a one-person lift feasible.

For each low/high bound, compute:

```text
packing_person_minutes =
    standard_unpacked_boxes * pack_rate
  + fragile_unpacked_boxes * extra_wrapping_rate
  + bulky_units_needing_preparation * preparation_rate
  + items_needing_disassembly * disassembly_rate

handling_person_minutes =
    (transport_boxes * box_handling_rate
     + bulky_transport_units * bulky_handling_rate) * access_multiplier

effective_crew(n) = 1 + 0.7 * (n - 1)   # n in [1, 4], editable efficiency
packing_elapsed = packing_person_minutes / effective_crew(packing_helpers)
handling_elapsed = handling_person_minutes / effective_crew(moving_crew)
travel_elapsed = (2 * trips - 1) * one_way_travel_minutes
move_day_elapsed =
    (handling_elapsed + travel_elapsed + setup_and_cleanup) * (1 + contingency)
packing_elapsed_with_buffer = packing_elapsed * (1 + contingency)
```

The travel formula assumes one vehicle, repeated trips between two apartments, a final arrival at the destination, and no separate vehicle-return journey. Add an explicit extra travel allowance for a rental return. Trips are user-entered; do not infer vehicle fit from photos. Multi-vehicle routing and exact scheduling are deferred.

Display packing and move-day time separately. If packing occurs that day, offer the sum and state that the two phases are assumed sequential. Person-hours describe work effort; travel and waiting are elapsed time. Selling and donation lead time is calendar time entered by the owner, never divided by crew size.

## Worked example

Assume 20 unfilled standard boxes, six bulky units needing preparation, no extra fragile/disassembly work, easy access, one packing person, and a moving crew of two. One load is carried to the destination, a 30-minute drive, with no return journey. Use the seed coefficients and a 20% contingency.

| Calculation | Result |
| --- | --- |
| Packing labor | `20 × (8–15) + 6 × (5–12)` = 190–372 person-minutes, or 3.2–6.2 person-hours |
| Packing elapsed including contingency | 228–446.4 minutes, about 3.8–7.4 hours |
| Handling labor | `20 × (4–8) + 6 × (12–24)` = 152–304 person-minutes |
| Effective two-person crew | `1 + 0.7 × 1` = 1.7 |
| Handling elapsed | 89.4–178.8 minutes |
| Move day with travel, setup/cleanup and contingency | `(89.4–178.8 + 30 + 30–60) × 1.2` = 179.3–322.6 minutes, about 3.0–5.4 hours |

The UI should round each endpoint up to useful planning increments, for example 4–7.5 hours packing and 3–5.5 hours moving using half-hour increments. Keep the unrounded values in the detail view. State that all 20 boxes remain to be packed and all six bulky units need preparation. Actual observed packing times can later replace the seed rates.

## Plan contents

A saved plan contains the complete input snapshot, unresolved coverage/quantity questions, lists for each disposition, proposed packing groups, essential and fragile checklists, assumptions, arithmetic breakdown, and optional AI commentary. Every item reference resolves to a snapshot entry, even if the live item is later deleted. Label historical references clearly.

Generate standard tasks in code: review undecided items, confirm access and vehicle trips, obtain boxes, arrange intended removals, pack nonessentials, prepare furniture, pack essentials last, load, unload, and check rooms. Task completion is derived from inventory/box state where possible. A short move-level checklist JSON can store completion of manual tasks such as booking help; no general project-management system is needed.

AI may recommend sequencing and explain which information would most improve the estimate. It cannot invent local disposal rules, buyer demand, current prices, or availability of movers. Do not add web browsing to this prototype.

Changing inventory or move settings makes a plan stale. Regeneration creates a new version; do not overwrite the old snapshot. Applying AI suggestions edits owner decisions and therefore also makes the prior plan stale.

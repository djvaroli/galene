# Product and user experience

Galene helps its owner answer three recurring questions: what do I own, where is it, and what will it take to move it? The first release must support the complete path from room capture to a reviewed inventory and a usable moving checklist.

## First usable release

| Capability | Included behavior |
| --- | --- |
| Private access | One administrator-provisioned Firebase account; sign in and sign out; no registration |
| Inventory | Create rooms; add, edit, search, filter, and remove items manually |
| Photo capture | Select a room, upload several photos, inspect processing progress, request item suggestions |
| Review | Correct labels and quantities, group small objects, discard false detections, resolve duplicates, save selected suggestions |
| Organization | Record shelf or cupboard notes, create labeled boxes, assign items, mark essentials and fragile items |
| Moving decisions | Keep, sell, donate, discard, or undecided; record actual completion separately |
| Moving plan | Checklist, packing groups, unresolved decisions, editable time assumptions and estimated ranges |
| AI assistance | Ask questions about saved inventory; request explained disposition suggestions; explicitly apply selected suggestions |

Manual inventory works when the AI provider is unavailable. Existing inventory remains readable and editable while a scan runs.

## Capture and review journey

1. Create a room such as Bedroom and note subareas such as wardrobe, desk, and under bed.
2. Take an overview and a few close-ups. The capture screen explains that drawers and closed cupboards need separate inspection.
3. Upload up to ten photos in one scan. Individual upload failures can be retried without repeating successful uploads.
4. After photos are prepared, select **Analyze photos**. The app shows queued, processing, and ready states; leaving the page does not lose progress.
5. Review draft cards beside the source photos. Each card has a label, quantity or unknown quantity, observation notes, and possible matches to existing inventory.
6. Choose create item, attach evidence to an existing item, or dismiss. Editing a suggestion changes the draft; saving is explicit. A batch may save only selected cards.
7. Add anything missed manually. Mark the room as reviewed only when satisfied, with remaining gaps recorded in notes.

Repeated pictures of one chair should suggest one object, but the owner makes the final identity decision. A shelf of books may be one group with an approximate quantity. A laptop or piece of furniture should normally be a separate item. The product does not promise an exact count of every visible object. Vision models have counting and recognition limitations. [OpenAI vision documentation](https://developers.openai.com/api/docs/guides/images-vision)

## Screens

| Screen | Main content and actions |
| --- | --- |
| Home | Rooms, inventory counts, scans awaiting review, active move |
| Room | Inventory, coverage notes, last reviewed date, add manually, scan room |
| Capture | Photo selection, thumbnails, preparation errors, Analyze photos |
| Scan review | Source image and suggestion cards; edit, match existing, save selected, dismiss |
| Item | Name, quantity, room and location note, photos, disposition, packing fields, owner notes |
| Move | Constraints, decision lists, packing checklist, estimate breakdown, stale-plan notice |
| Boxes | Label, destination room, contents, packed or unpacked state |
| Ask | Question, selected scope, answer with linked items, missing information |
| Settings | Display name, units, AI availability and usage, sign out |

Use responsive layouts designed for a phone camera workflow and desktop review. Provide visible labels, keyboard access, adequate tap targets, and textual status indicators. Use a file picker with camera capture as a browser hint; do not require a custom live camera interface. Keep server state in the query cache and unsaved form edits in component state.

Search includes item names and notes. Filters cover room, disposition, essentials, fragile, and packing state. The item list shows both entry count and known physical quantities; ten grouped entries do not imply ten physical objects.

## Moving journey

The owner supplies the move date, available help, access constraints, approximate travel time, and desired outcome. The app shows a complete list of active belongings, grouped by the owner's decisions. AI suggests decisions with short reasons and asks for missing information such as recent use or sentimental value. A photo alone cannot establish whether something should be discarded.

The owner accepts or edits suggestions, assigns belongings to boxes, and reviews the estimate. Keeping an item separate until the last day is an **essential** flag. A proposed donation stays in the inventory until the owner marks it donated. Unresolved items remain visible and count conservatively toward the move.

Packing and moving are separate stages. The plan shows labor hours, elapsed time with the entered crew, and calendar lead time for selling or arranging collections. It exposes assumptions instead of presenting a precise completion date without evidence.

## Product acceptance criteria

- From a phone, upload a small room scan, correct its suggestions, save selected items, and find them after signing out and back in.
- Rescan an existing object and attach the new evidence without creating a second inventory entry.
- Manually add an unseen object and find it through search.
- Ask where a saved object is; the answer links to its record and does not invent its location.
- Request a moving plan; it includes every active item or group, explicitly identifies undecided items, and explains the time range.
- Change a relevant item or moving constraint; the old plan is visibly stale until regenerated.
- Mark an item donated; it is excluded from future transport estimates but remains in history.
- Recreate the application containers; confirmed inventory and saved media remain available.

For an early usability trial, choose two rooms and hand-label the visible large items and useful small-item groups. Aim to suggest at least 80% of those reference entries and make correction faster than manual entry. These are trial targets, not promised model accuracy; record omissions and false positives before expanding scope.

## Follow-up priorities

1. Short video clips converted into selected still frames, using the same review flow.
2. Printable box labels and QR links to contents; no public access through the QR code.
3. JSON or CSV inventory export and an actual backup and restore workflow.
4. Better rescan matching, reminders, and move templates informed by recorded actual time.

Defer native mobile apps, offline synchronization, floor plans, automatic dimensions or weights, resale price scraping, marketplace posting, mover booking, multiple users, and autonomous actions. These add scope without proving the core capture-to-move workflow.

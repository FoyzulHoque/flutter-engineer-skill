# UX Copy: Minimal and Meaningful

Act as a UX copywriter for every string a user will see. The goal is the fewest words that let someone act with confidence. If a word doesn't help the user decide or act, cut it.

## The test for every string

1. **Is it necessary?** Would the user be confused or stuck without it? If not, delete it. The best copy is often none: a clear icon + layout, or a self-explaining button.
2. **Is it specific?** It should name the thing and the action ("Save address", not "Submit"; "Order #1042 is ready", not "Update available").
3. **Is it short?** Cut filler, then cut again. Front-load the key word.
4. **Is it human?** Plain words, no jargon, no system internals, no blame.

## Rules

- **Buttons are verbs plus an object:** "Place order", "Add card", "Clock in". Never "OK", "Submit" or "Yes" when a specific verb fits. Dialog buttons repeat the action: "Delete card" / "Cancel".
- **Titles name the place or the thing** in 1–3 words: "Orders", "Payment", "Shift details". Drop "My", "Your" and "Page" unless they disambiguate.
- **One message per screen.** Don't repeat the title in the subtitle or explain what the UI already shows.
- **Labels over placeholders.** Placeholders vanish while typing. Use them only for format hints ("04xx xxx xxx").
- **Sentence case** everywhere except proper nouns. No Title Case Buttons. No ALL CAPS except tiny overlines if the design uses them.
- **Numbers and data beat words:** "3 items · $18.50" rather than "You have 3 items in your cart totalling $18.50".
- **Cut these:** "Please", "Successfully", "Simply", "Just", "In order to", "Click here", "Welcome back! 👋", "Oops!", "Something went wrong" (alone), exclamation marks, and emoji in UI text unless the brand uses them.
- **No unnecessary confirmations.** Prefer undo ("Removed · Undo") over "Are you sure?". Confirm only destructive or costly actions, and say the consequence.
- **Consistent vocabulary.** One word per concept across the app ("store" or "branch", never both). Match the backend/business terms the users actually use. Put the glossary in the project notes.

## Patterns

| Situation | Write | Not |
|---|---|---|
| Error | What happened + how to fix: "No connection. Check your signal and try again." | "Error 503" / "Oops! Something went wrong!" |
| Field validation | The rule, at the field: "Use at least 8 characters" | "Invalid password" |
| Empty state | Why it's empty + next action: "No orders yet" + **Browse menu** | "No data found" |
| Success | Usually nothing, or a brief state change: "Saved" | "Your changes have been saved successfully!" |
| Loading | Skeleton, no text; for long waits say what's happening: "Confirming payment…" | "Loading, please wait…" |
| Destructive confirm | Title: "Delete account?" Body: the consequence in one line. Button: "Delete account" | "Are you sure?" / "Yes" |
| Permission ask (pre-prompt and `Info.plist`) | The user benefit: "Show stores near you" | "This app needs location access" |
| Notification | The fact first, ≤ 1 line: "Your chai is ready at Parramatta" | "Hey! 👋 We have an update about your order" |
| Offline banner | "Offline. Showing saved data." | "You are currently not connected to the internet" |

## Process in code

- When building or editing UI, **review every string you add or touch** against the test above, and show the final copy in the report.
- Rewriting existing copy beyond the task is a *recommendation*: list "current → proposed" pairs and wait for approval. Copy can be legal, brand or client-approved.
- Keep strings in the project's existing place (inline, a constants file, or `l10n` ARB files). Don't introduce i18n unasked, but never concatenate translated fragments. Use placeholders/plurals (`{count, plural, …}`) when l10n exists.
- With GetX `Translations` (`'key'.tr`): use stable snake_case keys by meaning (`orders_empty_title`), never English sentences as keys. Otherwise editing the English text silently breaks every other language. Keep one key per string, no emoji in values unless the brand uses them, and split a 2,000-line map into one file per language.
- Leave room for longer languages and large text scales. Never fit copy by shrinking the font.
- Don't put user-facing text in exceptions shown raw. Map errors to copy in one place (e.g. the error mapper in `util/`).

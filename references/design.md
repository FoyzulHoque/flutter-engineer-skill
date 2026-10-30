# App Design: Distinctive, Not Generic

The fastest way to make an app look AI-made is to reach for defaults: indigo/purple gradients, everything 16px-rounded with soft drop shadows, glassmorphism on every card, emoji icons, a centered hero with a gradient blob, three identical feature cards, Inter everywhere, and "Welcome back! 👋". Avoid all of those unless the brand actually calls for them.

This file is about *visual* decisions. Behavior stays in the other references. A restyle must not change flows, copy meaning, or API calls unless the user asks.

## 1. Design comes from a source, never from taste

Before touching UI, find the design source, in this order:
1. **The project's own tokens and theme.** `core/const/app_colors.dart`, `app_theme.dart`, text-style helpers, spacing classes, and shared widgets in `global_widgets/`. If they exist, they are the design system. Use them.
2. **Design docs in the repo** (`docs/`, `*_UI_Plan.md`, `REBRAND_PLAN.md`, briefs, screenshots, PDFs).
3. **The brand's real presence**: the client's website (measure its CSS: colours, fonts, radius, button height), logo files, a live prototype, or Figma.
4. **Ask the user** for the brand source if none exists. Don't invent a palette silently. If asked to propose one, offer 2–3 named *directions* (e.g. "night site office", "flat corporate navy", "warm café") with a screenshot/mock per direction, and let the user choose.

Write the chosen direction down as a doc comment at the top of the colour file. One paragraph says what the look is and why, and gives rules such as "white is the accent" or "status colours always carry a word". Future edits follow that paragraph.

## 2. Tokens by meaning, applied through the theme

**Name colours by role, not by screen or hue:**
```dart
/// Direction: flat corporate. Navy ink on light pages, royal blue for actions.
/// Status colours carry meaning and are always paired with a label.
class AppColors {
  AppColors._();
  // Surfaces: 0 = page, higher = more raised
  static const surface0 = Color(0xFFF8F8F8);
  static const surface1 = Color(0xFFFFFFFF);
  static const surface2 = Color(0xFFF1F2F5);
  static const border   = Color(0xFFDFE3EA);
  // Text
  static const textPrimary   = Color(0xFF16285D);
  static const textSecondary = Color(0xFF62718D);
  static const onAccent      = Color(0xFFFFFFFF);
  // Brand
  static const primary = Color(0xFF16285D);
  static const accent  = Color(0xFF1B48CC);
  // Status
  static const success = Color(0xFF15803D);
  static const warning = Color(0xFFC47A00);
  static const critical = Color(0xFFC8323A);
  static Color tint(Color c) => c.withValues(alpha: 0.12);
}
```
Anti-pattern seen in real apps: `scheduleDetailsPageOverviewColor`, `ladyIconBgColor`, `notecontainertext`. One-off names per screen make a restyle impossible and let the palette drift into 30 near-identical greys. When you meet this, don't rename everything unasked. Map new work onto semantic tokens and propose a consolidation.

**Also tokenise:** spacing (`AppSpacing.xs/sm/md/lg/xl`, plus a `screen` padding), radius (`AppRadius.control/card/sheet`), and type (`displayTextStyle`, `titleTextStyle`, `bodyTextStyle` helpers, with tabular figures for money and times).

**Push tokens into `ThemeData` component themes** (`filledButtonTheme`, `textButtonTheme`, `inputDecorationTheme`, `cardTheme`, `bottomSheetTheme`, `dividerTheme`, `appBarTheme`, `segmentedButtonTheme`, `switchTheme`, `snackBarTheme`, with `useMaterial3: true` and a full `ColorScheme`). Then plain `FilledButton`, `TextField` and `Switch` already look like the product, and screens need no per-call styling. A rebrand becomes "edit `lib/core/`", not "edit 80 screens".

**Never put raw `Color(0x…)`, `TextStyle(fontSize: …)` or magic padding numbers at call sites.** If a value is missing, add a token first.

## 3. What makes an app feel designed

- **A point of view.** One sentence of direction ("night site office", "warm café counter", "calm clinical"). Every choice should be defensible against it.
- **A restrained palette.** Neutrals do most of the work. One accent. Status colours reserved for status and **always paired with a word or icon**, never colour alone (accessibility, and it prevents decoration creep).
- **Type with hierarchy.** At most two families (display + body), chosen from the brand. Few sizes, clear weight steps. Tight tracking only where the brand does it.
- **Consistent geometry.** One radius language: square-ish (2–4px) for corporate, pill for friendly CTAs. Match the brand's website. One elevation model: flat with hairlines, *or* soft shadows, *or* glass. Don't mix all three.
- **Density fit for the user.** Field and worker apps get big tap targets (≥ 48dp), high contrast, readable outdoors, glanceable status, one primary action per screen. Consumer apps can be more editorial.
- **Real content.** Design with realistic data lengths: long names, zero items, 99+ badges, error text. Use the brand's real imagery, never placeholder stock or emoji as icons. Use one icon set consistently.
- **Considered states.** Empty, loading (skeletons shaped like the content, not just a spinner), error with a way out, offline, success. These are where generic apps look generic.
- **Motion with purpose.** Short (150–300ms), eased, used for continuity (sheet in, item added, tab change). Respect reduced-motion. Light haptics on confirmations via one helper.
- **Platform respect.** Safe areas, edge-to-edge with correct status-bar icon brightness (`SystemUiOverlayStyle` per background), back gestures, keyboard insets.

## 4. Working method for UI tasks

1. **Read** the tokens, theme, shared widgets and two sibling screens. Note the direction paragraph.
2. **Compose from shared widgets first** (`CustomButton`, `GlobalTextField`, section headers, sheets). Create a new shared widget only when a pattern repeats on two or more screens.
3. **Match siblings**: header style, screen padding, section spacing, card treatment, how lists and empty states look.
4. **Check at the extremes**: small phone (360dp) and large phone/tablet, text scale 1.3+, dark/light if supported, long localized strings.
5. **Show it.** Run it and take screenshots (emulator/device, or a widget golden). For a restyle, produce **before/after pairs** of the same screens with the same data, so the user judges the change rather than a description of it.
6. **For a rebrand**, write a short plan first, approval-gated: a source-vs-app comparison table (colour, type, radius, depth, buttons, inputs), a token old→new table, and what's retired. Then change `lib/core/` only. Screens should pick it up without being edited one by one.

## 5. What 41 template-built apps got wrong (and the few things they got right)

A design review of 41 production GetX apps cloned from one starter template found the template, not the designers, set the ceiling:

| Pattern (seen in most apps) | Measured | Consequence |
|---|---|---|
| `ThemeData` is one line (`scaffoldBackgroundColor` only) | 39 of 41 apps | Every button, field and card is styled at the call site |
| Raw `Color(0x…)` at call sites | 21–422 per app | No palette discipline; near-duplicate pinks/reds/greys (`0xffFE3C72`/`0xFFFE5196`; `textGrey` = `hintText`) |
| Inline `TextStyle(` | 113–603 per app | Type scale drifts screen by screen |
| Template palette copied, only `primaryColor` swapped | Same file in ~30 apps, the same red in 3 apps, the same pink in 4 | Different clients' apps look identical. Leftover tokens like `whatsAppBackgroundColor` and `tealAcent` in apps with no WhatsApp and no teal |
| Colour names by screen/order/hue: `scheduleDetailsPageOverviewColor`, `thirdColor`/`forthColor`, `backgroundColor2/3/4`, non-const `redcolor` | Most apps | Can't restyle; nobody knows which grey to use |
| Numbered duplicate widgets: `custom_text_field_2…_5`, `custom_button2`, `CustomButton`/`CustomButton2` | Most apps | Fix a bug once, it survives in four copies |
| Font sprawl via GoogleFonts | Up to 7 families; theme says Roboto while the helper says Inter | No typographic voice |
| `fontFamily: 'Poppins'` repeated at call sites | 9–10 places | It belongs in `ThemeData.fontFamily` / `textTheme` |
| Spinner-only loading (`CircularProgressIndicator`/EasyLoading) | 9–43 per app; skeletons in only ~7 apps | Feels slow and generic |
| No error/offline state; snackbars titled "Error" showing raw `$e` | Nearly all | Users see exceptions |
| `SafeArea` missing | 0–4 uses in 100+ file apps (5 apps) | Content under notches and home indicators |
| `.sp` font sizes everywhere (ScreenUtil) | All | Text scaling is controlled by ScreenUtil, not the user. Verify `minTextAdapt` and test at 1.3× system text |
| Stock "AI default" colours: `#6C63FF`/`#6056DD` purple, `#7B61FF // Purple (you can change this)`, `#2563EB` Tailwind blue, Material green `#4CAF50` | Several | Instantly generic |
| `colorSchemeSeed: white`, a dark app built on `ThemeData.light()`, `useMaterial3: false` as the entire theme | Individual apps | Material derives wrong surface/onSurface colours |
| Misspelled shared folders: `global_widegts`, `coustom_dialouge`, `bommotmsheet` | Every clone | Signals unmaintained code. Don't rename unasked, but don't copy them to new projects |
| Copy: "X Successfully!", "Oops", Title Case, emoji in toasts, typos ("Passsword", "pasword") | Everywhere | See `ux-copy.md` |
| Empty state renders `title!` on a hard-coded grey box | The shared template widget | Crashes on null and ignores the theme |

**What was good (reuse the idea, upgrade the execution):**
- A **parameterised empty state** (title, subtitle, CTA), but without fixed 300×300 images.
- **Shimmer skeletons** shaped like the content, but with colours from the theme and no `Expanded` returned from a helper.
- **Small, meaning-named palettes**: a 4-colour teal palette; Tailwind-style neutrals named by role (`textBlack 111827`, `textGrey 6B7280`, `border E5E7EB`).
- A **spacing/radius/button-height token file** (one app). Fold it into the theme.
- Explicit **loading → empty → data** branching on an analytics screen. Enable chart touch tooltips, though.
- Explicit **offline copy** ("No internet connection") on a home screen.

**When you start or restyle an app from this kind of template:** build the theme first (§2), map the template tokens onto semantic names, delete unused template tokens, merge numbered widget copies into one parameterised widget, set `fontFamily`/`textTheme` once, and add skeleton/empty/error/offline widgets to `global_widgets` before building screens. Propose this as a plan with approval. It touches many files.

## 6. Generic-AI tells to catch in review

- [ ] Purple/indigo gradient or gradient text with no brand reason
- [ ] Every surface has a blur, glow or large shadow
- [ ] Uniform 16–24px radius on everything regardless of brand
- [ ] Emoji used as icons or in headings
- [ ] Hardcoded colours/sizes at call sites; duplicated near-identical greys
- [ ] Spinner-only loading; "No data" empty states with no next action
- [ ] Colour as the only signal for status
- [ ] Centered-everything layouts and three identical cards in a row
- [ ] Copy like "Unleash", "Seamless", "Welcome back! 👋"
- [ ] Mixed icon sets, or Material icons beside a brand that uses custom ones

If the project's established direction intentionally uses one of these (e.g. a glass "night" theme), it's a choice, not a tell. Follow the project.

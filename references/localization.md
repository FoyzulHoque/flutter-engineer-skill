# Localization (l10n) and Right-to-Left

Primary source: https://docs.flutter.dev/ui/accessibility-and-internationalization/internationalization. Run `python <skill-dir>/scripts/check_translations.py <project-root>` before touching translations. It reports locale codes, key parity, unused keys and hardcoded strings.

## What we found in real apps (one shared template, five apps)

A `core/localization/localization.dart` with a GetX `Translations` map was copied between projects. Every copy had the same failures:

| Found | Effect |
|---|---|
| Locales out of parity (Arabic missing 137 of 527 keys; 9 languages each missing ~45 auth keys) | Missing keys fall back to English mid-screen. Keys missing from the fallback too render as the **raw key** |
| Keys used in code but defined nowhere (10–37 per app) | Raw key text on screen (`'Deleting...'.tr` → "Deleting...") in every non-English language |
| **Interpolated keys**: `'${package.coinAmount} Coins'.tr`, `'Pilot Name ${index + 1}'.tr` | Can never match a key. Use `trParams` / ARB placeholders |
| Hundreds of unused keys (393 in one app, product catalog words) | Translator cost and noise. Delete them, and translate data on the server, not in the app |
| Keys copied from an unrelated app (`Hire_Me`, `add_category`) and `.tr` used 0 times | A dead file that looks like i18n support but does nothing |
| Inconsistent key casing (`Enter_UserName` vs `enter_Username`) | The lookup misses and the raw key shows |
| English sentences or mixed styles as keys (`"Don't_Have_an_Account?"`) | Editing English breaks every other language |
| Invalid locale code `ar_AR` | There's no such region. Use `ar` or `ar_SA`/`ar_AE` |
| No `flutter_localizations`, no `supportedLocales`/`localizationsDelegates` | Date pickers, dialogs and "Cut/Copy/Paste" stay English, and **Arabic doesn't flip to right-to-left** |
| 96–298 hardcoded `Text('…')` per app next to `.tr` usage | Partially translated screens |
| Language names in the picker written in English ("Arabic") | Speakers look for "العربية" |
| Saved locale read in `main()` *and* in a controller, with different formats (`'fr'` vs `'en_US'`) | The language resets or flips on restart |

**Half-migration seen:** an app had `lib/l10n/app_*.arb` (good camelCase keys, four languages) **and** a GetX map with the same keys, but no `generate: true`, no `l10n.yaml`, and 0 uses of `AppLocalizations.of` against 144 `.tr` calls. The ARB files were dead copies drifting apart. (It did wire `localizationsDelegates` + `supportedLocales` correctly, the part most apps miss.) Pick one system and delete the other. Note that omitting `supportedLocales` defaults to `[Locale('en', 'US')]`, which stops RTL and other Material locales.

**Lesson:** a template copies its bugs into every app. Before reusing a localization file, run the checker and delete what the new app doesn't have.

## Choosing the approach

| Situation | Use |
|---|---|
| New app, or a real multi-language requirement | **Official `gen_l10n`** (ARB files + `flutter_localizations`): type-safe getters, ICU plurals/selects, placeholders, compile-time errors for missing keys |
| Existing GetX app already on `Translations` | Keep it (don't migrate unasked), but harden it with the rules below. Propose a migration only if plurals, RTL or many languages are needed |
| English-only app | No i18n framework. Keep strings in one place so it can be added later |

### Official setup (summary; check the docs for the pinned Flutter version)
```yaml
# pubspec.yaml
dependencies:
  flutter_localizations: { sdk: flutter }
  intl: any
flutter:
  generate: true
# l10n.yaml
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
```
```json
// lib/l10n/app_en.arb
{
  "ordersEmptyTitle": "No orders yet",
  "cartItemCount": "{count, plural, =0{Empty} =1{1 item} other{{count} items}}",
  "@cartItemCount": { "placeholders": { "count": { "type": "int" } } }
}
```
```dart
MaterialApp( // or GetMaterialApp
  localizationsDelegates: AppLocalizations.localizationsDelegates,
  supportedLocales: AppLocalizations.supportedLocales,
);
Text(AppLocalizations.of(context)!.ordersEmptyTitle);
```

### Hardening GetX `Translations`
- **Also add Flutter's delegates** to `GetMaterialApp`: `localizationsDelegates: GlobalMaterialLocalizations.delegates` and `supportedLocales: [...]` matching the map. Without them, RTL and Material widgets don't localize.
- **One file per language** (`en_us.dart`, `ar.dart`), merged in the `Translations` class. Never a 2,000-line single map.
- **Keys:** snake_case by meaning (`login_button`, `orders_empty_title`), never sentences or punctuation. Every locale has exactly the same key set (the checker enforces this).
- **Placeholders:** `'hello_name'.trParams({'name': n})` with `'Hello @name'`, never string concatenation. Plurals: `'item'.trPlural('items', count)`, or move to ARB if the grammar is complex (Arabic has six plural forms).
- **Only offer languages that exist** in the map. Build the picker from the supported list, and show each language name in its own language.
- **Persist the locale in one place** (a `LocaleService`), in one format (`languageCode` or `languageCode_countryCode`). Apply it on startup via `GetMaterialApp(locale:)`, and change it with `Get.updateLocale`.
- `fallbackLocale` must be the most complete locale.

## Right-to-left (Arabic, Hebrew, Urdu, Persian)
- Needs the localization delegates (above) so `Directionality` flips automatically.
- Use direction-aware APIs: `EdgeInsetsDirectional`, `AlignmentDirectional`, `PositionedDirectional`, `TextAlign.start/end`, and `BorderRadiusDirectional`. Never `left`/`right` for layout.
- Directional icons (back arrows, chevrons) must mirror. Material `Icons.arrow_back` adapts, custom SVGs need `matchTextDirection` or a `Transform.flip`.
- Numbers, phone numbers and codes stay LTR inside RTL text. Wrap them in `Directionality(textDirection: TextDirection.ltr)` where needed.
- Fonts: confirm the font supports Arabic glyphs (many Google Fonts don't), and set a fallback.
- Test by forcing the locale and screenshotting key screens in both directions.

## Formatting
- Dates, numbers and currency via `intl` (`DateFormat.yMMMd(locale)`, `NumberFormat.simpleCurrency(locale:)`). Never hand-built month arrays like `"jan": "Jan"` in the translation map.
- Leave 30–40% extra width for German/French. Never shrink fonts to fit.

## Done means
- The checker shows key parity across locales, 0 unused keys, and no hardcoded user-facing `Text('…')` in touched files.
- Each supported locale opened once and screenshotted (including RTL if present).
- Copy reviewed with `ux-copy.md`.

# Payments: In-App Purchases, RevenueCat, Stripe, Google Pay, Apple Pay

Primary sources: https://www.revenuecat.com/docs/welcome/overview, https://docs.stripe.com/, https://developer.apple.com/documentation/ (StoreKit, PassKit/Apple Pay), https://developer.android.com/google/play/billing and https://developers.google.com/pay. SDK APIs and store rules change often. **Read the docs for the pinned package versions before writing payment code.**

**All payment work is approval-gated:** adding SDKs, keys, products, webhooks, price changes, going live. Never handle raw card numbers in app code, never log payment payloads, and never put secret keys (`sk_…`, RevenueCat secret API keys, webhook secrets) in the app. Only publishable/public keys ship in the binary.

## Step 1: pick the right rail (store policy decides, not preference)

| What's being sold | Required / sensible rail |
|---|---|
| Digital content or features used in the app (subscriptions, premium unlocks, coins, courses) | **Store in-app purchase** (Apple StoreKit / Google Play Billing). Use **RevenueCat** or `in_app_purchase` |
| Physical goods, real-world services (food, rides, tickets, deliveries) | **Stripe** (cards, **Apple Pay**, **Google Pay**) or another PSP. Store IAP must *not* be used |
| Person-to-person, donations, B2B | Stripe or PSP (check guideline specifics) |

Region-specific exceptions exist (external purchase links, alternative billing in some countries). Check the current Apple guidelines and Play policy before relying on one. Getting this wrong is the most common payment-related rejection.

## RevenueCat (subscriptions and IAP)

What it does: wraps StoreKit + Play Billing, validates receipts server-side, tracks entitlements, and offers paywalls, analytics and webhooks. The Flutter package is `purchases_flutter`, with `purchases_ui_flutter` for hosted paywalls.

Setup:
1. Create products in App Store Connect and Play Console (same product ids where possible). Play needs an uploaded build on a testing track before products are usable.
2. In RevenueCat, add the apps (App Store with an in-app purchase key, Play with service-account credentials), create **Entitlements** (e.g. `pro`), attach products, and group them into an **Offering**.
3. App: configure once at startup, with the **platform-specific public SDK key**:
```dart
Future<void> initPurchases(String? appUserId) async {
  final key = Platform.isIOS ? Env.rcAppleKey : Env.rcGoogleKey; // public keys, via --dart-define
  await Purchases.configure(PurchasesConfiguration(key)..appUserID = appUserId);
}
```
4. Gate features on **entitlements**, not product ids:
```dart
final info = await Purchases.getCustomerInfo();
final isPro = info.entitlements.active.containsKey('pro');
```
5. Purchase from the current offering:
```dart
final offerings = await Purchases.getOfferings();
final pkg = offerings.current?.monthly;
if (pkg != null) {
  try {
    final result = await Purchases.purchasePackage(pkg);
    // re-check result.customerInfo.entitlements.active['pro']
  } on PlatformException catch (e) {
    if (PurchasesErrorHelper.getErrorCode(e) != PurchasesErrorCode.purchaseCancelledError) rethrow;
  }
}
```
Method names change between major versions, so confirm against the pinned version.

Must-haves:
- **Restore purchases** button (Apple requires it).
- Identify users: `Purchases.logIn(userId)` after your auth, and `logOut()` on sign-out, so entitlements follow the account.
- Listen for updates (`addCustomerInfoUpdateListener`) so a renewal or refund changes access live.
- Backend truth: use RevenueCat **webhooks** or the REST API to grant server-side access. Don't trust a client flag for anything valuable.
- Paywall: show price from the product (localized string), terms, renewal period, and links to privacy/terms. Apple and Google both review this.
- Testing: StoreKit config file / sandbox testers on iOS, license testers + internal track on Android. RevenueCat shows sandbox data separately.

## Official `in_app_purchase` (without RevenueCat)

Fine for simple cases, but **you own receipt validation**. A real app got this wrong: after a purchase it called `POST /subscription {planId}` with no receipt. The backend activated premium on the app's word, so anyone with a token could call that endpoint and get premium free.

Do:
- Subscribe to `InAppPurchase.instance.purchaseStream` **once, at app start** (not in a screen controller). Store the subscription and cancel it on dispose. Purchases can arrive at any time (renewals, pending → purchased, restores).
- On `purchased` **and `restored`**: send `purchase.verificationData.serverVerificationData` + `source` + productId to your backend. The backend verifies with the App Store Server API / Google Play Developer API, then grants the entitlement. Grant only after the server confirms.
- Call `completePurchase` when `pendingCompletePurchase` is true **for every final status** (purchased, restored, error). Un-completed Android purchases are auto-refunded after 3 days, and iOS ones stay stuck in the queue.
- Handle `pending` (e.g. parents approving, cash payments) without granting access. Handle `canceled` quietly, with no error snackbar.
- `queryProductDetails` → log and surface `notFoundIDs`. A typo in a product ID (`com.app.planss.monthly`) means the product just never appears.
- Subscriptions are `buyNonConsumable`. Coins and credits are `buyConsumable` (with `autoConsume` on Android).
- Server-side renewals and cancellations come via App Store Server Notifications and Play Real-time Developer Notifications. Without them, the backend never learns a subscription lapsed.
- If this sounds like a lot, that's why RevenueCat exists. Recommend it unless there's a reason not to.

## Stripe (physical goods, services)

Flutter package: `flutter_stripe`. **Architecture: the server creates a PaymentIntent and the app confirms it.**

```
App ──(cart id)──▶ Your backend ──(secret key)──▶ Stripe: create PaymentIntent (+ Customer, ephemeral key)
App ◀─(client_secret, ephemeralKey, customerId, publishableKey)── backend
App: PaymentSheet.init → present → result
Stripe ──webhook payment_intent.succeeded──▶ backend marks order paid   ← source of truth
```

App side:
```dart
Stripe.publishableKey = Env.stripePublishableKey; // pk_… only
Stripe.merchantIdentifier = 'merchant.com.example.app'; // Apple Pay
await Stripe.instance.applySettings();

await Stripe.instance.initPaymentSheet(
  paymentSheetParameters: SetupPaymentSheetParameters(
    paymentIntentClientSecret: s.clientSecret,
    customerId: s.customerId,
    customerEphemeralKeySecret: s.ephemeralKey,
    merchantDisplayName: 'Example',
    applePay: const PaymentSheetApplePay(merchantCountryCode: 'AU'),
    googlePay: const PaymentSheetGooglePay(merchantCountryCode: 'AU', testEnv: true),
  ),
);
try {
  await Stripe.instance.presentPaymentSheet();
  // Show "processing", then poll/await the backend order status (webhook-confirmed).
} on StripeException catch (e) {
  if (e.error.code != FailureCode.Canceled) showError(e.error.localizedMessage);
}
```

Rules:
- **The amount is computed on the server** from the cart. Never send a price from the app.
- Use **idempotency keys** on PaymentIntent creation. Disable the pay button while submitting. On timeout, check order status before retrying.
- The order is paid when the **webhook** says so, not when the sheet closes. Handle `requires_action` (3-D Secure), which PaymentSheet does for you.
- Native setup for `flutter_stripe`: Android needs `FlutterFragmentActivity` in `MainActivity` and an AppCompat/MaterialComponents theme. iOS needs a minimum platform version in the Podfile. Check its README for the pinned version.
- Test with Stripe test mode keys and test cards (`4242…`, 3DS cards), and use `stripe listen` to forward webhooks locally.

## Apple Pay
- An Apple Developer **Merchant ID** (`merchant.com.example.app`), a payment processing certificate created *through Stripe* (or your PSP), and the **Apple Pay capability** with the merchant id in `Runner.entitlements`.
- Show Apple Pay only when the device supports it (`Stripe.instance.isPlatformPaySupported()`).
- Follow Apple's Human Interface Guidelines for the Apple Pay button (official button, no custom styling).
- Apple Pay is for physical goods and services. Digital goods still go through IAP.

## Google Pay
- Through Stripe: enable in PaymentSheet (`googlePay:` params). Use `testEnv: true` until production access is approved.
- Add to `AndroidManifest.xml` inside `<application>`:
```xml
<meta-data android:name="com.google.android.gms.wallet.api.enabled" android:value="true"/>
```
- Production requires completing Google Pay's business console / integration checklist. Check https://developers.google.com/pay.
- **Google Play Billing ≠ Google Pay.** Play Billing (via RevenueCat/`in_app_purchase`) is for digital goods. Google Pay is a wallet for physical goods via your PSP.

## Red flags found in real apps (stop and raise immediately)

| Found | Why it's serious | Fix |
|---|---|---|
| `https://api.stripe.com/...` called from Dart with `Bearer $stripeSecretKey` | The secret key ships in every APK/IPA and anyone can extract it, then refund, charge or read all customers | Move PaymentIntent creation to the backend, **roll the key** in the Stripe dashboard, and purge it from git history |
| `sk_test_`/`sk_live_` in source or git history | Same, even test keys leak account data and webhooks | Roll, purge history, add a secret scanner |
| Amount computed in the app (`(amount * 100).toInt()`) and sent to Stripe | The client can change the price | Server computes from cart/order id |
| Hardcoded `paymentMethod: "pm_card_visa"` | A Stripe *test* token, so payments never work in live mode | Collect via PaymentSheet |
| Digital coins/credits sold via Stripe *and* RevenueCat in the same app | Store policy: digital goods must use IAP, which gets the app rejected or removed | Coins and subscriptions via RevenueCat only |
| `Purchases.configure` awaited in `main()` before everything, unguarded | A config error blocks launch | Guard it; don't block first frame |
| `print("Payment API Response: ${response.body}")` / `"Exception: $e"` shown to users | Leaks payment data to logs and raw errors to users | `debugPrint` of status only; map errors to copy |
| No restore-purchases button, no `Purchases.logIn` | Apple rejection; entitlements lost on reinstall or new device | See the RevenueCat section |

This exact Stripe pattern (secret key in a `consts.dart`, direct `api.stripe.com` calls from a `stripe_service.dart`) was found in **five apps built from the same template**. When a repo looks template-derived, assume it inherited this and check.

When you find any of these, report them at the top of your answer with file references, before doing the requested task. Rolling keys and purging git history are the user's actions. Explain how, don't do it.

## Payment testing checklist
- [ ] Success, cancel, decline, 3-D Secure challenge, network drop mid-payment, app killed mid-payment.
- [ ] Double-tap does not double-charge (idempotency + disabled button).
- [ ] Webhook arrives late: UI shows "processing" and resolves.
- [ ] Subscriptions: purchase, restore, renew, cancel, refund, upgrade/downgrade, expired card (grace period).
- [ ] Wallet buttons only shown when supported. Test keys swapped for live only at release, with approval.

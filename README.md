# Luton Accountants — funnel landing page (Elementor)

A single-page lead funnel for **www.lutonaccountants.co.uk**. It includes a hero with a quote form, pricing, an instant quote calculator, local SEO content, booking, FAQs, WhatsApp everywhere and an exit-intent popup.

## Files

| File | What it's for |
|---|---|
| `dist/elementor-html-widget.html` | **Paste this into Elementor.** It's the whole page in one block. |
| `dist/elementor-template.json` | Alternative: import it as a ready-made Elementor page. |
| `dist/preview.html` | Open it in a browser to preview the page. |
| `dist/seo-settings.txt` | SEO title, meta description and keyphrases for Yoast or Rank Math. |
| `config.json` | **Edit your details here**: phone, WhatsApp, prices, address, FAQs and reviews. |
| `src/funnel.html`, `build.py` | Source files. Run `python3 build.py` after editing `config.json`. |

## Putting it into Elementor

**Option A: paste it (simplest)**
1. In WordPress go to **Pages → Add New** and click **Edit with Elementor**.
2. Click the ⚙️ (Page Settings) icon and set **Page Layout → Elementor Canvas**. This removes the theme header and footer, which is what you want for a funnel.
3. Add a **Section/Container** and set **Content Width: Full Width**. Set padding and gap to 0.
4. Drag in an **HTML** widget and paste the **entire** contents of `dist/elementor-html-widget.html`.
5. Click **Publish**. In **Settings → Reading** you can make this page the homepage.

**Option B: import it**
**Templates → Saved Templates → Import Templates →** `dist/elementor-template.json`. Then create a page, click the folder icon → **My Templates → Insert**.

> The HTML widget needs an Administrator account, because WordPress only lets admins save `<script>` code. On some managed hosts you also need the `unfiltered_html` capability.

## Before going live: change these in `config.json`

1. `phone_display`, `phone_e164`: your real number (the `e164` format is `+441582…`).
2. `whatsapp_number`: international format with no `+` or spaces, e.g. `447912345678`.
3. `email` and `address`: as a remote practice, leave `street` and `postcode` empty. The page then says "Remote practice serving Luton & Bedfordshire" and no office address is published. On Google Business Profile, set yourself up as a **service-area business** with the address hidden. Keep the business name and phone identical everywhere, because consistency is a major local-ranking factor.
4. `plans`, `addons_text` and `calculator`: your real prices. The prices included are realistic UK placeholders.
5. `reviews`: replace with **genuine** Google reviews. To hide the section, use an empty list (`[]`).
6. `form_endpoint`: see below. **Important**.
7. Optional: `booking_url` (Calendly or similar) adds a "Pick a time online" option. `google_reviews_url` adds a reviews button.
8. Check every claim is true for you: "WhatsApp reply within 24 hours", "taking on new clients", the sectors you serve and the FAQ answers.

Then run `python3 build.py` and re-paste `dist/elementor-html-widget.html`.

## How form leads reach you

- **With `form_endpoint` set** (recommended): leads are POSTed as JSON. A free [Formspree](https://formspree.io) form works out of the box: paste its URL, e.g. `https://formspree.io/f/abcdwxyz`. Make.com, Zapier and n8n webhooks also work, and can forward leads to email, a CRM or WhatsApp. Each lead includes name, phone, email, service, quote, preferred contact method and time, page URL, and UTM/gclid/fbclid for ad tracking.
- **With no endpoint**: submitting opens WhatsApp with the enquiry pre-filled. No lead is lost, but the visitor still has to press send.
- **Prefer Elementor Pro forms?** Delete the `<form>` blocks and use the Pro Form widget. You lose the WhatsApp hand-off and the calculator-to-form link.

## Conversion features

- Countdown bar to the 31 January Self Assessment deadline. It updates automatically every year.
- Sticky header with click-to-call and WhatsApp.
- Hero quote form, a three-field form above the fold.
- Instant quote calculator. "Lock in this price on WhatsApp" sends the exact quote, and "Book a call" carries the quote into the booking form.
- Pricing cards that pre-select the chosen plan in the booking form.
- A floating WhatsApp button on desktop with a pop-out hint. On mobile there's a sticky bottom bar instead: **Call · WhatsApp · Free call**.
- Exit-intent popup offering a "free tax review". It shows at most once per session, never after a lead, and on mobile after 40 seconds.
- After submitting, a thank-you state with a "message us on WhatsApp" follow-up that includes their details.
- Honeypot spam protection, form validation and a GDPR consent checkbox.

## Local SEO built in

- Keyword-led H1 ("accountants in Luton"), H2s and copy naming Luton areas, nearby towns and LU postcodes.
- `AccountingService` LocalBusiness schema: service area, opening hours and prices. A street address and map location are added only if you set one.
- `FAQPage` schema generated from the same FAQ list shown on the page.
- A footer with business name, service area and phone that should match your Google Business Profile.
- Add the title and description from `dist/seo-settings.txt` to Yoast or Rank Math.

**Off-page actions that matter most:** use this URL as the website on your Google Business Profile, set the primary category to "Accountant", and ask every happy client for a Google review that mentions Luton.

## Tracking

If Google Tag Manager, GA4 (`gtag`) or the Meta Pixel are on the site, these events fire automatically:
`generate_lead` (Meta: `Lead`), `laf_click` (with a `label` such as `wa_header`, `call_mbar` or `plan_growth`), `select_plan`, `calc_used`, `calc_quote_to_booking` and `exit_popup_shown`.
Mark `generate_lead` as a conversion in GA4 or Google Ads.

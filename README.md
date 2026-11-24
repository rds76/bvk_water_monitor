# BVK Water Monitor — Home Assistant Custom Integration

A [HACS](https://hacs.xyz/)-compatible Home Assistant integration that pulls water consumption data from the **BVK (Brněnské vodárny a kanalizace)** customer portal and exposes it as sensors in Home Assistant.

---

## Sensors

| Sensor | Unit | Description |
|---|---|---|
| **Water Meter Index** | m³ | Current cumulative meter reading (`TOTAL_INCREASING`) |
| **Daily Water Consumption** | L | Most recent day's consumption |
| **Monthly Water Consumption** | L | Current month's total consumption |

The daily sensor also exposes a `last_7_days` attribute with a date → litres history, and the meter index sensor exposes the `last_reading_at` timestamp.

---

## How it works

1. Authenticates with the [BVK customer portal](https://zis.bvk.cz) using your email and password when setup needs token URLs.
2. Caches SUEZ Smart Solutions token URLs locally and reuses them to access `cz-sitr.suezsmartsolutions.com`.
3. Scrapes the portal for meter index, daily and monthly consumption every **2 hours**.

On setup or if the local token cache is missing, the integration logs into BVK
and stores the SUEZ token URLs locally. Later updates reuse those URLs; a BVK
login is repeated only when SUEZ rejects a cached URL. A network failure alone
does not trigger a BVK login. Newly added consumption places are discovered
when token URLs are refreshed. If a BVK login fails or cannot be confirmed,
automatic login is paused, including after a Home Assistant restart. Re-enter
your credentials when Home Assistant requests re-authentication to resume.

---

## Installation

### Via HACS (recommended)

1. In HACS go to **Integrations → ⋮ → Custom repositories**.
2. Add `https://github.com/koooop/bvk_water_monitor` with category **Integration**.
3. Install **BVK Water Monitor** and restart Home Assistant.

### Manual

1. Copy the `custom_components/water_monitor/` folder into your HA `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

Go to **Settings → Integrations → Add Integration → BVK Water Monitor**.

### Step 1 — BVK credentials
Enter your **email** and **password** for the BVK customer portal (`https://zis.bvk.cz`).

The integration validates the credentials once for each form submission. If
validation fails, it remains on the form and does not retry automatically.
After successful setup, it logs in to discover the smart-meter token URL.

---

## Supported regions

Currently only **BVK Brno (Czech Republic)** is supported. The integration relies on the SUEZ Smart Solutions portal used by BVK.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Login fails at setup | Check the account and credentials before submitting the form again. |
| Re-authentication requested | Login failed or could not be confirmed. Check the BVK portal and network, then re-enter your credentials. No automatic login is attempted until then. |
| Sensors unavailable | Check connectivity and whether the BVK and SUEZ portals are available. |
| Data is 1–2 days behind | Expected — the smart meter transmits readings with a ~24 h delay. |

---

## License

MIT

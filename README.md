# FloodWatch Kenya v2.0 — Nationwide Subscriber Experience

This release expands the product from a Nairobi-only prototype into a nationwide decision-support tool covering 92 areas across Kenya, plus emergency, alerting and accessibility features requested directly by the product owner.

## Product flow

Subscriber → saves places (matched to one of 92 monitored areas nationwide) → sees current risk for those areas → sees recommended action → monitors routes between areas → reports flooding → can reach emergency contacts and share an alert instantly.

## Area coverage and data provenance

Zone susceptibility (baseline, drainage, historical exposure, river exposure, elevation) is a first-pass editorial judgment informed by:

- The 2026 Nairobi Rivers Regeneration Programme mapping of 38 flood-prone Nairobi neighbourhoods across five river corridors, reported by the Ministry of Interior, plus 22 additional Nairobi areas for full city coverage (60 Nairobi areas total).
- The 2024 Space4All "Diagnostic of Urban Flooding in Nairobi" report (Kibera, Mathare, Mukuru, Kariobangi as focus areas; ~27% of city territory highly flood-prone).
- Kenya Meteorological Department advisories and disaster reporting on the March–May 2024 and March–May 2026 nationwide flood events, which named 30 counties as flood-affected in 2026 alone. 32 national hotspots are included: chronic river-basin zones (Budalangi, the Kano Plains/Ahero, the Tana River basin, Garissa), coastal counties (Mombasa, Kilifi, Kwale, Lamu, Taita Taveta), semi-arid flash-flood zones (Turkana, Marsabit, Isiolo, Wajir, Mandera), Rift Valley landslide/flood risk areas (Narok, Baringo, West Pokot, Elgeyo Marakwet, Nakuru, Naivasha, Eldoret), and central/eastern/western counties repeatedly flagged in 2024–2026 advisories (Kiambu, Murang'a, Kirinyaga, Kitui, Makueni, Kajiado, Bungoma, Kisumu, Homa Bay, Migori).

**These susceptibility scores are not calibrated hydrological output.** They are a defensible starting point pending real terrain/drainage modelling.

## What's new in v2.0

- **Nationwide coverage**: 92 monitored areas (60 Nairobi + 32 national), grouped by corridor/region in every dropdown and on the map.
- **Per-area live rainfall**: a single multi-location Open-Meteo request now returns live rain/forecast for every one of the 92 areas individually, replacing the earlier single citywide reading applied to all zones.
- **Satellite basemap**: a free Esri World Imagery layer toggle alongside the OpenStreetMap street layer.
- **Live traffic deep link**: each zone's map popup links out to Google Maps' live traffic view for that location (no API key required; this is a link-out, not an embedded live feed).
- **Emergency button**: a fixed on-map button opens Kenya's national emergency numbers (Police 999/112, Safaricom 911, Kenya Red Cross 1199, St John Ambulance, AMREF Flying Doctors) as tap-to-dial links, plus a flood safety protocol checklist.
- **Pop-up alerts**: browser Notification API support — fires a native notification when a subscriber's highest-risk saved place crosses into HIGH or SEVERE. Only works while the tab is open (see limitations below).
- **Audible alarm**: a short tone plays automatically when the highest-risk reading reaches SEVERE.
- **WhatsApp sharing**: a "Share via WhatsApp" button opens WhatsApp with a pre-filled alert message the subscriber can send to any contact or group — this is a share action the person triggers, not an automated broadcast.
- **Eye-friendly display**: a light/dark theme toggle, persisted per device.

## Current integrations

- Live per-area hourly + 15-minute rainfall/forecast via Open-Meteo (one multi-location request for all 92 zones).
- Historical Nairobi flood observations via the public ArcGIS FeatureServer (Nairobi-only; national historical flood data is not yet integrated).
- Local browser storage for saved places, routes, theme preference, and prototype flood reports (geolocated and assigned to the nearest monitored zone).
- Browser Notification API and Web Audio for pop-up/alarm alerts (client-side only, tab must be open).
- wa.me deep link for WhatsApp sharing (manual send, no messaging backend).

## Design principles

1. Alerts must be relevant to a subscriber's location/route.
2. Every alert should explain where, why, when and what action to take.
3. Risk score is an index, not a probability.
4. Official warnings remain authoritative.
5. Community reports must be verified before becoming high-confidence alerts.

## Next production work

- Account/authentication and paid subscriptions.
- True background push notifications (current pop-ups only fire while the browser tab is open; real background delivery needs a service worker plus a push server) and SMS/WhatsApp Business API for automatic outbound alerts (current WhatsApp button is a manual share action, not automated sending).
- Geocoded saved places (currently matched to the nearest of 92 named zones, not a real address) and actual route geometry (currently a straight line between two zones).
- Calibrated, per-zone susceptibility from real terrain/drainage modelling, replacing the current editorial first-pass scores.
- Embedded live traffic data (currently a link-out to Google Maps rather than an in-app feed, since a licensed traffic API key is needed).
- KMD official-warning ingestion (currently always reads "no live feed").
- National historical flood-extent data (the ArcGIS layer currently covers Nairobi only).
- Human/automated report verification (all community reports are currently unverified by design).
- Alert history and subscriber feedback ("useful / not useful").
- Fleet dashboard and API.

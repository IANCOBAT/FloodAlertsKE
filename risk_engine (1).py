
from dataclasses import dataclass, field
from math import exp
from typing import List, Optional

@dataclass
class Zone:
    name: str
    baseline: float
    drainage: float       # 0-100, higher = more drainage vulnerability
    historical: float     # 0-100, historical flood evidence
    river_exposure: float # 0-100
    elevation: float      # 0-100, higher = safer/elevated

@dataclass
class Inputs:
    rain_15m: float = 0.0
    rain_1h: float = 0.0
    rain_3h: float = 0.0
    rain_6h: float = 0.0
    rain_24h: float = 0.0
    forecast_1h: float = 0.0       # forecast rainfall mm next hour
    rain_probability: float = 0.0  # 0-100
    community_reports: int = 0
    verified_reports: int = 0
    official_warning: int = 0      # 0 none, 1 watch, 2 warning
    report_recency_minutes: Optional[float] = None

@dataclass
class RiskResult:
    score: int
    level: str
    confidence: int
    drivers: List[str] = field(default_factory=list)
    action: str = "Monitor conditions."
    time_window: str = "Unknown"

def clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def rain_score(i: Inputs):
    # Tunable first-pass thresholds. These are NOT calibrated flood probabilities.
    s15 = clamp(i.rain_15m / 12 * 100)
    s1  = clamp(i.rain_1h / 35 * 100)
    s3  = clamp(i.rain_3h / 60 * 100)
    s6  = clamp(i.rain_6h / 90 * 100)
    s24 = clamp(i.rain_24h / 150 * 100)
    sf  = clamp(i.forecast_1h / 35 * 100) * (0.35 + 0.65*i.rain_probability/100)

    # Short-duration intense rain gets more weight for urban flash flooding.
    return (0.25*s15 + 0.30*s1 + 0.18*s3 + 0.10*s6 + 0.07*s24 + 0.10*sf)

def report_score(i: Inputs):
    verified = clamp(i.verified_reports * 25)
    unverified = clamp(i.community_reports * 7)
    return max(verified, unverified)

def calculate(zone: Zone, i: Inputs) -> RiskResult:
    r = rain_score(i)

    # Static susceptibility: useful until we have calibrated terrain/drainage layers.
    susceptibility = (
        0.30*zone.baseline +
        0.30*zone.drainage +
        0.25*zone.historical +
        0.10*zone.river_exposure +
        0.05*(100-zone.elevation)
    )

    reports = report_score(i)
    official = 0 if i.official_warning == 0 else (55 if i.official_warning == 1 else 85)

    # Dynamic rainfall dominates; static susceptibility modifies local exposure.
    score = 0.58*r + 0.22*susceptibility + 0.12*reports + 0.08*official

    drivers = []
    if i.rain_1h >= 20: drivers.append("heavy 1-hour rainfall")
    if i.rain_3h >= 40: drivers.append("high 3-hour accumulation")
    if i.rain_24h >= 100: drivers.append("wet antecedent conditions")
    if i.verified_reports: drivers.append(f"{i.verified_reports} verified local report(s)")
    if i.official_warning: drivers.append("official warning/watch")
    if zone.historical >= 60: drivers.append("historical flood exposure")
    if zone.drainage >= 60: drivers.append("drainage vulnerability")

    score = int(round(clamp(score)))
    if score >= 80:
        level, action = "SEVERE", "Avoid exposed low-lying roads and crossings; reroute if possible."
    elif score >= 65:
        level, action = "HIGH", "Prepare to reroute; avoid known low points and monitor updates."
    elif score >= 45:
        level, action = "WATCH", "Monitor closely and allow extra travel time."
    else:
        level, action = "LOW", "Normal caution; monitor official warnings."

    # Confidence is deliberately separate from risk.
    confidence = 35
    if i.verified_reports: confidence += 15
    if i.rain_1h > 0: confidence += 15
    if i.forecast_1h > 0: confidence += 10
    if i.official_warning: confidence += 15
    if i.report_recency_minutes is not None and i.report_recency_minutes <= 30: confidence += 10
    confidence = int(clamp(confidence, 20, 95))

    if i.rain_1h >= 20 or i.forecast_1h >= 20:
        window = "next 30–120 minutes"
    elif i.rain_3h >= 40:
        window = "next 1–3 hours"
    else:
        window = "no immediate high-risk window identified"

    return RiskResult(score, level, confidence, drivers, action, window)

if __name__ == "__main__":
    # Matches the 60-zone citywide catalogue used in index.html. Susceptibility values are a
    # first-pass editorial judgment (see README: Nairobi Rivers Regeneration Programme mapping,
    # the 2024 Space4All urban flooding diagnostic, and 2024/2026 flood event reporting) —
    # not calibrated hydrological output.
    zones = [
        # Nairobi East corridor
        Zone("Kiambiu", 65, 80, 85, 75, 20),
        Zone("Dandora", 55, 75, 80, 70, 25),
        Zone("Kariobangi", 60, 78, 82, 75, 20),
        Zone("Kayole", 50, 62, 58, 52, 38),
        Zone("Komarock", 38, 50, 45, 38, 48),
        Zone("Njiru", 42, 52, 45, 42, 45),
        Zone("Ruai", 38, 48, 40, 38, 48),
        Zone("Mwiki", 42, 52, 45, 42, 45),
        Zone("Donholm", 55, 70, 70, 55, 35),
        Zone("Savannah", 48, 58, 52, 48, 40),
        Zone("Tassia", 44, 54, 48, 44, 42),
        Zone("Fedha", 48, 58, 52, 48, 38),
        # Nairobi West corridor
        Zone("Madaraka", 44, 54, 48, 44, 42),
        Zone("Nairobi West", 40, 50, 44, 40, 45),
        Zone("Lang'ata", 28, 34, 28, 28, 55),
        Zone("Kawangware", 55, 70, 56, 46, 35),
        Zone("Kangemi", 55, 68, 56, 50, 35),
        Zone("Lavington", 20, 25, 20, 25, 65),
        Zone("Westlands", 25, 30, 25, 20, 65),
        Zone("Parklands", 30, 35, 30, 30, 55),
        Zone("Kitisuru", 15, 20, 15, 20, 70),
        Zone("Spring Valley", 20, 25, 20, 25, 65),
        Zone("Kileleshwa", 20, 25, 20, 25, 60),
        Zone("Chiromo", 32, 38, 36, 42, 50),
        # Nairobi North corridor
        Zone("Mathare", 70, 85, 90, 85, 15),
        Zone("Korogocho", 65, 80, 85, 80, 18),
        Zone("Lucky Summer", 50, 60, 55, 50, 35),
        # Nairobi Central corridor
        Zone("CBD", 35, 45, 40, 45, 45),
        Zone("Globe", 35, 45, 40, 45, 45),
        Zone("Gikomba", 50, 62, 58, 62, 35),
        Zone("Eastleigh", 45, 55, 45, 40, 40),
        Zone("Industrial Area", 55, 70, 75, 65, 35),
        # Nairobi South corridor
        Zone("Kilimani", 25, 30, 25, 30, 55),
        Zone("Kibera", 65, 80, 88, 78, 18),
        Zone("South C", 60, 80, 80, 70, 25),
        Zone("South B", 45, 55, 50, 45, 40),
        Zone("Mukuru Kwa Reuben", 66, 82, 85, 80, 18),
        Zone("Kwa Njenga", 60, 76, 78, 74, 20),
        # Other Nairobi areas
        Zone("Karen", 10, 15, 10, 15, 75),
        Zone("Runda", 10, 15, 10, 15, 72),
        Zone("Muthaiga", 15, 20, 15, 20, 68),
        Zone("Gigiri", 12, 15, 10, 15, 70),
        Zone("Loresho", 15, 20, 15, 20, 65),
        Zone("Ridgeways", 15, 20, 12, 18, 68),
        Zone("Roysambu", 35, 45, 35, 30, 50),
        Zone("Zimmerman", 35, 45, 35, 30, 48),
        Zone("Kasarani", 40, 50, 40, 35, 45),
        Zone("Buruburu", 40, 50, 45, 40, 42),
        Zone("Umoja", 45, 55, 50, 45, 38),
        Zone("Embakasi", 50, 60, 55, 50, 35),
        Zone("Pipeline", 55, 65, 55, 50, 32),
        Zone("Imara Daima", 55, 65, 55, 55, 30),
        Zone("Syokimau", 45, 50, 45, 50, 38),
        Zone("Dagoretti", 40, 50, 40, 35, 50),
        Zone("Riruta", 40, 50, 40, 35, 48),
        Zone("Ngong Road", 25, 30, 25, 30, 55),
        Zone("Ngara", 45, 55, 50, 50, 42),
        Zone("Pangani", 45, 55, 45, 45, 42),
        Zone("Highridge", 25, 30, 25, 25, 58),
        Zone("Uthiru / Kabete", 30, 35, 25, 25, 55),
        # Nyanza / Lake Basin
        Zone("Budalangi (Busia)", 60, 55, 80, 85, 20),
        Zone("Ahero / Nyando (Kisumu)", 58, 55, 78, 82, 20),
        Zone("Kisumu Town", 40, 50, 42, 40, 45),
        Zone("Homa Bay", 35, 40, 35, 35, 50),
        Zone("Migori", 32, 38, 32, 30, 50),
        # Western Kenya
        Zone("Bungoma", 35, 42, 38, 32, 48),
        # Rift Valley
        Zone("Eldoret / Uasin Gishu", 38, 45, 42, 38, 48),
        Zone("Nakuru Town", 35, 42, 35, 30, 50),
        Zone("Naivasha", 32, 38, 30, 32, 50),
        Zone("Narok (Mai Mahiu corridor)", 40, 42, 45, 35, 42),
        Zone("Baringo", 35, 38, 38, 35, 45),
        Zone("West Pokot", 35, 38, 38, 32, 45),
        Zone("Elgeyo Marakwet", 30, 35, 32, 28, 50),
        # North Eastern & Northern Kenya
        Zone("Turkana (Lodwar)", 40, 35, 40, 35, 45),
        Zone("Marsabit", 38, 32, 35, 30, 48),
        Zone("Isiolo", 40, 35, 38, 35, 45),
        Zone("Garissa", 55, 45, 60, 65, 25),
        Zone("Wajir", 42, 35, 40, 35, 45),
        Zone("Mandera", 42, 35, 40, 35, 45),
        Zone("Tana River (Hola)", 58, 50, 70, 80, 20),
        Zone("Tana River (Garsen)", 58, 50, 72, 82, 18),
        # Coast
        Zone("Lamu", 48, 50, 50, 45, 35),
        Zone("Mombasa", 50, 60, 55, 40, 35),
        Zone("Kilifi", 45, 52, 45, 38, 40),
        Zone("Kwale", 42, 48, 42, 35, 42),
        Zone("Taita Taveta (Voi)", 38, 42, 38, 35, 45),
        # Central & Eastern Kenya
        Zone("Kitui", 35, 40, 35, 30, 48),
        Zone("Makueni (Wote)", 35, 40, 35, 30, 48),
        Zone("Kiambu Town", 40, 48, 40, 35, 45),
        Zone("Murang'a", 35, 42, 35, 32, 48),
        Zone("Kirinyaga (Kerugoya)", 35, 42, 35, 32, 48),
        Zone("Kajiado", 30, 35, 30, 28, 52),
    ]
    demo = Inputs(rain_15m=7, rain_1h=24, rain_3h=48, rain_6h=62,
                  rain_24h=110, forecast_1h=18, rain_probability=80,
                  community_reports=3, verified_reports=1, official_warning=1,
                  report_recency_minutes=18)
    for z in zones:
        print(z.name, calculate(z, demo))

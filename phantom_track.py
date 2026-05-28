#!/usr/bin/python3

import json
import requests
import time
import os
import re
import sys
import math
import socket
import struct
import hashlib
import ipaddress
import threading
import phonenumbers
from phonenumbers import carrier, geocoder, timezone as ph_timezone
from sys import stderr
from datetime import datetime
from collections import defaultdict

Bl   = '\033[30m'
Re   = '\033[1;31m'
Gr   = '\033[1;32m'
Ye   = '\033[1;33m'
Blu  = '\033[1;34m'
Mage = '\033[1;35m'
Cy   = '\033[1;36m'
Wh   = '\033[1;37m'
Rs   = '\033[0m'
Dim  = '\033[2m'
Bld  = '\033[1m'

TOOL_NAME    = "PHANTOM TRACK"
TOOL_VERSION = "1.0.0"
TOOL_AUTHOR  = "Alb4don"

BRAZIL_AREA_CODES = {
    "11": "São Paulo - SP", "12": "São José dos Campos - SP", "13": "Santos - SP",
    "14": "Bauru - SP",     "15": "Sorocaba - SP",            "16": "Ribeirão Preto - SP",
    "17": "São José do Rio Preto - SP", "18": "Presidente Prudente - SP",
    "19": "Campinas - SP",  "21": "Rio de Janeiro - RJ",      "22": "Campos dos Goytacazes - RJ",
    "24": "Volta Redonda - RJ", "27": "Vitória - ES",         "28": "Cachoeiro de Itapemirim - ES",
    "31": "Belo Horizonte - MG", "32": "Juiz de Fora - MG",   "33": "Governador Valadares - MG",
    "34": "Uberlândia - MG", "35": "Poços de Caldas - MG",    "37": "Divinópolis - MG",
    "38": "Montes Claros - MG", "41": "Curitiba - PR",        "42": "Ponta Grossa - PR",
    "43": "Londrina - PR",  "44": "Maringá - PR",             "45": "Foz do Iguaçu - PR",
    "46": "Francisco Beltrão - PR", "47": "Joinville - SC",   "48": "Florianópolis - SC",
    "49": "Chapecó - SC",   "51": "Porto Alegre - RS",        "53": "Pelotas - RS",
    "54": "Caxias do Sul - RS", "55": "Santa Maria - RS",     "61": "Brasília - DF",
    "62": "Goiânia - GO",   "63": "Palmas - TO",              "64": "Rio Verde - GO",
    "65": "Cuiabá - MT",    "66": "Rondonópolis - MT",        "67": "Campo Grande - MS",
    "68": "Rio Branco - AC", "69": "Porto Velho - RO",        "71": "Salvador - BA",
    "73": "Ilhéus - BA",    "74": "Juazeiro - BA",            "75": "Feira de Santana - BA",
    "77": "Vitória da Conquista - BA", "79": "Aracaju - SE",  "81": "Recife - PE",
    "82": "Maceió - AL",    "83": "João Pessoa - PB",         "84": "Natal - RN",
    "85": "Fortaleza - CE", "86": "Teresina - PI",            "87": "Petrolina - PE",
    "88": "Juazeiro do Norte - CE", "89": "Picos - PI",       "91": "Belém - PA",
    "92": "Manaus - AM",    "93": "Santarém - PA",            "94": "Marabá - PA",
    "95": "Boa Vista - RR", "96": "Macapá - AP",              "97": "Coari - AM",
    "98": "São Luís - MA",  "99": "Imperatriz - MA",
}

BRAZIL_OPERATORS = {
    "Vivo":   ["11", "17", "15", "19", "21", "31", "41", "51", "61", "71", "81", "85", "91"],
    "Claro":  ["11", "21", "31", "41", "51", "61", "71", "81", "85", "91"],
    "TIM":    ["11", "21", "31", "41", "51", "61", "71", "81", "85", "91"],
    "Oi":     ["21", "31", "61", "71", "81", "85", "91"],
    "Nextel": ["11", "21"],
}

BRAZIL_MOBILE_PREFIXES_9 = ["9"]
BRAZIL_VIRTUAL_OPERATORS  = ["MVNOnet", "Correios Celular", "Porto Seguro Tel", "Surf Telecom"]

INT_COUNTRY_CODES = {
    "1":  "United States / Canada", "7":  "Russia / Kazakhstan",
    "20": "Egypt",  "27": "South Africa", "30": "Greece",
    "31": "Netherlands", "32": "Belgium",  "33": "France",
    "34": "Spain",  "36": "Hungary",  "39": "Italy",
    "40": "Romania", "41": "Switzerland", "43": "Austria",
    "44": "United Kingdom", "45": "Denmark", "46": "Sweden",
    "47": "Norway", "48": "Poland",   "49": "Germany",
    "51": "Peru",   "52": "Mexico",   "53": "Cuba",
    "54": "Argentina", "55": "Brazil", "56": "Chile",
    "57": "Colombia", "58": "Venezuela", "60": "Malaysia",
    "61": "Australia", "62": "Indonesia", "63": "Philippines",
    "64": "New Zealand", "65": "Singapore", "66": "Thailand",
    "81": "Japan",  "82": "South Korea", "84": "Vietnam",
    "86": "China",  "90": "Turkey",   "91": "India",
    "92": "Pakistan", "93": "Afghanistan", "94": "Sri Lanka",
    "95": "Myanmar", "98": "Iran",    "212": "Morocco",
    "213": "Algeria", "216": "Tunisia", "218": "Libya",
    "220": "Gambia", "221": "Senegal", "222": "Mauritania",
    "234": "Nigeria", "251": "Ethiopia", "254": "Kenya",
    "255": "Tanzania", "256": "Uganda", "260": "Zambia",
    "263": "Zimbabwe", "351": "Portugal", "352": "Luxembourg",
    "353": "Ireland", "354": "Iceland", "358": "Finland",
    "380": "Ukraine", "381": "Serbia", "385": "Croatia",
    "386": "Slovenia", "420": "Czech Republic", "421": "Slovakia",
    "966": "Saudi Arabia", "971": "UAE", "972": "Israel",
    "973": "Bahrain", "974": "Qatar", "975": "Bhutan",
    "977": "Nepal",  "994": "Azerbaijan", "995": "Georgia",
    "996": "Kyrgyzstan", "998": "Uzbekistan",
}

SUSPICIOUS_PATTERNS = [
    r"^(\d)\1{6,}",
    r"^1234567", r"^0987654",
    r"^000000", r"^111111",
]

USERNAME_CONFIDENCE = {
    "exact_match":   0.95,
    "partial_match": 0.60,
    "not_found":     0.00,
}

IP_RISK_FACTORS = {
    "tor_exit":      0.90,
    "vpn":           0.70,
    "datacenter":    0.50,
    "residential":   0.10,
    "mobile":        0.05,
}

def clear():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')

def sanitize_input(text, max_len=256, allowed_chars=None):
    if not isinstance(text, str):
        return ""
    text = text.strip()[:max_len]
    if allowed_chars:
        text = re.sub(f"[^{re.escape(allowed_chars)}]", "", text)
    return text

def validate_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False

def safe_request(url, timeout=10, headers=None):
    try:
        h = {"User-Agent": "Mozilla/5.0 (compatible; PhantomTrack/2.0)"}
        if headers:
            h.update(headers)
        r = requests.get(url, timeout=timeout, headers=h, allow_redirects=True)
        return r
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def estimate_location_accuracy(ip_data):
    accuracy_score = 0.0
    notes = []
    conn = ip_data.get("connection", {})
    org  = conn.get("org", "").lower()
    isp  = conn.get("isp", "").lower()
    if any(k in org for k in ["hosting", "cloud", "datacenter", "amazon", "google", "microsoft", "azure", "digital ocean"]):
        accuracy_score += 0.2
        notes.append("Datacenter/Cloud IP - location may reflect server, not user")
    elif any(k in isp for k in ["mobile", "cellular", "wireless", "telecom"]):
        accuracy_score += 0.6
        notes.append("Mobile carrier - city-level accuracy likely")
    else:
        accuracy_score += 0.75
        notes.append("Residential ISP - city-level accuracy expected")
    if ip_data.get("is_eu"):
        notes.append("EU IP - GDPR may limit granularity")
    return round(accuracy_score * 100), notes

def detect_ip_anomalies(ip_data):
    anomalies = []
    conn = ip_data.get("connection", {})
    org  = conn.get("org", "").lower()
    if any(k in org for k in ["vpn", "proxy", "tor", "anonymous", "hide", "privacy"]):
        anomalies.append(f"{Re}VPN/Proxy/Tor detected{Wh}")
    if ip_data.get("type") == "IPv6":
        anomalies.append(f"{Ye}IPv6 address - geolocation less precise{Wh}")
    try:
        lat = float(ip_data.get("latitude", 0))
        lon = float(ip_data.get("longitude", 0))
        if lat == 0.0 and lon == 0.0:
            anomalies.append(f"{Re}Null Island coordinates (0,0) - geolocation failed{Wh}")
    except (ValueError, TypeError):
        pass
    return anomalies

def analyze_phone_risk(parsed_number, number_str):
    risk_score  = 0
    risk_notes  = []
    cleaned     = re.sub(r'\D', '', number_str)
    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, cleaned[-10:]):
            risk_score += 30
            risk_notes.append("Sequential/repeated digit pattern detected")
            break
    if not phonenumbers.is_valid_number(parsed_number):
        risk_score += 50
        risk_notes.append("Number fails international validity check")
    if not phonenumbers.is_possible_number(parsed_number):
        risk_score += 40
        risk_notes.append("Number length/format not possible for region")
    ntype = phonenumbers.number_type(parsed_number)
    if ntype == phonenumbers.PhoneNumberType.VOIP:
        risk_score += 35
        risk_notes.append("VoIP number - commonly used for fraud")
    elif ntype == phonenumbers.PhoneNumberType.TOLL_FREE:
        risk_score += 15
        risk_notes.append("Toll-free number")
    elif ntype == phonenumbers.PhoneNumberType.PREMIUM_RATE:
        risk_score += 25
        risk_notes.append("Premium rate number")
    return min(risk_score, 100), risk_notes

def get_brazil_details(number_str):
    cleaned = re.sub(r'\D', '', number_str)
    if cleaned.startswith("55"):
        cleaned = cleaned[2:]
    if len(cleaned) < 10:
        return None
    ddd = cleaned[:2]
    local = cleaned[2:]
    details = {"ddd": ddd, "local": local}
    details["city_region"] = BRAZIL_AREA_CODES.get(ddd, "Unknown region")
    if len(local) == 9 and local[0] == "9":
        details["line_type"] = "Mobile (9-digit)"
        details["is_mobile"] = True
    elif len(local) == 8:
        details["line_type"] = "Fixed-line or older mobile"
        details["is_mobile"] = False
    else:
        details["line_type"] = "Unknown"
        details["is_mobile"] = None
    matched_ops = [op for op, areas in BRAZIL_OPERATORS.items() if ddd in areas]
    details["likely_operators"] = matched_ops if matched_ops else ["Unknown"]
    return details

def get_number_type_label(number_type):
    mapping = {
        phonenumbers.PhoneNumberType.MOBILE:        "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE:    "Fixed-line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed-line or Mobile",
        phonenumbers.PhoneNumberType.TOLL_FREE:     "Toll-free",
        phonenumbers.PhoneNumberType.PREMIUM_RATE:  "Premium Rate",
        phonenumbers.PhoneNumberType.SHARED_COST:   "Shared Cost",
        phonenumbers.PhoneNumberType.VOIP:          "VoIP",
        phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
        phonenumbers.PhoneNumberType.PAGER:         "Pager",
        phonenumbers.PhoneNumberType.UAN:           "UAN",
        phonenumbers.PhoneNumberType.UNKNOWN:       "Unknown",
    }
    return mapping.get(number_type, "Other")

def run_banner():
    clear()
    time.sleep(0.3)
    stderr.write(f"""{Cy}
  ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
  ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
  ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
  ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
  ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
{Wh}
  ████████╗██████╗  █████╗  ██████╗██╗  ██╗
  ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
     ██║   ██████╔╝███████║██║     █████╔╝
     ██║   ██╔══██╗██╔══██║██║     ██╔═██╗
     ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗
     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
{Dim}
  {Cy}╔══════════════════════════════════════════════════════╗
  ║  {Wh}v{TOOL_VERSION} {Gr}OSINT Intelligence Framework{Cy}║
  ║  {Dim}By: Alb4don{Wh}|  {Gr}Version 1.0.0{Cy}        ║
  ║  {Ye}"The greatest asset of a modern investigator    ║
  ║        is not a magnifying glass,                    ║
  ║       but an internet connection." - Unknown{Cy}     ║
  ╚══════════════════════════════════════════════════════╝{Rs}
""")
    time.sleep(0.4)

def is_option(func):
    def wrapper(*args, **kwargs):
        run_banner()
        func(*args, **kwargs)
    return wrapper

@is_option
def IP_Track():
    raw = input(f"{Wh}\n  Enter IP target : {Gr}")
    ip  = sanitize_input(raw, max_len=64, allowed_chars="0123456789abcdefABCDEF:.")
    if not ip:
        print(f"{Re}  [!] Empty input.{Rs}")
        return
    if not validate_ip(ip):
        print(f"{Re}  [!] Invalid IP address format.{Rs}")
        return

    print(f"\n  {Wh}Querying geolocation data...{Rs}")
    req = safe_request(f"http://ipwho.is/{ip}")
    if not req:
        print(f"{Re}  [!] Failed to reach geolocation API. Check connectivity.{Rs}")
        return

    try:
        ip_data = json.loads(req.text)
    except json.JSONDecodeError:
        print(f"{Re}  [!] Invalid response from API.{Rs}")
        return

    if not ip_data.get("success", True) and ip_data.get("message"):
        print(f"{Re}  [!] API error: {ip_data['message']}{Rs}")
        return

    accuracy_pct, acc_notes = estimate_location_accuracy(ip_data)
    anomalies = detect_ip_anomalies(ip_data)

    try:
        lat = float(ip_data.get("latitude", 0))
        lon = float(ip_data.get("longitude", 0))
    except (ValueError, TypeError):
        lat, lon = 0.0, 0.0

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    print(f"\n  {Wh}{'═'*55}")
    print(f"  {Cy}  PHANTOM TRACK — IP INTELLIGENCE REPORT")
    print(f"  {Wh}{'═'*55}")
    print(f"  {Dim}Query Time       : {Wh}{now}")
    print(f"  {Wh}IP Target        : {Gr}{ip}")
    print(f"  {Wh}IP Type          : {Gr}{ip_data.get('type', 'N/A')}")
    print(f"  {Wh}{'─'*55}")
    print(f"  {Cy}[ GEOGRAPHIC LOCATION ]")
    print(f"  {Wh}Country          : {Gr}{ip_data.get('country', 'N/A')} ({ip_data.get('country_code', 'N/A')}) {ip_data.get('flag', {}).get('emoji', '')}")
    print(f"  {Wh}Continent        : {Gr}{ip_data.get('continent', 'N/A')} ({ip_data.get('continent_code', 'N/A')})")
    print(f"  {Wh}Region           : {Gr}{ip_data.get('region', 'N/A')} ({ip_data.get('region_code', 'N/A')})")
    print(f"  {Wh}City             : {Gr}{ip_data.get('city', 'N/A')}")
    print(f"  {Wh}Postal Code      : {Gr}{ip_data.get('postal', 'N/A')}")
    print(f"  {Wh}Latitude         : {Gr}{lat}")
    print(f"  {Wh}Longitude        : {Gr}{lon}")
    print(f"  {Wh}Maps (approx.)   : {Blu}https://www.google.com/maps/@{lat},{lon},12z")
    print(f"  {Wh}OSM Map          : {Blu}https://www.openstreetmap.org/?mlat={lat}&mlon={lon}&zoom=12")
    print(f"  {Wh}EU Member        : {Gr}{ip_data.get('is_eu', 'N/A')}")
    print(f"  {Wh}Calling Code     : {Gr}{ip_data.get('calling_code', 'N/A')}")
    print(f"  {Wh}Capital          : {Gr}{ip_data.get('capital', 'N/A')}")
    print(f"  {Wh}Borders          : {Gr}{ip_data.get('borders', 'N/A')}")
    print(f"  {Wh}{'─'*55}")
    print(f"  {Cy}[ NETWORK / ASN ]")
    conn = ip_data.get("connection", {})
    print(f"  {Wh}ASN              : {Gr}{conn.get('asn', 'N/A')}")
    print(f"  {Wh}Organization     : {Gr}{conn.get('org', 'N/A')}")
    print(f"  {Wh}ISP              : {Gr}{conn.get('isp', 'N/A')}")
    print(f"  {Wh}Domain           : {Gr}{conn.get('domain', 'N/A')}")
    print(f"  {Wh}{'─'*55}")
    print(f"  {Cy}[ TIMEZONE ]")
    tz = ip_data.get("timezone", {})
    print(f"  {Wh}TZ ID            : {Gr}{tz.get('id', 'N/A')}")
    print(f"  {Wh}Abbreviation     : {Gr}{tz.get('abbr', 'N/A')}")
    print(f"  {Wh}DST              : {Gr}{tz.get('is_dst', 'N/A')}")
    print(f"  {Wh}UTC Offset       : {Gr}{tz.get('utc', 'N/A')}")
    print(f"  {Wh}Current Time     : {Gr}{tz.get('current_time', 'N/A')}")
    print(f"  {Wh}{'─'*55}")
    print(f"  {Cy}[ LOCATION ACCURACY ANALYSIS ]")
    bar_filled = "█" * (accuracy_pct // 10)
    bar_empty  = "░" * (10 - accuracy_pct // 10)
    color = Gr if accuracy_pct >= 70 else (Ye if accuracy_pct >= 40 else Re)
    print(f"  {Wh}Accuracy Score   : {color}{bar_filled}{Dim}{bar_empty}{Rs} {color}{accuracy_pct}%")
    for note in acc_notes:
        print(f"  {Ye}  ↳ {note}")
    if anomalies:
        print(f"  {Wh}{'─'*55}")
        print(f"  {Cy}[ ANOMALY / RISK DETECTION ]")
        for a in anomalies:
            print(f"  {Re}  ⚠  {a}")
    print(f"  {Wh}{'═'*55}{Rs}")

@is_option
def phoneGW():
    raw = input(f"\n  {Wh}Enter phone number {Gr}(e.g. +5544999999999 or +6281xxxxxxxxx){Wh}: {Gr}")
    user_phone = sanitize_input(raw, max_len=20, allowed_chars="+0123456789 -()")
    if not user_phone:
        print(f"{Re}  [!] Empty input.{Rs}")
        return

    country_code_str = re.sub(r'\D', '', user_phone)
    if len(country_code_str) < 2:
        print(f"{Re}  [!] Number too short.{Rs}")
        return

    cc2 = country_code_str[:2]
    cc3 = country_code_str[:3]
    detected_country = INT_COUNTRY_CODES.get(cc3) or INT_COUNTRY_CODES.get(cc2)

    if user_phone.startswith("+55") or user_phone.startswith("55") and not user_phone.startswith("+"):
        default_region = "BR"
    elif user_phone.startswith("+62") or (not user_phone.startswith("+") and user_phone.startswith("0")):
        default_region = "ID"
    else:
        default_region = None

    try:
        if default_region:
            parsed = phonenumbers.parse(user_phone, default_region)
        else:
            parsed = phonenumbers.parse(user_phone)
    except phonenumbers.NumberParseException as e:
        print(f"{Re}  [!] Could not parse number: {e}{Rs}")
        return

    region_code   = phonenumbers.region_code_for_number(parsed)
    provider      = carrier.name_for_number(parsed, "en")
    location_en   = geocoder.description_for_number(parsed, "en")
    location_pt   = geocoder.description_for_number(parsed, "pt")
    is_valid      = phonenumbers.is_valid_number(parsed)
    is_possible   = phonenumbers.is_possible_number(parsed)
    fmt_intl      = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    fmt_e164      = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    fmt_national  = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    number_type   = phonenumbers.number_type(parsed)
    type_label    = get_number_type_label(number_type)
    tz_list       = ph_timezone.time_zones_for_number(parsed)
    tz_str        = ", ".join(tz_list) if tz_list else "N/A"

    risk_score, risk_notes = analyze_phone_risk(parsed, user_phone)
    is_brazil = (parsed.country_code == 55)
    brazil_details = get_brazil_details(user_phone) if is_brazil else None

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    print(f"\n  {Wh}{'═'*55}")
    print(f"  {Cy}  PHANTOM TRACK — PHONE INTELLIGENCE REPORT")
    print(f"  {Wh}{'═'*55}")
    print(f"  {Dim}Query Time           : {Wh}{now}")
    print(f"  {Wh}{'─'*55}")
    print(f"  {Cy}[ NUMBER DETAILS ]")
    print(f"  {Wh}International Format : {Gr}{fmt_intl}")
    print(f"  {Wh}E.164 Format         : {Gr}{fmt_e164}")
    print(f"  {Wh}National Format      : {Gr}{fmt_national}")
    print(f"  {Wh}Country Code         : {Gr}+{parsed.country_code}")
    print(f"  {Wh}National Number      : {Gr}{parsed.national_number}")
    print(f"  {Wh}Extension            : {Gr}{parsed.extension or 'None'}")
    print(f"  {Wh}{'─'*55}")
    print(f"  {Cy}[ GEOGRAPHIC INFO ]")
    print(f"  {Wh}Region Code          : {Gr}{region_code or 'N/A'}")
    print(f"  {Wh}Location (EN)        : {Gr}{location_en or 'N/A'}")
    print(f"  {Wh}Location (PT)        : {Gr}{location_pt or 'N/A'}")
    print(f"  {Wh}Country (detected)   : {Gr}{detected_country or 'N/A'}")
    print(f"  {Wh}Timezone(s)          : {Gr}{tz_str}")
    print(f"  {Wh}{'─'*55}")
    print(f"  {Cy}[ CARRIER / TYPE ]")
    print(f"  {Wh}Operator (known)     : {Gr}{provider or 'N/A'}")
    print(f"  {Wh}Number Type          : {Gr}{type_label}")
    valid_color = Gr if is_valid else Re
    poss_color  = Gr if is_possible else Re
    print(f"  {Wh}Valid Number         : {valid_color}{is_valid}")
    print(f"  {Wh}Possible Number      : {poss_color}{is_possible}")

    if is_brazil and brazil_details:
        print(f"  {Wh}{'─'*55}")
        print(f"  {Cy}[ BRAZIL-SPECIFIC ANALYSIS ]")
        print(f"  {Wh}DDD (Area Code)      : {Gr}{brazil_details['ddd']}")
        print(f"  {Wh}City / Region        : {Gr}{brazil_details['city_region']}")
        print(f"  {Wh}Line Type            : {Gr}{brazil_details['line_type']}")
        ops = ", ".join(brazil_details['likely_operators'])
        print(f"  {Wh}Likely Operators     : {Gr}{ops}")
        if brazil_details.get("is_mobile"):
            print(f"  {Ye}  ↳ 9-digit mobile numbers indicate post-2012 format (ANATEL regulation)")

    print(f"  {Wh}{'─'*55}")
    print(f"  {Cy}[ RISK / ANOMALY ANALYSIS ]")
    risk_color = Gr if risk_score < 30 else (Ye if risk_score < 60 else Re)
    bar_f = "█" * (risk_score // 10)
    bar_e = "░" * (10 - risk_score // 10)
    print(f"  {Wh}Risk Score           : {risk_color}{bar_f}{Dim}{bar_e}{Rs} {risk_color}{risk_score}%")
    if risk_notes:
        for rn in risk_notes:
            print(f"  {Ye}  ⚠  {rn}")
    else:
        print(f"  {Gr}  ✓  No anomalies detected")
    print(f"  {Wh}{'═'*55}{Rs}")

@is_option
def TrackLu():
    try:
        raw      = input(f"\n  {Wh}Enter Username : {Gr}")
        username = sanitize_input(raw, max_len=50, allowed_chars="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
        if not username:
            print(f"{Re}  [!] Invalid username.{Rs}")
            return

        results = {}
        social_media = [
            {"url": "https://www.facebook.com/{}", "name": "Facebook", "check_404": True},
            {"url": "https://www.twitter.com/{}", "name": "Twitter (X)", "check_404": True},
            {"url": "https://www.instagram.com/{}/", "name": "Instagram", "check_404": True},
            {"url": "https://www.linkedin.com/in/{}", "name": "LinkedIn", "check_404": True},
            {"url": "https://www.github.com/{}", "name": "GitHub", "check_404": True},
            {"url": "https://www.pinterest.com/{}/", "name": "Pinterest", "check_404": True},
            {"url": "https://www.tumblr.com/{}", "name": "Tumblr", "check_404": True},
            {"url": "https://www.youtube.com/@{}", "name": "YouTube", "check_404": True},
            {"url": "https://soundcloud.com/{}", "name": "SoundCloud", "check_404": True},
            {"url": "https://www.snapchat.com/add/{}", "name": "Snapchat", "check_404": True},
            {"url": "https://www.tiktok.com/@{}", "name": "TikTok", "check_404": True},
            {"url": "https://www.behance.net/{}", "name": "Behance", "check_404": True},
            {"url": "https://medium.com/@{}", "name": "Medium", "check_404": True},
            {"url": "https://www.quora.com/profile/{}", "name": "Quora", "check_404": True},
            {"url": "https://www.flickr.com/people/{}", "name": "Flickr", "check_404": True},
            {"url": "https://www.twitch.tv/{}", "name": "Twitch", "check_404": True},
            {"url": "https://www.dribbble.com/{}", "name": "Dribbble", "check_404": True},
            {"url": "https://t.me/{}", "name": "Telegram", "check_404": True},
            {"url": "https://www.reddit.com/user/{}", "name": "Reddit", "check_404": True},
            {"url": "https://keybase.io/{}", "name": "Keybase", "check_404": True},
            {"url": "https://about.me/{}", "name": "About.me", "check_404": True},
            {"url": "https://www.producthunt.com/@{}", "name": "Product Hunt", "check_404": True},
            {"url": "https://open.spotify.com/user/{}", "name": "Spotify", "check_404": True},
            {"url": "https://steamcommunity.com/id/{}", "name": "Steam", "check_404": True},
        ]

        found_count   = 0
        checked_count = 0
        print(f"\n  {Wh}Scanning {len(social_media)} platforms for {Gr}{username}{Wh}...{Rs}")

        for site in social_media:
            url      = site['url'].format(username)
            response = safe_request(url, timeout=8)
            checked_count += 1
            if response is None:
                results[site['name']] = {"status": "timeout", "url": url, "found": False}
            elif response.status_code == 200:
                body_lower = response.text.lower()
                false_positive_signals = [
                    "page not found", "user not found", "this account doesn't exist",
                    "sorry, this page isn't available", "profile not found",
                    "account suspended", "user doesn't exist", "no user found",
                    "does not exist", "couldn't find", "not available",
                    "404", "user has been banned",
                ]
                fp_detected = any(s in body_lower for s in false_positive_signals)
                if fp_detected:
                    results[site['name']] = {"status": "not_found", "url": url, "found": False}
                else:
                    results[site['name']] = {"status": "found", "url": url, "found": True}
                    found_count += 1
            elif response.status_code == 404:
                results[site['name']] = {"status": "not_found", "url": url, "found": False}
            elif response.status_code in (301, 302):
                results[site['name']] = {"status": "redirect", "url": url, "found": False}
            elif response.status_code == 429:
                results[site['name']] = {"status": "rate_limited", "url": url, "found": False}
            else:
                results[site['name']] = {"status": f"http_{response.status_code}", "url": url, "found": False}

        print(f"\n  {Wh}{'═'*55}")
        print(f"  {Cy}  PHANTOM TRACK — USERNAME INTELLIGENCE REPORT")
        print(f"  {Wh}{'═'*55}")
        print(f"  {Wh}Target Username  : {Gr}{username}")
        print(f"  {Wh}Platforms Scanned: {Gr}{checked_count}")
        print(f"  {Wh}Profiles Found   : {Gr}{found_count}")
        print(f"  {Wh}{'─'*55}")

        print(f"  {Cy}[ FOUND PROFILES ]{Rs}")
        any_found = False
        for site, data in results.items():
            if data["found"]:
                any_found = True
                print(f"  {Gr}  ✓  {Wh}{site:<20} {Gr}{data['url']}")
        if not any_found:
            print(f"  {Dim}  No profiles found on scanned platforms.")

        print(f"\n  {Cy}[ NOT FOUND / UNAVAILABLE ]{Rs}")
        for site, data in results.items():
            if not data["found"]:
                status_map = {
                    "not_found":   f"{Dim}Not found",
                    "timeout":     f"{Ye}Timeout",
                    "redirect":    f"{Ye}Redirect",
                    "rate_limited": f"{Ye}Rate limited",
                }
                status_label = status_map.get(data["status"], f"{Re}{data['status']}")
                print(f"  {Dim}  ✗  {Wh}{site:<20} {status_label}{Rs}")

        print(f"  {Wh}{'─'*55}")
        print(f"  {Ye}  Note: 200 OK with false-positive detection applied.{Rs}")
        print(f"  {Ye}  Some platforms may block automated requests.{Rs}")
        print(f"  {Wh}{'═'*55}{Rs}")

    except KeyboardInterrupt:
        print(f"\n{Re}  [!] Interrupted.{Rs}")

@is_option
def showIP():
    print(f"\n  {Wh}Fetching your public IP...{Rs}")
    r4 = safe_request("https://api.ipify.org/")
    r6 = safe_request("https://api6.ipify.org/")

    print(f"\n  {Wh}{'═'*50}")
    print(f"  {Cy}  PHANTOM TRACK — YOUR IP ADDRESS")
    print(f"  {Wh}{'═'*50}")
    if r4:
        print(f"  {Wh}IPv4 Address : {Gr}{r4.text.strip()}")
    else:
        print(f"  {Wh}IPv4 Address : {Re}Unavailable")
    if r6:
        v6 = r6.text.strip()
        if ":" in v6:
            print(f"  {Wh}IPv6 Address : {Gr}{v6}")
        else:
            print(f"  {Wh}IPv6 Address : {Dim}Not available (no IPv6 connectivity)")
    else:
        print(f"  {Wh}IPv6 Address : {Dim}Not available")
    print(f"  {Wh}{'═'*50}{Rs}")

@is_option
def AIAssist():
    print(f"\n  {Wh}{'═'*55}")
    print(f"  {Cy}  PHANTOM TRACK — AI CONTEXT ANALYZER")
    print(f"  {Wh}{'═'*55}")
    print(f"  {Gr}  Analyze suspicious indicators without external APIs.")
    print(f"  {Wh}{'─'*55}")
    print(f"  {Wh}  Select analysis type:")
    print(f"  {Wh}  [{Gr}1{Wh}] Analyze Phone Number")
    print(f"  {Wh}  [{Gr}2{Wh}] Analyze IP Address")
    print(f"  {Wh}  [{Gr}3{Wh}] Analyze Username pattern")
    print(f"  {Wh}  [{Gr}0{Wh}] Back")
    print(f"  {Wh}{'─'*55}")
    choice = input(f"  {Wh}Select: {Gr}").strip()

    if choice == "1":
        raw = input(f"\n  {Wh}Enter phone number: {Gr}")
        num = sanitize_input(raw, max_len=20, allowed_chars="+0123456789 -()")
        if not num:
            print(f"{Re}  [!] Empty input.{Rs}")
            return
        try:
            parsed = phonenumbers.parse(num, None)
        except phonenumbers.NumberParseException:
            try:
                parsed = phonenumbers.parse(num, "ID")
            except Exception as e:
                print(f"{Re}  [!] Parse error: {e}{Rs}")
                return
        risk, notes = analyze_phone_risk(parsed, num)
        ntype = get_number_type_label(phonenumbers.number_type(parsed))
        region = phonenumbers.region_code_for_number(parsed)
        loc    = geocoder.description_for_number(parsed, "en")
        valid  = phonenumbers.is_valid_number(parsed)
        print(f"\n  {Cy}[ AI ANALYSIS — PHONE ]{Rs}")
        print(f"  {Wh}Number        : {Gr}{phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}")
        print(f"  {Wh}Region        : {Gr}{region or 'Unknown'}")
        print(f"  {Wh}Location      : {Gr}{loc or 'Unknown'}")
        print(f"  {Wh}Type          : {Gr}{ntype}")
        print(f"  {Wh}Valid         : {Gr if valid else Re}{valid}")
        risk_color = Gr if risk < 30 else (Ye if risk < 60 else Re)
        print(f"  {Wh}Risk Score    : {risk_color}{risk}%")
        if notes:
            for n in notes:
                print(f"  {Ye}  ⚠  {n}")
        if risk < 30:
            print(f"\n  {Gr}  ✓ Low risk indicators. Number appears legitimate.")
        elif risk < 60:
            print(f"\n  {Ye}  ⚠ Moderate risk. Verify through additional channels.")
        else:
            print(f"\n  {Re}  ✗ High risk. Strong indicators of fraudulent/unusual number.")

    elif choice == "2":
        raw = input(f"\n  {Wh}Enter IP address: {Gr}")
        ip  = sanitize_input(raw, max_len=64, allowed_chars="0123456789abcdefABCDEF:.")
        if not validate_ip(ip):
            print(f"{Re}  [!] Invalid IP.{Rs}")
            return
        req = safe_request(f"http://ipwho.is/{ip}")
        if not req:
            print(f"{Re}  [!] Network error.{Rs}")
            return
        try:
            data = json.loads(req.text)
        except Exception:
            print(f"{Re}  [!] Invalid response.{Rs}")
            return
        acc, notes   = estimate_location_accuracy(data)
        anomalies    = detect_ip_anomalies(data)
        risk_score   = 100 - acc
        if anomalies:
            risk_score = min(risk_score + 20 * len(anomalies), 100)
        risk_color   = Gr if risk_score < 30 else (Ye if risk_score < 60 else Re)
        print(f"\n  {Cy}[ AI ANALYSIS — IP ]{Rs}")
        print(f"  {Wh}IP            : {Gr}{ip}")
        print(f"  {Wh}Country       : {Gr}{data.get('country', 'N/A')}")
        print(f"  {Wh}City          : {Gr}{data.get('city', 'N/A')}")
        print(f"  {Wh}ISP           : {Gr}{data.get('connection', {}).get('isp', 'N/A')}")
        print(f"  {Wh}Accuracy Est. : {Gr}{acc}%")
        print(f"  {Wh}Risk Score    : {risk_color}{risk_score}%")
        for n in notes:
            print(f"  {Ye}  ↳ {n}")
        for a in anomalies:
            print(f"  {Re}  ⚠  {a}")
        if risk_score < 30:
            print(f"\n  {Gr}  ✓ Low risk. Likely residential/legitimate IP.")
        elif risk_score < 60:
            print(f"\n  {Ye}  ⚠ Moderate risk. Could be shared/NAT/mobile.")
        else:
            print(f"\n  {Re}  ✗ High risk. Likely VPN/Proxy/Datacenter.")

    elif choice == "3":
        raw      = input(f"\n  {Wh}Enter username to analyze: {Gr}")
        username = sanitize_input(raw, max_len=50)
        if not username:
            print(f"{Re}  [!] Empty input.{Rs}")
            return
        notes = []
        score = 0
        if re.search(r'\d{4,}', username):
            notes.append("Contains 4+ consecutive digits (common in generated usernames)")
            score += 20
        if re.search(r'[_.\-]{2,}', username):
            notes.append("Multiple consecutive special chars")
            score += 15
        if len(username) > 30:
            notes.append("Unusually long username")
            score += 10
        if re.search(r'^[a-z]{6,12}\d{2,4}$', username, re.I):
            notes.append("Pattern: letters + trailing digits (very common for bots/bulk accounts)")
            score += 25
        if re.search(r'(admin|support|official|help|team|staff)', username, re.I):
            notes.append("Impersonation keyword detected")
            score += 35
        risk_color = Gr if score < 30 else (Ye if score < 60 else Re)
        print(f"\n  {Cy}[ AI ANALYSIS — USERNAME ]{Rs}")
        print(f"  {Wh}Username      : {Gr}{username}")
        print(f"  {Wh}Length        : {Gr}{len(username)}")
        print(f"  {Wh}Risk Score    : {risk_color}{score}%")
        if notes:
            for n in notes:
                print(f"  {Ye}  ⚠  {n}")
        else:
            print(f"  {Gr}  ✓ No suspicious patterns detected.")

    print(f"  {Wh}{'═'*55}{Rs}")

options = [
    {"num": 1, "text": "IP Tracker",             "func": IP_Track},
    {"num": 2, "text": "Show Your IP",            "func": showIP},
    {"num": 3, "text": "Phone Number Tracker",    "func": phoneGW},
    {"num": 4, "text": "Username Tracker",        "func": TrackLu},
    {"num": 5, "text": "AI Context Analyzer",     "func": AIAssist},
    {"num": 0, "text": "Exit",                    "func": exit},
]

def call_option(opt):
    for option in options:
        if option["num"] == opt:
            if "func" in option:
                option["func"]()
            return
    raise ValueError("Option not found")

def execute_option(opt):
    try:
        call_option(opt)
        input(f"\n  {Wh}[ {Gr}+ {Wh}] Press enter to continue")
        main()
    except ValueError as e:
        print(f"{Re}  [!] {e}{Rs}")
        time.sleep(2)
        main()
    except KeyboardInterrupt:
        print(f"\n  {Re}[!] Interrupted. Returning to menu...{Rs}")
        time.sleep(1)
        main()

def is_in_options(num):
    return any(o["num"] == num for o in options)

def option_text():
    lines = ""
    for opt in options:
        num_color = Re if opt["num"] == 0 else Gr
        lines += f"  {Wh}[{num_color}{opt['num']}{Wh}] {Gr}{opt['text']}{Rs}\n"
    return lines

def option():
    clear()
    stderr.write(f"""{Cy}
  ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
  ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
  ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
  ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
  ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝

  {Wh}████████╗██████╗  █████╗  ██████╗██╗  ██╗
  ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
     ██║   ██████╔╝███████║██║     █████╔╝
     ██║   ██╔══██╗██╔══██║██║     ██╔═██╗
     ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗
     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝

  {Dim}v{TOOL_VERSION}  |  {Gr}OSINT Intelligence Framework  {Dim}|  By: Alb4don{Rs}
  {Ye}  "The greatest asset of a modern investigator is not a magnifying glass,                    
                   but an internet connection." - Unknown{Rs}

  {Wh}{'─'*55}{Rs}
""")
    stderr.write(option_text())
    stderr.write(f"\n  {Wh}{'─'*55}{Rs}\n")

def main():
    clear()
    option()
    time.sleep(0.2)
    try:
        opt = int(input(f"\n  {Wh}[ + ] {Gr}Select Option : {Wh}"))
        if not is_in_options(opt):
            print(f"{Re}  [!] Invalid option. Please choose from menu.{Rs}")
            time.sleep(1.5)
            main()
            return
        execute_option(opt)
    except ValueError:
        print(f"\n  {Re}[!] Please enter a number.{Rs}")
        time.sleep(1.5)
        main()
    except KeyboardInterrupt:
        print(f"\n  {Re}[!] Exit{Rs}")
        time.sleep(1)
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n  {Re}[!] Exit{Rs}")
        time.sleep(1)
        sys.exit(0)

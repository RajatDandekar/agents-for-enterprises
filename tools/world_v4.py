"""v4 world rename: Rasoi Steel Works (Pune, cookers, INR, GST) -> Northbridge Cycles (Manchester, e-bikes, GBP, VAT).

    python3 tools/world_v4.py PATH [PATH ...]          # rewrite text files in place, print a count per file
    python3 tools/world_v4.py --check PATH [PATH ...]  # list leftovers of the old world, change nothing

The same map is used for every lecture as it is rebuilt, so names stay consistent across the course. Numbers are
NOT rescaled here (battery quantities are a tenth of the gasket ones and rates ten times higher, so order values
match; VAT is 20%, not 18%): seed data and prose with numbers are edited by hand. See WORLD_V4.md.
Recorded model replies (cassettes) are keyed by a hash of the request, so a renamed run must be re-recorded.
"""
import pathlib
import re
import sys

# Ordered: longer and more specific strings first. (old, new, word_boundary)
MAP = [
    # ERP and package
    ("Bahi ERP", "Ledgerline ERP", 0), ("BahiError", "LedgerlineError", 0), ("svc@bahi", "svc@ledger", 0),
    ("bahi-erp", "ledgerline-erp", 0), ("BAHI_", "LEDGER_", 0), ("Bahi", "Ledgerline", 0), ("BAHI", "LEDGERLINE", 0),
    ("bahi", "ledgerline", 0),
    # company, app, places
    ("Rasoi Steel Works", "Northbridge Cycles", 0), ("rasoisteel", "northbridgecycles", 0),
    ("rasoi-experience", "northbridge-experience", 0), ("RASOI", "NORTHBRIDGE", 0), ("Rasoi", "Northbridge", 0),
    ("rasoi", "northbridge", 0),
    ("RSW-PUN-01", "NBC-MAN-01", 0), ("RSW-CHK-01", "NBC-LDS-01", 0), ("RSW", "NBC", 1),
    ("WH-PUN-STR", "WH-MAN-STR", 0), ("WH-CHK-STR", "WH-LDS-STR", 0),
    ("Pune main stores", "Manchester main stores", 0), ("Chakan stores", "Leeds stores", 0),
    ("Pune plant", "Manchester plant", 0), ("Chakan unit", "Leeds unit", 0),
    ("Pune", "Manchester", 1), ("PUNE", "MANCHESTER", 1), ("Chakan", "Leeds", 1), ("Bhosari", "Salford", 1),
    ("Rajkot", "Eindhoven", 1), ("Ahmedabad", "Rotterdam", 1), ("Mumbai", "Birmingham", 1), ("MUMBAI", "BIRMINGHAM", 1),
    ("Kolkata", "Gdańsk", 1), ("Vadodara", "Lyon", 1), ("Gujarat", "the Netherlands", 1),
    ("Maharashtra", "England", 1),
    # people (pronouns match: Emma she, Daniel he, Luis he, Henrik he, Aiko she)
    ("Kavita Joshi", "Emma Clarke", 0), ("KJOSHI", "ECLARKE", 0), ("Kavita", "Emma", 1), ("kavita", "emma", 1),
    ("Joshi", "Clarke", 1), ("joshi", "clarke", 1),
    ("Rohit Mehta", "Daniel Okafor", 0), ("RMEHTA", "DOKAFOR", 0), ("Rohit", "Daniel", 1), ("rohit", "daniel", 1),
    ("Mehta", "Okafor", 1), ("mehta", "okafor", 1),
    ("Suresh Kulkarni", "Luis Moreno", 0), ("SKULKARNI", "LMORENO", 0), ("Suresh", "Luis", 1), ("suresh", "luis", 1),
    ("Kulkarni", "Moreno", 1), ("kulkarni", "moreno", 1),
    ("Anand Patil", "Henrik Weber", 0), ("APATIL", "HWEBER", 0), ("Anand", "Henrik", 1), ("anand", "henrik", 1),
    ("Patil", "Weber", 1), ("patil", "weber", 1),
    ("Neha Desai", "Aiko Tanaka", 0), ("NDESAI", "ATANAKA", 0), ("Neha", "Aiko", 1), ("neha", "aiko", 1),
    ("Desai", "Tanaka", 1), ("desai", "tanaka", 1),
    # suppliers
    ("Deccan Paints & Inks", "Voltway Paints & Coatings", 0), ("Deccan Paints", "Voltway Paints", 0),
    ("Deccan Polymers", "Voltway Cells", 0), ("DECCAN", "VOLTWAY", 0), ("Deccan", "Voltway", 0), ("deccan", "voltway", 0),
    ("DP-RJK-0042", "VC-EIN-0042", 0), ("DP-RJK-0009", "VC-EIN-0009", 0), ("DPI-AMD-0107", "VPC-ROT-0107", 0),
    ("DP-RJK", "VC-EIN", 0),
    ("Sahyadri Valves", "Pennine Brakes", 0), ("SV-PUN-0017", "PB-MAN-0017", 0), ("Sahyadri", "Pennine", 1),
    ("Om Sheet Metals", "Castlefield Chargers", 0), ("OSM-PUN-0031", "CC-SAL-0031", 0),
    ("Mahalaxmi Steels", "Albion Motors", 0), ("MS-MUM-0008", "AM-BIR-0008", 0), ("Mahalaxmi", "Albion", 1),
    ("Shree Packaging", "Irwell Packaging", 0), ("SP-PUN-0055", "IP-MAN-0055", 0), ("Shree", "Irwell", 1),
    ("Kaveri Rubber Products", "Nordic Cell Co.", 0), ("Kaveri Rubber", "Nordic Cell", 0), ("KR-KOL-0063", "NC-GDA-0063", 0),
    ("Kaveri", "Nordic Cell", 1), ("kaveri", "nordic_cell", 1),
    ("Shakti Seals", "Brightcell Energy", 0), ("SHAKTI", "BRIGHTCELL", 0), ("Shakti", "Brightcell", 1),
    ("shakti", "brightcell", 1),
    # items (codes, then descriptions, then words)
    ("GSK-SIL-05L-R", "BAT-500-R", 0), ("GSK-SIL-05L", "BAT-500", 0), ("GSK-RUB-05L", "BAT-400-OLD", 0),
    ("GSK-SIL-03L", "BAT-375", 0), ("GSK-SIL-07L", "BAT-750", 0), ("GSK", "BAT", 1),
    ("Gasket, silicone, 5 L (rework)", "Battery pack, 36 V 500 Wh (refurbished)", 0),
    ("Gasket, silicone, 5 L", "Battery pack, 36 V 500 Wh", 0), ("Gasket, rubber, 5 L", "Battery pack, 36 V 400 Wh (old model)", 0),
    ("Gasket, silicone, 3 L", "Battery pack, 36 V 375 Wh", 0), ("Gasket, silicone, 7.5 L", "Battery pack, 48 V 750 Wh", 0),
    ("HDL-BKL-01", "GRP-ERG-01", 0), ("HDL-BKL-02", "GRP-ERG-02", 0),
    ("Handle, bakelite, long", "Grip, ergonomic, long", 0), ("Handle, bakelite, short", "Grip, ergonomic, short", 0),
    ("WHS-STD-01", "BEL-STD-01", 0), ("Whistle (weight valve), standard", "Bell, standard", 0),
    ("SVL-STD-01", "BRK-PAD-01", 0), ("Safety valve, standard", "Brake pads, disc (pair)", 0),
    ("SS-CIR-05L", "MTR-HUB-250", 0), ("Steel circle, 5 L body blank", "Hub motor, 250 W", 0),
    ("LID-SS-05L", "CHG-4A-01", 0), ("Lid, stainless steel, 5 L", "Charger, 4 A", 0),
    ("BOX-CRG-05L", "BOX-BIKE-01", 0), ("Carton, corrugated, 5 L", "Carton, bike shipping", 0),
    ("silicone gaskets", "battery packs", 0), ("silicone gasket", "battery pack", 0),
    ("Gaskets", "Battery packs", 0), ("gaskets", "battery packs", 0), ("GASKETS", "BATTERY PACKS", 0),
    ("Gasket", "Battery pack", 0), ("gasket", "battery pack", 0), ("GASKET", "BATTERY PACK", 0),
    ("bakelite handles", "ergonomic grips", 0), ("bakelite", "ergonomic", 0),
    ("whistles", "bells", 1), ("safety valves", "brake pads", 1), ("steel circles", "hub motors", 1),
    ("pressure-cooker maker", "e-bike maker", 0), ("pressure-cooker", "e-bike", 0), ("pressure cookers", "e-bikes", 0),
    ("pressure cooker", "e-bike", 0), ("Cookers", "E-bikes", 1), ("cookers", "e-bikes", 1), ("cooker", "e-bike", 1),
    ("5-litre line, regular production", "City e-bike line, regular production", 0), ("5-litre", "city e-bike", 0),
    ("3-litre line", "Cargo e-bike line", 0), ("3-litre", "cargo e-bike", 0),
    ("Diwali production run", "Spring launch run", 0), ("before Diwali", "before the spring launch", 0),
    ("the Diwali", "the spring-launch", 0), ("Diwali", "spring-launch", 0), ("diwali", "spring_launch", 0),
    # certification rule (§6.2)
    ("food-grade certificate", "UN 38.3 certificate", 0), ("Food-grade certificate", "UN 38.3 certificate", 0),
    ("food-grade cert", "UN 38.3 cert", 0), ("FOOD-GRADE", "UN38.3", 0), ("FOOD_GRADE", "UN38_3", 0),
    ("Food-grade", "Battery-safety", 0), ("food-grade", "battery-safety", 0), ("food_grade", "cell_safety", 0),
    ("Food grade", "Battery safety", 0), ("food grade", "battery safety", 0),
    ("food_contact", "cell_safety", 0), ("Food-contact", "Lithium-cell", 0), ("food-contact", "lithium-cell", 0),
    ("food contact", "lithium cells", 0), ("FSSAI-LAB", "UN38.3-TR", 0), ("FSSAI", "UN 38.3", 0), ("BIS-SS304", "UN38.3-TR", 0),
    # tax and money
    ("GST18-INTRA", "VAT20-UK", 0), ("GST18-INTER", "VAT20-RC", 0), ("GST12-INTRA", "VAT5-UK", 0), ("GST12-INTER", "VAT5-RC", 0),
    ("CGST 9% + SGST 9% (same state)", "VAT 20% (UK supplier)", 0), ("IGST 18% (other state)", "VAT 20%, reverse charge (overseas supplier)", 0),
    ("CGST 6% + SGST 6% (same state)", "VAT 5% (UK supplier)", 0), ("IGST 12% (other state)", "VAT 5%, reverse charge (overseas supplier)", 0),
    ("TAX REGION DOES NOT MATCH SUPPLIER STATE", "TAX CODE DOES NOT MATCH SUPPLIER COUNTRY", 0),
    ("STATE CD (2)", "COUNTRY CD (2)", 0), ("GSTIN ALREADY REGISTERED", "VAT NO ALREADY REGISTERED", 0),
    ("GSTIN", "VAT number", 0), ("gstin", "vat_no", 0), ("18% GST", "20% VAT", 0), ("GST", "VAT", 1),
    ("₹", "£", 0), ("en-IN", "en-GB", 0), ("+05:30", "+00:00", 0), ("IST", "GMT", 1),
]

OLD_WORDS = ["Rasoi", "Kavita", "Rohit", "Neha", "Suresh", "Anand", "Deccan", "Sahyadri", "Mahalaxmi", "Kaveri",
             "Shakti", "Pune", "Chakan", "Diwali", "gasket", "cooker", "Bahi", "bahi", "GST", "₹", "lakh", "crore",
             "IST", "FSSAI", "India", "Rs.", "INR"]
TEXT = {".py", ".md", ".json", ".jsonl", ".js", ".html", ".css", ".txt", ".yaml", ".yml", ".toml", ".sh", ".ipynb",
        ".csv", ".sql", ".env", ".cfg", ".ini", ""}
SKIP = {"cassettes", "__pycache__", ".git", "qa", "node_modules", "shots", "archive", "site-dist", ".venv"}


def _rx(old, wb):
    return re.compile((r"(?<![A-Za-z0-9_])" + re.escape(old) + r"(?![A-Za-z0-9_])") if wb else re.escape(old))


RULES = [(_rx(o, wb), n) for o, n, wb in MAP]


def convert(text):
    n = 0
    for rx, new in RULES:
        text, k = rx.subn(new, text)
        n += k
    return text, n


def files(paths):
    for p in map(pathlib.Path, paths):
        if p.is_file():
            yield p
            continue
        for f in sorted(p.rglob("*")):
            if f.is_file() and not (SKIP & set(f.parts)) and f.suffix in TEXT:
                yield f


def main(argv):
    check = argv[:1] == ["--check"]
    paths = argv[1:] if check else argv
    total = 0
    for f in files(paths):
        try:
            s = f.read_text()
        except UnicodeDecodeError:
            continue
        if check:
            hits = [w for w in OLD_WORDS if _rx(w, w.isalpha()).search(s)]
            if hits:
                print(f"{f}: {', '.join(hits)}")
            continue
        t, n = convert(s)
        if n:
            f.write_text(t)
            total += n
            print(f"{n:6d}  {f}")
    if not check:
        print(f"{total} replacements")


if __name__ == "__main__":
    main(sys.argv[1:])

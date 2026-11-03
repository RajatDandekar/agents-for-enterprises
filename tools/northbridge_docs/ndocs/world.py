"""Master data for the Northbridge documentation dump.

Every record that exists in ledgerline/erp/seed.py is copied from it unchanged (imported, never retyped).
Everything else is invented here from fixed seeds, so the dump is the same on every run.
"""
from __future__ import annotations

import datetime as dt
import random
import unicodedata

from ledgerline.erp import seed as S

TODAY = S.TODAY  # 2026-10-26


def rng(name: str) -> random.Random:
    return random.Random(f"northbridge-docs/{name}")


def ascii3(city: str) -> str:
    a = unicodedata.normalize("NFKD", city).encode("ascii", "ignore").decode()
    a = a.replace("ł", "l").replace("Ł", "L")
    return a[:3].upper()


def d(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


# ------------------------------------------------------------------------------------------------ people
SEED_USERS = {u[0]: u for u in S.USERS}

# user_id, name, role, ou, limit, manager, default cc, title (extra staff; never in the sandbox)
EXTRA_PEOPLE = [
    ("GWHITAKER", "Grace Whitaker", "FIN-CTRL", "NBC-MAN-01", 0, "HWEBER", "ADM-01", "Financial controller"),
    ("MKOWALSKI", "Marta Kowalski", "AP-MGR", "NBC-MAN-01", 0, "GWHITAKER", "FIN-01", "Accounts payable manager"),
    ("TASHWORTH", "Tom Ashworth", "AP-CLERK", "NBC-MAN-01", 0, "MKOWALSKI", "FIN-01", "Accounts payable clerk"),
    ("RPRYCE", "Rhys Pryce", "IT-MGR", "NBC-MAN-01", 0, "HWEBER", "IT-01", "IT manager"),
    ("JFLETCHER", "Joanna Fletcher", "IT-ADMIN", "NBC-MAN-01", 0, "RPRYCE", "IT-01", "Ledgerline key user and administrator"),
    ("PJANSEN", "Pieter Jansen", "QA-MGR", "NBC-MAN-01", 0, "HWEBER", "QA-01", "Quality manager"),
    ("CBARNES", "Chloe Barnes", "QA-INSP", "NBC-MAN-01", 0, "PJANSEN", "QA-01", "Incoming inspector"),
    ("CSHAW", "Callum Shaw", "STORES-MGR", "NBC-MAN-01", 0, "HWEBER", "LOG-01", "Stores manager"),
    ("NDOYLE", "Niamh Doyle", "STORES", "NBC-LDS-01", 0, "CSHAW", "LDS-LOG-01", "Stores, Leeds unit"),
    ("SLINDQVIST", "Sofia Lindqvist", "HR-MGR", "NBC-MAN-01", 0, "HWEBER", "HR-01", "HR manager"),
    ("OLLOYD", "Owen Lloyd", "HR-ADV", "NBC-MAN-01", 0, "SLINDQVIST", "HR-01", "HR adviser"),
    ("IMORGAN", "Isla Morgan", "SAL-MGR", "NBC-MAN-01", 0, "HWEBER", "SAL-01", "Sales manager, UK and Europe"),
    ("SBERG", "Stefan Berg", "PRD-PLAN", "NBC-MAN-01", 0, "HWEBER", "PRD-07", "Production planner"),
    ("BPRICE", "Bronwen Price", "PLANT-HEAD", "NBC-LDS-01", 5000000, None, "LDS-ADM-01", "Head of the Leeds unit"),
    ("KMENSAH", "Kwame Mensah", "PUR-EXEC", "NBC-MAN-01", 250000, "DOKAFOR", "PRD-03", "Purchase executive"),
    ("HNAKAMURA", "Hana Nakamura", "PUR-EXEC", "NBC-LDS-01", 250000, "DOKAFOR", "LDS-PRD-01", "Purchase executive, Leeds"),
    ("ECHEN", "Ethan Chen", "SAL-EXEC", "NBC-MAN-01", 0, "IMORGAN", "SAL-01", "Sales executive"),
]
MD_NAME = "Catherine Holt"  # Managing Director; approves above £5,000,000 outside Ledgerline
FIRST = ["Oliver", "Charlotte", "Harry", "Amelia", "Jack", "Freya", "Noah", "Grace", "Thomas", "Lucy", "William",
         "Ella", "Samuel", "Megan", "Joseph", "Hannah", "Benjamin", "Zoe", "Lewis", "Callum", "Rhian", "Declan",
         "Piotr", "Katarzyna", "Lukas", "Sanne", "Mathieu", "Elena", "Marco", "Giulia", "Carlos", "Lucia", "Joao",
         "Ines", "Ama", "Chidi", "Ngozi", "Yusuf", "Leila", "Mei", "Hiroshi", "Yuki", "Minh", "Linh", "Nadia",
         "Ingrid", "Erik", "Astrid", "Aisling", "Eamon", "Bronagh", "Gareth", "Alys", "Fergus", "Mairi"]
LAST = ["Hughes", "Bennett", "Walsh", "Kowalczyk", "Nowicki", "Visser", "Fischer", "Schmidt", "Rossi", "Bianchi",
        "Garcia", "Silva", "Owusu", "Adeyemi", "Sato", "Nguyen", "Lin", "Berglund", "Murphy", "Kelly", "Evans",
        "Morgan", "Lloyd-Jones", "Shaw", "Barnes", "Holt", "Fletcher", "Brennan", "Whitworth", "Cartwright",
        "Thornton", "Haworth", "Sutcliffe", "Pickering", "Ramsbottom", "Hollis", "Pryor", "Ainsworth", "Dunne"]
ROLE_TITLES = {"PUR-EXEC": "Purchase executive", "PUR-SR": "Senior buyer", "PUR-MGR": "Purchase manager",
               "PLANT-HEAD": "Plant head", "STORES": "Stores", "SYS-ADMIN": "Integration service account",
               "STORES-MGR": "Stores manager", "AP-CLERK": "Accounts payable clerk", "AP-MGR": "Accounts payable manager",
               "FIN-CTRL": "Financial controller", "SAL-EXEC": "Sales executive", "SAL-MGR": "Sales manager",
               "PRD-PLAN": "Production planner", "PRD-SUP": "Production supervisor", "QA-INSP": "Quality inspector",
               "QA-MGR": "Quality manager", "HR-ADV": "HR adviser", "HR-MGR": "HR manager", "IT-ADMIN": "IT administrator",
               "IT-MGR": "IT manager", "MNT-TECH": "Maintenance technician"}
ROLE_LIMIT = {"PUR-EXEC": 250000, "PUR-SR": 500000, "PUR-MGR": 1000000, "PLANT-HEAD": 5000000}


def users():
    """All Ledgerline users: the six seed users exactly, then the rest of the company."""
    out = []
    for u in S.USERS:
        uid, name, role, ou, lim, mgr, _pw, cc, email, _slack = u
        out.append(dict(user_id=uid, name=name, role_cd=role, ou_cd=ou, appr_limit=lim, manager_id=mgr,
                        default_cc=cc, email=email, title=ROLE_TITLES.get(role, role), status="ACTIVE"))
    for uid, name, role, ou, lim, mgr, cc, title in EXTRA_PEOPLE:
        out.append(dict(user_id=uid, name=name, role_cd=role, ou_cd=ou, appr_limit=lim, manager_id=mgr,
                        default_cc=cc, email=name.lower().replace(" ", ".") + "@northbridgecycles.example",
                        title=title, status="ACTIVE"))
    r = rng("users")
    taken = {u["user_id"] for u in out}
    roles = (["STORES"] * 14 + ["PRD-SUP"] * 16 + ["QA-INSP"] * 6 + ["SAL-EXEC"] * 14 + ["AP-CLERK"] * 5 +
             ["MNT-TECH"] * 10 + ["PRD-PLAN"] * 4 + ["IT-ADMIN"] * 2 + ["HR-ADV"] * 2 + ["PUR-EXEC"] * 3 + ["PUR-SR"])
    mgr_for = {"STORES": "CSHAW", "PRD-SUP": "SBERG", "QA-INSP": "PJANSEN", "SAL-EXEC": "IMORGAN", "AP-CLERK": "MKOWALSKI",
               "MNT-TECH": "HWEBER", "PRD-PLAN": "HWEBER", "IT-ADMIN": "RPRYCE", "HR-ADV": "SLINDQVIST",
               "PUR-EXEC": "DOKAFOR", "PUR-SR": "DOKAFOR"}
    cc_for = {"STORES": "LOG-01", "PRD-SUP": "PRD-07", "QA-INSP": "QA-01", "SAL-EXEC": "SAL-01", "AP-CLERK": "FIN-01",
              "MNT-TECH": "MNT-01", "PRD-PLAN": "PRD-07", "IT-ADMIN": "IT-01", "HR-ADV": "HR-01", "PUR-EXEC": "PRD-03",
              "PUR-SR": "PRD-03"}
    for role in roles:
        while True:
            fn, ln = r.choice(FIRST), r.choice(LAST)
            uid = (fn[0] + ln.replace("-", "")).upper()[:10]
            if uid not in taken:
                break
        taken.add(uid)
        ou = "NBC-LDS-01" if r.random() < 0.3 else "NBC-MAN-01"
        st = "ACTIVE" if r.random() > 0.08 else "LOCKED"
        out.append(dict(user_id=uid, name=f"{fn} {ln}", role_cd=role, ou_cd=ou, appr_limit=ROLE_LIMIT.get(role, 0),
                        manager_id=mgr_for[role], default_cc=cc_for[role],
                        email=f"{fn}.{ln}".lower().replace("-", "") + "@northbridgecycles.example",
                        title=ROLE_TITLES[role], status=st))
    # leavers kept on file, the way old ERPs do
    for uid, name, role, left in [("GSUTCLIFFE", "Graham Sutcliffe", "PUR-MGR", "2019-03-31"),
                                  ("DRAMSDEN", "Derek Ramsden", "IT-MGR", "2012-06-30"),
                                  ("PURCH01", "Purchasing shared login (1998)", "PUR-EXEC", "2009-01-31"),
                                  ("EDI_GW", "EDI gateway account (6.x)", "SYS-ADMIN", "2015-03-31")]:
        out.append(dict(user_id=uid, name=name, role_cd=role, ou_cd="NBC-MAN-01", appr_limit=0, manager_id=None,
                        default_cc="ADM-01", email="", title=f"left {left}", status="DISABLED"))
    return out


# ------------------------------------------------------------------------------------------------ items
# item families: prefix, category, uom, cell_safety, description builder
SEED_ITEM_CODES = {i[0] for i in S.ITEMS}


def items():
    """Item master: the 12 seed items exactly (first), then about 2,400 more."""
    out = []
    r = rng("items")
    legacy_n = [104200]

    def legacy():
        legacy_n[0] += r.randint(1, 37)
        return f"NB{legacy_n[0]:06d}"

    for itm_cd, descr, uom, cs, cat, act, rol, adi in S.ITEMS:
        out.append(dict(itm_cd=itm_cd, descr=descr, uom_cd=uom, cell_safety=cs, category=cat, active=act,
                        reorder_lvl=rol, avg_daily_issue=adi, legacy_cd=legacy(), hs_code=_hs(itm_cd),
                        un_no="UN3480" if itm_cd.startswith("BAT") else "", buyer="LMORENO" if cs else "ECLARKE",
                        lead_days=42 if itm_cd.startswith("BAT") else 21, abc="A" if adi >= 600 or cs else "B",
                        std_cost=None, created_on="2019-04-01", notes=""))
    seen = set(SEED_ITEM_CODES)

    def add(code, descr, uom, cs, cat, rol=None, adi=None, active=1, notes="", buyer=None, lead=None, un=""):
        if code in seen:
            return
        seen.add(code)
        a = adi if adi is not None else r.choice([0, 0, 5, 10, 20, 40, 80, 120, 250, 400, 900])
        out.append(dict(itm_cd=code, descr=descr, uom_cd=uom, cell_safety=cs, category=cat, active=active,
                        reorder_lvl=rol if rol is not None else a * r.choice([5, 7, 10, 14]), avg_daily_issue=a,
                        legacy_cd=legacy() if r.random() < 0.7 else "", hs_code=_hs(code), un_no=un,
                        buyer=buyer or r.choice(["ECLARKE", "LMORENO", "KMENSAH", "HNAKAMURA"]),
                        lead_days=lead or r.choice([7, 10, 14, 21, 28, 42, 56]),
                        abc=r.choice("ABCC"), std_cost=None,
                        created_on=f"{r.randint(1999, 2026)}-{r.randint(1, 12):02d}-{r.randint(1, 28):02d}",
                        notes=notes))

    # batteries and other lithium-cell parts (cell_safety = 1)
    for code, v, wh in [("BAT-250", 36, 250), ("BAT-300", 36, 300), ("BAT-418", 36, 418), ("BAT-625", 36, 625),
                        ("BAT-720", 36, 720), ("BAT-500-48", 48, 500), ("BAT-625-48", 48, 625), ("BAT-960-48", 48, 960)]:
        add(code, f"Battery pack, {v} V {wh} Wh", "NOS", 1, "SPARES", un="UN3480", lead=42, buyer="LMORENO")
    add("BAT-625-INT", "Battery pack, 36 V 625 Wh, in-tube", "NOS", 1, "SPARES", un="UN3480", lead=42, buyer="LMORENO")
    add("BAT-RNG-250", "Range extender battery, 36 V 250 Wh", "NOS", 1, "SPARES", un="UN3480", buyer="LMORENO")
    add("BAT-300-OLD", "Battery pack, 36 V 300 Wh (2014 model)", "NOS", 1, "SPARES", active=0, adi=0, rol=0,
        notes="superseded by BAT-375")
    add("BAT-CEL-21700", "Lithium-ion cell, 21700, 4.8 Ah (service spares)", "NOS", 1, "SPARES", un="UN3480",
        buyer="LMORENO", notes="Quality use only")
    add("BAT-BMS-36", "Battery management board, 36 V", "NOS", 0, "COMPONENTS",
        notes="no cells: not lithium-cell")
    for w in [250, 350, 500]:
        for kind, nm in [("HUB", "Hub motor"), ("RHB", "Rear hub motor"), ("MID", "Mid-drive motor")]:
            add(f"MTR-{kind}-{w}", f"{nm}, {w} W", "NOS", 1, "RAW", lead=56, buyer="LMORENO")
    for a in ["2A", "3A", "4A", "5A", "6A"]:
        for n in ["01", "02"]:
            add(f"CHG-{a}-{n}", f"Charger, {a[:-1]} A" + (", fast" if n == "02" else ""), "NOS", 1, "COMPONENTS",
                buyer="LMORENO")
    add("CHG-4A-UK", "Charger, 4 A, UK plug (old code)", "NOS", 1, "COMPONENTS", active=0, adi=0, rol=0,
        notes="use CHG-4A-01")
    for n, (d_, cs) in enumerate([("Display, LCD, monochrome", 0), ("Display, colour TFT with coin cell", 1),
                                  ("Display, LED bar", 0), ("Display, colour TFT", 0)], 1):
        add(f"DSP-{n:02d}", d_, "NOS", cs, "COMPONENTS", notes="coin cell: lithium-cell flag set by Quality" if cs else "")
    for n, d_ in enumerate(["Controller, 36 V 15 A", "Controller, 36 V 18 A", "Controller, 48 V 20 A",
                            "Controller, 36 V 15 A, waterproof"], 1):
        add(f"CTL-{n:02d}", d_, "NOS", 0, "COMPONENTS")
    # the rest of the bike
    for b in ["MNT-FRM-02", "MNT-FRM-03", "MNT-RCK-01", "MNT-RCK-03"]:
        add(b, "Battery mount, " + ("down-tube" if "FRM" in b else "rear rack") + f", type {b[-1]}", "NOS", 0, "COMPONENTS")
    models = [("ANC", "Ancoats city"), ("DEA", "Deansgate step-through"), ("MED", "Medlock trekking"),
              ("IRK", "Irk cargo"), ("TAM", "Tame folding"), ("ROC", "Roch mountain"), ("SPR", "Medlock 2 (spring launch)")]
    sizes, colours = ["S", "M", "L", "XL"], [("BLK", "black"), ("GRN", "racing green"), ("SLV", "silver"),
                                             ("RED", "brick red"), ("BLU", "canal blue")]
    for mc, mn in models:
        for s in sizes:
            for cc, cn in colours:
                add(f"FRM-{mc}-{s}-{cc}", f"Frame, {mn}, size {s}, {cn}", "NOS", 0, "RAW", lead=70)
    for size in ["20", "24", "26", "27.5", "28", "29"]:
        for t, tn in [("CTY", "city"), ("TRK", "trekking"), ("MTB", "off-road"), ("PCT", "puncture-resistant")]:
            for w in ["1.75", "2.0", "2.25"]:
                add(f"TYR-{size}-{t}-{w}", f"Tyre, {size} in x {w}, {tn}", "NOS", 0, "COMPONENTS")
        add(f"TUB-{size}", f"Inner tube, {size} in", "NOS", 0, "COMPONENTS")
        for rt in ["AL", "AL-DW"]:
            add(f"RIM-{size}-{rt}", f"Rim, {size} in, aluminium" + (", double-wall" if rt == "AL-DW" else ""), "NOS", 0, "RAW")
    for g in ["14G", "13G"]:
        for ln in range(254, 306, 2):
            add(f"SPK-{g}-{ln}", f"Spoke, {g}, {ln} mm, stainless", "NOS", 0, "COMPONENTS", adi=r.choice([0, 200, 900]))
    for kind, nm in [("PAD", "Brake pads, disc (pair)"), ("ROT", "Brake rotor"), ("CAL", "Brake caliper, hydraulic"),
                     ("LEV", "Brake lever"), ("HOS", "Brake hose")]:
        for spec in ["160", "180", "203"] if kind in ("ROT", "HOS") else ["01", "02", "03"]:
            code = f"BRK-{kind}-{spec}"
            if code == "BRK-PAD-01":
                continue
            add(code, f"{nm}, {spec} mm" if kind in ("ROT", "HOS") else f"{nm}, type {spec[-1]}", "NOS", 0, "COMPONENTS")
    for sp in [8, 9, 10, 11]:
        add(f"CHN-{sp}S", f"Chain, {sp}-speed", "NOS", 0, "COMPONENTS")
        add(f"CST-{sp}S-1136", f"Cassette, {sp}-speed, 11-36", "NOS", 0, "COMPONENTS")
        add(f"DRL-{sp}S", f"Rear derailleur, {sp}-speed", "NOS", 0, "COMPONENTS")
        add(f"SHF-{sp}S", f"Shifter, {sp}-speed", "NOS", 0, "COMPONENTS")
    for nm, code in [("Belt drive, 118T", "BLT-118"), ("Belt drive, 122T", "BLT-122"), ("Hub gear, 5-speed", "HGR-5S"),
                     ("Hub gear, 8-speed", "HGR-8S"), ("Chainring, 38T", "CRG-38"), ("Chainring, 42T", "CRG-42"),
                     ("Crankset, 170 mm", "CRK-170"), ("Crankset, 175 mm", "CRK-175"), ("Bottom bracket, sealed", "BBR-01"),
                     ("Pedals, platform (pair)", "PDL-01"), ("Pedals, folding (pair)", "PDL-02")]:
        add(code, nm, "NOS" if "Pedals" not in nm else "PR", 0, "COMPONENTS")
    for w in [580, 620, 680, 720]:
        for kind, nm in [("FLT", "flat"), ("RIS", "riser"), ("SWP", "swept-back")]:
            add(f"HBR-{kind}-{w}", f"Handlebar, {nm}, {w} mm", "NOS", 0, "COMPONENTS")
    for ln in [60, 70, 80, 90, 100]:
        add(f"STM-{ln}", f"Stem, {ln} mm", "NOS", 0, "COMPONENTS")
    for c in ["01", "02", "03"]:
        add(f"GRP-ERG-{c}", f"Grip, ergonomic, type {c[-1]}", "PR", 0, "COMPONENTS")
        add(f"SDL-{c}", f"Saddle, {['comfort', 'sport', 'cargo'][int(c) - 1]}", "NOS", 0, "COMPONENTS")
        add(f"SPT-{c}", f"Seat post, {['27.2', '30.9', '31.6'][int(c) - 1]} mm", "NOS", 0, "COMPONENTS")
        add(f"BEL-STD-{int(c) + 1:02d}", f"Bell, {['brass', 'mini', 'ping'][int(c) - 1]}", "NOS", 0, "COMPONENTS")
    for kind, nm in [("FRT", "Front light, 70 lux"), ("FR2", "Front light, 100 lux"), ("REA", "Rear light"),
                     ("REB", "Rear light with brake function"), ("REF", "Reflector set")]:
        add(f"LGT-{kind}", nm, "NOS" if kind != "REF" else "SET", 0, "COMPONENTS")
    for kind, nm in [("MDG", "Mudguard set, 50 mm"), ("MDW", "Mudguard set, 65 mm"), ("RCK", "Rear rack, 25 kg"),
                     ("RCC", "Rear rack, cargo 60 kg"), ("KST", "Kickstand"), ("KS2", "Kickstand, double"),
                     ("CGD", "Chain guard"), ("LCK", "Frame lock"), ("BSK", "Front basket")]:
        add(f"ACC-{kind}", nm, "SET" if kind.startswith("M") else "NOS", 0, "COMPONENTS")
    for c, nm in [("MTR", "Motor cable, 1,200 mm"), ("DSP", "Display cable"), ("BRK", "Brake cable, inner"),
                  ("SHF", "Gear cable, inner"), ("HSG", "Cable housing"), ("SNS", "Speed sensor with cable"),
                  ("TRQ", "Torque sensor"), ("LGT", "Light cable")]:
        for n in ["01", "02"]:
            add(f"CBL-{c}-{n}", nm + (", long" if n == "02" else ""), "NOS" if c != "HSG" else "MTR", 0, "COMPONENTS")
    for kind, nm in [("BLT", "Bolt, hex socket"), ("SCR", "Screw, pan head"), ("NUT", "Nut, nyloc"), ("WSH", "Washer")]:
        for m in ["M3", "M4", "M5", "M6", "M8", "M10"]:
            for ln in (["6", "8", "10", "12", "16", "20", "25", "30", "35", "40"] if kind in ("BLT", "SCR") else ["-"]):
                for fin, fn in [("ZN", "zinc"), ("SS", "stainless"), ("BK", "black oxide")]:
                    code = f"FST-{kind}-{m}{'' if ln == '-' else 'X' + ln}-{fin}"
                    add(code, f"{nm}, {m}{'' if ln == '-' else ' x ' + ln + ' mm'}, {fn}", "NOS", 0, "RAW",
                        adi=r.choice([0, 100, 400, 1200, 3000]))
    for kind, nm in [("PNT", "Powder coat"), ("LAC", "Clear lacquer"), ("PRM", "Primer")]:
        for cc, cn in colours + [("WHT", "white"), ("GRY", "graphite")]:
            add(f"{kind}-{cc}", f"{nm}, {cn}", "KG", 0, "RAW")
    for code, nm in [("BOX-BIKE-02", "Carton, bike shipping, cargo"), ("BOX-BIKE-03", "Carton, folding bike"),
                     ("BOX-BAT-01", "Carton, battery pack, UN-rated"), ("BOX-BAT-02", "Carton, battery pack, overpack"),
                     ("BOX-PRT-01", "Carton, spare parts, small"), ("BOX-PRT-02", "Carton, spare parts, large"),
                     ("PKG-FOAM-01", "Foam insert, frame"), ("PKG-TAPE-01", "Packing tape"), ("PKG-LBL-UN", "Label, lithium battery handling"),
                     ("PKG-WRAP-01", "Stretch wrap"), ("PKG-PAL-01", "Pallet, 1200 x 1000"), ("PKG-CRN-01", "Corner protector")]:
        add(code, nm, "NOS" if "TAPE" not in code and "WRAP" not in code else "ROL", 0, "PACKING")
    # maintenance, repair and operations spares (MRO): the bulk of a 28-year item master
    machines = ["welding robot", "paint line", "wheel truing machine", "conveyor", "compressor", "forklift",
                "battery test rig", "end-of-line tester", "frame jig", "spoke threader", "shrink tunnel", "label printer"]
    parts = ["belt", "bearing", "filter", "nozzle", "sensor", "fuse", "relay", "contactor", "seal kit", "motor",
             "drive belt", "roller", "spring", "gasket set", "valve", "hose", "encoder", "lamp", "brush", "fan"]
    n = 1
    for m in machines:
        for p in parts:
            for v in ["A", "B", "C", "D"]:
                add(f"MRO-{n:05d}", f"{p.capitalize()}, {m}, type {v}", "NOS", 0, "MRO", adi=0,
                    rol=r.choice([0, 1, 2, 4]), active=0 if r.random() < 0.12 else 1)
                n += 1
    kits = ["front wheel", "rear wheel", "brake service", "drivetrain service", "cable set", "light set", "mudguard",
            "rack", "kickstand", "display mount", "battery lock", "charging port", "saddle clamp", "headset", "fork seal",
            "pedal", "chain guard", "frame plugs", "battery rail", "motor connector", "sensor magnet", "bell", "grip set",
            "bottle cage bolts", "derailleur hanger", "axle nuts", "spoke set", "rim tape", "valve set", "warranty labels"]
    for mc, mn in models:
        for k, kit in enumerate(kits, 1):
            add(f"SPR-{mc}-{k:02d}", f"Service kit, {mn}, {kit}", "SET", 0, "SPARES", adi=r.choice([0, 1, 2, 5]))
    for code, nm, uom in [("CON-GLV-01", "Gloves, nitrile (box)", "BOX"), ("CON-WIP-01", "Wipes, cleaning", "BOX"),
                          ("CON-GRS-01", "Grease, bearing", "KG"), ("CON-THR-01", "Thread locker, medium", "NOS"),
                          ("CON-SLV-01", "Cable ties (bag)", "BAG"), ("CON-ESD-01", "ESD bags (pack)", "PKT")]:
        add(code, nm, uom, 0, "CONSUMABLES")
    # finished goods
    for mc, mn in models:
        for s in sizes:
            for cc, cn in colours:
                add(f"FG-{mc}-{s}-{cc}", f"E-bike, {mn}, size {s}, {cn}", "NOS", 0, "FINISHED", adi=r.choice([10, 20, 40, 80]))
    return out


def _hs(code: str) -> str:
    if code.startswith("BAT"):
        return "8507.60"
    if code.startswith("MTR"):
        return "8501.31"
    if code.startswith("CHG"):
        return "8504.40"
    if code.startswith("FG-"):
        return "8711.60"
    if code.startswith(("FRM", "RIM", "SPK", "BRK", "HBR", "STM", "SPT", "CHN", "CST", "DRL", "SHF", "MNT", "PDL", "CRK")):
        return "8714.99"
    if code.startswith("TYR"):
        return "4011.50"
    return ""


# ------------------------------------------------------------------------------------------------ suppliers
SEED_SUP_CODES = [s[0] for s in S.SUPPLIERS]

PLACES = {"GB": ["Manchester", "Salford", "Bolton", "Oldham", "Stockport", "Rochdale", "Wigan", "Warrington", "Preston",
                 "Blackburn", "Leeds", "Bradford", "Huddersfield", "Halifax", "Wakefield", "Sheffield", "Rotherham",
                 "Birmingham", "Coventry", "Wolverhampton", "Telford", "Nottingham", "Derby", "Leicester", "Glasgow",
                 "Cardiff", "Newport", "Bristol", "Swindon", "Hull", "Sunderland", "Carlisle"],
          "NL": ["Utrecht", "Tilburg", "Zwolle", "Arnhem", "Breda"], "DE": ["Stuttgart", "Nuremberg", "Dortmund", "Leipzig", "Bielefeld"],
          "PL": ["Wrocław", "Poznań", "Łódź", "Katowice"], "FR": ["Lille", "Grenoble", "Nantes"], "CZ": ["Brno", "Ostrava"],
          "PT": ["Porto", "Aveiro", "Águeda"], "IT": ["Treviso", "Bologna", "Vicenza"], "ES": ["Valencia", "Bilbao"],
          "BE": ["Ghent", "Antwerp"], "TW": ["Taichung", "Tainan", "Changhua"], "SE": ["Malmö"], "DK": ["Odense"]}
NAME_A = ["Calder", "Irwell", "Mersey", "Pennine", "Ribble", "Aire", "Wharfe", "Tame", "Medlock", "Severn", "Trent",
          "Humber", "Kinder", "Holme", "Saddleworth", "Bowland", "Lune", "Dove", "Wyre", "Derwent", "Nidd", "Swale",
          "Ure", "Colne", "Etherow", "Goyt", "Bollin", "Weaver", "Dane", "Mardale", "Hebden", "Sowerby", "Ryburn",
          "Northgate", "Millstone", "Ironbridge", "Foundry Lane", "Canalside", "Viaduct", "Quayside", "Brindley",
          "Arkwright", "Pendle", "Rivington", "Winter Hill", "Blackstone", "Greenfield", "Highfield", "Fairfield"]
NAME_B = {"FST": ["Fasteners", "Fixings", "Bolt & Nut"], "TYR": ["Tyre Co.", "Rubber Products", "Wheels"],
          "RIM": ["Wheelworks", "Rims", "Alloy Wheels"], "FRM": ["Frameworks", "Tube & Frame", "Fabrications"],
          "PNT": ["Coatings", "Powder Coating", "Finishes"], "BOX": ["Packaging", "Cartons", "Corrugated"],
          "CBL": ["Cables", "Wiring", "Harness Systems"], "LGT": ["Lighting", "Lamps"], "BRK": ["Brake Systems", "Braking"],
          "CHN": ["Drivetrain", "Transmission", "Gears"], "MRO": ["Engineering Supplies", "Industrial Spares", "Maintenance Supplies"],
          "ACC": ["Accessories", "Cycle Parts"], "CTL": ["Electronics", "Controls"], "SVC": ["Services", "Logistics", "Calibration"]}
SUFFIX = {"GB": ["Ltd", "Ltd", "Limited", "& Sons Ltd", "plc"], "NL": ["B.V."], "DE": ["GmbH"], "PL": ["Sp. z o.o."],
          "FR": ["SAS", "SARL"], "CZ": ["s.r.o."], "PT": ["Lda"], "IT": ["S.r.l."], "ES": ["S.L."], "BE": ["NV"],
          "TW": ["Co., Ltd."], "SE": ["AB"], "DK": ["ApS"]}
# extra suppliers of lithium-cell parts (never of BAT-500: the story's two BAT-500 sources stay Voltway and Nordic Cell)
EXTRA_CELL_SUPPLIERS = [
    ("TES-PLY-0144", "Tamar Energy Storage", "GB", "Plymouth", "N45", "BAT"),
    ("RCS-STU-0151", "Rheinfeld Cell Systems", "DE", "Stuttgart", "N45", "BAT"),
    ("HDM-TAI-0162", "Hsinlu Drive Motors", "TW", "Taichung", "ADV", "MTR"),
    ("ODM-POR-0170", "Ondina Motores", "PT", "Porto", "N60", "MTR"),
    ("KPS-BRN-0177", "Kraj Power Supplies", "CZ", "Brno", "N30", "CHG"),
    ("SCC-BOL-0183", "Saddleworth Charger Co.", "GB", "Bolton", "N30", "CHG"),
]


def vat_no(r, country):
    if country == "GB":
        return f"GB{r.randint(100000000, 999999999)}"
    if country == "NL":
        return f"NL{r.randint(100000000, 999999999)}B01"
    if country == "DE":
        return f"DE{r.randint(100000000, 999999999)}"
    if country == "PL":
        return f"PL{r.randint(1000000000, 9999999999)}"
    if country == "FR":
        return f"FR{r.randint(10, 99)}{r.randint(100000000, 999999999)}"
    if country == "CZ":
        return f"CZ{r.randint(10000000, 99999999)}"
    if country == "PT":
        return f"PT{r.randint(100000000, 999999999)}"
    if country == "IT":
        return f"IT{r.randint(10000000000, 99999999999)}"
    if country == "ES":
        return f"ESB{r.randint(1000000, 9999999)}{r.choice('ABCDEFGHJ')}"
    if country == "BE":
        return f"BE0{r.randint(100000000, 999999999)}"
    if country == "SE":
        return f"SE{r.randint(100000000000, 999999999999)}"
    if country == "DK":
        return f"DK{r.randint(10000000, 99999999)}"
    return f"TW{r.randint(10000000, 99999999)}"


def suppliers():
    """Supplier master: the 8 seed suppliers exactly, then about 420 more. Brightcell Energy is never here."""
    out = []
    for sup_cd, name, vat, state, city, status, pt in S.SUPPLIERS:
        out.append(dict(sup_cd=sup_cd, name=name, vat_no=vat, state=state, city=city, status=status, pt_cd=pt,
                        created_by="MIGRATION", created_on="2019-04-01", supplies=_seed_supplies(sup_cd),
                        contact="", email=f"orders@{sup_cd.lower()}.example", notes=""))
    r = rng("suppliers")
    used_vat = {s["vat_no"] for s in out}
    used_names = {s["name"] for s in out}
    n = 110
    for sup_cd, name, state, city, pt, fam in EXTRA_CELL_SUPPLIERS:
        v = vat_no(r, state)
        used_vat.add(v)
        out.append(dict(sup_cd=sup_cd, name=name, vat_no=v, state=state, city=city, status="ACTIVE", pt_cd=pt,
                        created_by=r.choice(["LMORENO", "ECLARKE"]), created_on=f"20{r.randint(20, 25)}-0{r.randint(1, 9)}-1{r.randint(0, 9)}",
                        supplies=fam, contact="", email=f"orders@{sup_cd.lower()}.example", notes=""))
    fams = list(NAME_B)
    weights = [12, 6, 5, 4, 4, 5, 5, 3, 3, 4, 14, 5, 3, 6]
    countries = ["GB"] * 70 + ["NL"] * 5 + ["DE"] * 6 + ["PL"] * 4 + ["FR"] * 3 + ["CZ"] * 2 + ["PT"] * 4 + ["IT"] * 3 + \
                ["ES"] * 2 + ["BE"] * 2 + ["TW"] * 6 + ["SE"] + ["DK"]
    while len(out) < 430:
        fam = r.choices(fams, weights)[0]
        c = r.choice(countries)
        city = r.choice(PLACES[c])
        base = r.choice(NAME_A) if c == "GB" or r.random() < 0.3 else city
        name = f"{base} {r.choice(NAME_B[fam])}"
        if name in used_names or "Bright" in name or "Voltway" in name:
            continue
        used_names.add(name)
        initials = "".join(w[0] for w in name.replace("&", " ").split() if w[0].isalpha())[:3].upper()
        n += r.randint(1, 4)
        sup_cd = f"{initials}-{ascii3(city)}-{n:04d}"
        v = vat_no(r, c)
        if v in used_vat:
            continue
        used_vat.add(v)
        status = "ACTIVE" if r.random() > 0.13 else "BLOCKED"
        yr = r.randint(1998, 2026)
        created_by = "MIGRATION" if yr < 2019 else r.choice(["ECLARKE", "LMORENO", "KMENSAH", "GSUTCLIFFE", "HNAKAMURA"])
        created_on = "2019-04-01" if yr < 2019 else f"{yr}-{r.randint(1, 12):02d}-{r.randint(1, 28):02d}"
        if created_on > TODAY:
            created_on = "2026-09-15"
        out.append(dict(sup_cd=sup_cd, name=f"{name} {r.choice(SUFFIX[c])}" if r.random() < 0.5 else name,
                        vat_no=v if r.random() > 0.04 else "", state=c, city=city, status=status,
                        pt_cd=r.choice(["N30", "N30", "N45", "N60", "EOM30", "N15"] if c != "TW" else ["ADV", "N30"]),
                        created_by=created_by, created_on=created_on, supplies=fam, contact="",
                        email=f"orders@{sup_cd.lower()}.example",
                        notes=r.choice(["", "", "", "replaced by new code", "two failed audits", "debit notes unpaid"]) if status == "BLOCKED" else ""))
    for s in out:
        s["contact"] = SUP_CONTACTS.get(s["sup_cd"], "")
    return out


SUP_CONTACTS = {"VC-EIN-0042": "Femke de Vries", "NC-GDA-0063": "Agnieszka Nowak", "CC-SAL-0031": "Lee Haworth",
                "AM-BIR-0008": "Sam Cartwright", "PB-MAN-0017": "Ben Thornton", "IP-MAN-0055": "Hannah Pickering",
                "VPC-ROT-0107": "Joost Bakker"}


def _seed_supplies(sup_cd):
    return {"VC-EIN-0042": "BAT", "VC-EIN-0009": "BAT", "VPC-ROT-0107": "PNT", "PB-MAN-0017": "BRK", "CC-SAL-0031": "CHG",
            "AM-BIR-0008": "MTR", "IP-MAN-0055": "BOX", "NC-GDA-0063": "BAT"}[sup_cd]


def certificates(sups):
    """Supplier certificates: the 4 seed UN 38.3 rows exactly, then ISO and UN 38.3 rows for other suppliers."""
    out = [dict(sup_cd=a, cert_type=b, doc_ref=c, valid_to=d_, uploaded_by=e, uploaded_on=f, issued_on=_issued(c, f))
           for a, b, c, d_, e, f in S.SUP_CERTS]
    r = rng("certs")
    for s in sups:
        if s["sup_cd"] in SEED_SUP_CODES and s["sup_cd"] not in ("VC-EIN-0042", "PB-MAN-0017", "IP-MAN-0055"):
            continue
        if s["supplies"] in ("BAT", "MTR", "CHG") and s["sup_cd"] not in SEED_SUP_CODES:
            vt = r.choice(["2026-11-30", "2027-02-28", "2027-05-31", "2026-12-15", "2026-08-31", "2027-09-30"])
            iss = (d(vt) - dt.timedelta(days=365)).isoformat()
            out.append(dict(sup_cd=s["sup_cd"], cert_type="UN38.3", doc_ref=f"UN38.3-TR/{s['sup_cd'][:2]}/{iss[:4]}/{r.randint(10, 400):03d}",
                            valid_to=vt, uploaded_by="LMORENO", uploaded_on=iss, issued_on=iss))
        if r.random() < 0.55 or s["sup_cd"] in ("VC-EIN-0042", "PB-MAN-0017", "IP-MAN-0055"):
            vt = f"{r.randint(2025, 2028)}-{r.randint(1, 12):02d}-28"
            out.append(dict(sup_cd=s["sup_cd"], cert_type="ISO-9001", doc_ref=f"ISO9001/{r.randint(10000, 99999)}",
                            valid_to=vt, uploaded_by=r.choice(["LMORENO", "ECLARKE", "PJANSEN"]),
                            uploaded_on=f"{int(vt[:4]) - 3}-{vt[5:7]}-01", issued_on=f"{int(vt[:4]) - 3}-{vt[5:7]}-01"))
        if r.random() < 0.2:
            vt = f"{r.randint(2026, 2029)}-{r.randint(1, 12):02d}-28"
            out.append(dict(sup_cd=s["sup_cd"], cert_type=r.choice(["ISO-14001", "REACH-DECL", "ROHS-DECL"]),
                            doc_ref=f"DOC/{r.randint(1000, 9999)}", valid_to=vt, uploaded_by="PJANSEN",
                            uploaded_on=f"{int(vt[:4]) - 2}-01-15", issued_on=f"{int(vt[:4]) - 2}-01-15"))
    return out


def _issued(doc_ref, uploaded_on):
    # issue dates of the seed certificates (not stored in the sandbox; the test reports carry them)
    return {"UN38.3-TR/VC/2026/118": "2026-03-27", "UN38.3-TR/CC/2026/044": "2026-02-02",
            "UN38.3-TR/AM/2026/301": "2026-06-24", "UN38.3-TR/NC/2025/090": "2025-09-26"}.get(doc_ref, uploaded_on)


def rate_contracts(sups, itms):
    """Rate contracts: the 12 seed rows exactly, their previous periods, then rows for other suppliers' items."""
    out = [dict(sup_cd=a, itm_cd=b, rate=c, valid_from=d_, valid_to=e, contract_no="") for a, b, c, d_, e in S.SUP_RATES]
    prev = {("VC-EIN-0042", "BAT-500"): 109.50, ("VC-EIN-0042", "BAT-375"): 89.00, ("VC-EIN-0042", "BAT-750"): 141.00,
            ("VC-EIN-0042", "MNT-FRM-01"): 17.90, ("VC-EIN-0042", "MNT-RCK-02"): 15.20, ("NC-GDA-0063", "BAT-500"): 108.00,
            ("PB-MAN-0017", "BEL-STD-01"): 6.55, ("PB-MAN-0017", "BRK-PAD-01"): 9.10, ("CC-SAL-0031", "CHG-4A-01"): 93.50,
            ("AM-BIR-0008", "MTR-HUB-250"): 138.00, ("IP-MAN-0055", "BOX-BIKE-01"): 20.40}
    for (s, i), rt in prev.items():
        out.append(dict(sup_cd=s, itm_cd=i, rate=rt, valid_from="2025-04-01", valid_to="2026-03-31", contract_no=""))
    r = rng("rates")
    by_fam = {}
    for s in sups:
        if s["status"] == "ACTIVE" and s["sup_cd"] not in SEED_SUP_CODES:
            by_fam.setdefault(s["supplies"], []).append(s)
    fam_of = {"FST": "FST", "TYR": "TYR", "TUB": "TYR", "RIM": "RIM", "SPK": "RIM", "FRM": "FRM", "PNT": "PNT", "LAC": "PNT",
              "PRM": "PNT", "BOX": "BOX", "PKG": "BOX", "CBL": "CBL", "LGT": "LGT", "BRK": "BRK", "CHN": "CHN", "CST": "CHN",
              "DRL": "CHN", "SHF": "CHN", "BLT": "CHN", "HGR": "CHN", "CRG": "CHN", "CRK": "CHN", "BBR": "CHN", "PDL": "ACC",
              "MRO": "MRO", "ACC": "ACC", "HBR": "ACC", "STM": "ACC", "GRP": "ACC", "SDL": "ACC", "SPT": "ACC", "BEL": "ACC",
              "CTL": "CTL", "DSP": "CTL", "CON": "MRO", "MNT": "ACC", "BAT": "BAT", "MTR": "MTR", "CHG": "CHG"}
    seeded = {(x["sup_cd"], x["itm_cd"]) for x in out}
    for it in itms:
        if it["itm_cd"] in SEED_ITEM_CODES or not it["active"] or it["category"] == "FINISHED":
            continue
        pre = it["itm_cd"].split("-")[0]
        fam = fam_of.get(pre)
        if not fam or fam not in by_fam:
            continue
        if pre == "MRO" and r.random() < 0.6:
            continue  # most MRO spares are bought on direct orders without a contract
        base = _base_price(it, r)
        for s in r.sample(by_fam[fam], min(len(by_fam[fam]), r.choice([1, 1, 2]))):
            if (s["sup_cd"], it["itm_cd"]) in seeded:
                continue
            rt0 = round(base * r.uniform(0.92, 1.0), 2)
            cno = f"RC/{r.randint(2025, 2026)}/{r.randint(100, 999)}"
            out.append(dict(sup_cd=s["sup_cd"], itm_cd=it["itm_cd"], rate=rt0, valid_from="2025-04-01", valid_to="2026-03-31", contract_no=cno))
            out.append(dict(sup_cd=s["sup_cd"], itm_cd=it["itm_cd"], rate=round(rt0 * r.uniform(1.0, 1.06), 2),
                            valid_from="2026-04-01", valid_to="2027-03-31", contract_no=cno))
    return out


def _base_price(it, r):
    c = it["itm_cd"]
    table = [("BAT", 95, 190), ("MTR", 120, 260), ("CHG", 60, 120), ("FRM", 85, 210), ("TYR", 9, 28), ("TUB", 2.5, 5),
             ("RIM", 14, 40), ("SPK", 0.18, 0.45), ("BRK", 6, 55), ("CHN", 7, 22), ("CST", 14, 45), ("DRL", 18, 70),
             ("SHF", 9, 35), ("CTL", 38, 90), ("DSP", 22, 85), ("FST", 0.02, 0.6), ("PNT", 6, 14), ("LAC", 7, 12),
             ("PRM", 5, 9), ("BOX", 1.2, 24), ("PKG", 0.3, 9), ("CBL", 1.5, 14), ("LGT", 6, 38), ("MRO", 4, 900)]
    for p, lo, hi in table:
        if c.startswith(p):
            return round(r.uniform(lo, hi), 2)
    return round(r.uniform(3, 60), 2)


def warehouses():
    out = [dict(whs_cd=a, name=b, ou_cd=c, kind="STORES") for a, b, c in S.WAREHOUSES]
    out += [dict(whs_cd="WH-MAN-QC", name="Manchester quality hold", ou_cd="NBC-MAN-01", kind="QUALITY"),
            dict(whs_cd="WH-MAN-BAT", name="Battery store (6.x code; merged into WH-MAN-STR in 2019, do not use)", ou_cd="NBC-MAN-01", kind="CLOSED"),
            dict(whs_cd="WH-MAN-FG", name="Manchester finished goods", ou_cd="NBC-MAN-01", kind="FG"),
            dict(whs_cd="WH-MAN-RTV", name="Manchester returns to supplier", ou_cd="NBC-MAN-01", kind="RTV"),
            dict(whs_cd="WH-MAN-MRO", name="Manchester maintenance spares", ou_cd="NBC-MAN-01", kind="MRO"),
            dict(whs_cd="WH-LDS-QC", name="Leeds quality hold", ou_cd="NBC-LDS-01", kind="QUALITY"),
            dict(whs_cd="WH-LDS-FG", name="Leeds finished goods", ou_cd="NBC-LDS-01", kind="FG"),
            dict(whs_cd="WH-MAN-OLD", name="Ardwick overflow store (closed 2017)", ou_cd="NBC-MAN-01", kind="CLOSED")]
    return out


def stock(itms):
    """Stock as at 26 Oct 2026, 09:00: seed rows exactly, then rows for other active items."""
    out = [dict(itm_cd=a, whs_cd=b, on_hand=c, allocated=d_, on_order=e) for a, b, c, d_, e in S.STOCK]
    have = {(x["itm_cd"], x["whs_cd"]) for x in out}
    r = rng("stock")
    for it in itms:
        if not it["active"] or it["itm_cd"] in SEED_ITEM_CODES:
            continue
        whs = "WH-MAN-FG" if it["category"] == "FINISHED" else "WH-MAN-MRO" if it["category"] == "MRO" else "WH-MAN-STR"
        if (it["itm_cd"], whs) in have:
            continue
        adi = it["avg_daily_issue"] or 1
        out.append(dict(itm_cd=it["itm_cd"], whs_cd=whs, on_hand=int(adi * r.uniform(2, 40)) if it["category"] != "MRO" else r.randint(0, 6),
                        allocated=int(adi * r.uniform(0, 3)) if it["category"] in ("RAW", "COMPONENTS") else 0,
                        on_order=r.choice([0, 0, int(adi * 10)])))
        if r.random() < 0.25 and it["category"] in ("COMPONENTS", "RAW", "SPARES"):
            out.append(dict(itm_cd=it["itm_cd"], whs_cd="WH-LDS-STR", on_hand=int(adi * r.uniform(1, 10)), allocated=0, on_order=0))
    return out


def cost_centres():
    out = [dict(cc_cd=a, name=b, status=c, closed_on=d_, owner=e, ou_cd="NBC-MAN-01", opened_on="") for a, b, c, d_, e in S.COST_CENTRES]
    extra = [("PRD-01", "Ancoats city line (2016-2022)", "CLOSED", "2022-12-31", "DOKAFOR"),
             ("PRD-02", "Deansgate step-through line", "OPEN", None, "DOKAFOR"),
             ("PRD-04", "Medlock trekking line", "OPEN", None, "DOKAFOR"),
             ("PRD-06", "Tame folding line", "CLOSED", "2025-03-31", "DOKAFOR"),
             ("PRD-08", "Roch mountain line (opens 2027)", "PLANNED", None, "DOKAFOR"),
             ("PRD-09", "Battery refurbishment", "OPEN", None, "PJANSEN"),
             ("MNT-02", "Leeds maintenance", "OPEN", None, "BPRICE"), ("QA-01", "Quality", "OPEN", None, "PJANSEN"),
             ("LOG-01", "Stores and logistics", "OPEN", None, "CSHAW"), ("SAL-01", "Sales UK", "OPEN", None, "IMORGAN"),
             ("SAL-02", "Sales Europe", "OPEN", None, "IMORGAN"), ("SAL-03", "Warranty and service", "OPEN", None, "IMORGAN"),
             ("RND-01", "Product development", "OPEN", None, "HWEBER"), ("IT-01", "IT", "OPEN", None, "RPRYCE"),
             ("HR-01", "Human resources", "OPEN", None, "SLINDQVIST"), ("FIN-01", "Finance", "OPEN", None, "GWHITAKER"),
             ("HSE-01", "Health, safety and environment", "OPEN", None, "HWEBER"),
             ("LDS-PRD-01", "Leeds assembly", "OPEN", None, "BPRICE"), ("LDS-LOG-01", "Leeds stores", "OPEN", None, "BPRICE"),
             ("LDS-ADM-01", "Leeds administration", "OPEN", None, "BPRICE"),
             ("PRD-5", "City line (6.x code, do not use)", "CLOSED", "2019-03-31", "GSUTCLIFFE"),
             ("CAP-2026", "Capital projects 2026-27", "OPEN", None, "GWHITAKER"),
             ("CAP-2025", "Capital projects 2025-26", "CLOSED", "2026-03-31", "GWHITAKER")]
    for a, b, c, d_, e in extra:
        out.append(dict(cc_cd=a, name=b, status=c, closed_on=d_, owner=e, ou_cd="NBC-LDS-01" if a.startswith("LDS") else "NBC-MAN-01", opened_on=""))
    return out


def budgets(ccs):
    out = [dict(cc_cd=a, period=b, amount=c, committed=d_) for a, b, c, d_ in S.BUDGETS]
    have = {(x["cc_cd"], x["period"]) for x in out}
    r = rng("budgets")
    periods = ["2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2", "2026-Q3", "2026-Q4", "2027-Q1"]
    for cc in ccs:
        base = r.choice([50000, 120000, 200000, 300000, 600000, 900000])
        for p in periods:
            if (cc["cc_cd"], p) in have or cc["status"] == "PLANNED" and p != "2027-Q1":
                continue
            if cc["closed_on"] and p > cc["closed_on"][:4] + "-Q" + str((int(cc["closed_on"][5:7]) - 1) // 3 + 1):
                continue
            amt = round(base * r.uniform(0.8, 1.2), -3)
            used = amt * r.uniform(0.55, 1.0) if p < "2026-Q4" else 0 if p == "2027-Q1" else amt * r.uniform(0.1, 0.4)
            out.append(dict(cc_cd=cc["cc_cd"], period=p, amount=amt, committed=round(used, 2)))
    return out


def tax_codes():
    out = [dict(tax_cd=a, descr=b, rate=c, kind=d_, active=1, valid_from="2011-01-04", valid_to="") for a, b, c, d_ in S.TAX_CODES]
    out += [dict(tax_cd="VAT0-ZR", descr="Zero-rated (UK supplier)", rate=0.0, kind="INTRA", active=1, valid_from="1998-04-01", valid_to=""),
            dict(tax_cd="VAT0-RC", descr="Zero-rated, reverse charge (overseas supplier)", rate=0.0, kind="INTER", active=1, valid_from="2011-01-04", valid_to=""),
            dict(tax_cd="VAT-EX", descr="Exempt", rate=0.0, kind="NA", active=1, valid_from="1998-04-01", valid_to=""),
            dict(tax_cd="OUTSCOPE", descr="Outside the scope of VAT", rate=0.0, kind="NA", active=1, valid_from="1998-04-01", valid_to=""),
            dict(tax_cd="V175-UK", descr="VAT 17.5% (UK supplier), legacy", rate=0.175, kind="INTRA", active=0, valid_from="1998-04-01", valid_to="2011-01-03"),
            dict(tax_cd="V15-UK", descr="VAT 15% (UK supplier), temporary rate, legacy", rate=0.15, kind="INTRA", active=0, valid_from="2008-12-01", valid_to="2009-12-31"),
            dict(tax_cd="V1", descr="6.x code: standard rate, do not use", rate=0.175, kind="INTRA", active=0, valid_from="1998-04-01", valid_to="2011-01-03")]
    return out


def pay_terms():
    out = [dict(pt_cd=a, descr=b, days=c) for a, b, c in S.PAY_TERMS]
    out += [dict(pt_cd="N15", descr="Net 15 days", days=15), dict(pt_cd="N90", descr="Net 90 days (legacy, do not use)", days=90),
            dict(pt_cd="EOM30", descr="30 days end of month", days=30), dict(pt_cd="N7", descr="Net 7 days", days=7)]
    return out


UOMS = [("NOS", "Numbers (pieces)"), ("KG", "Kilograms"), ("PR", "Pair"), ("SET", "Set"), ("MTR", "Metres"), ("ROL", "Roll"),
        ("BOX", "Box"), ("BAG", "Bag"), ("PKT", "Packet"), ("HRS", "Hours (services)"), ("EA", "Each (6.x, same as NOS)")]


def customers():
    r = rng("customers")
    towns = {"GB": ["Harrogate", "York", "Chester", "Bath", "Kendal", "Lancaster", "Shrewsbury", "Ludlow", "Durham",
                    "Cambridge", "Oxford", "Brighton", "Exeter", "Norwich", "Lincoln", "Edinburgh", "Aberdeen", "Belfast",
                    "Swansea", "Hexham", "Keswick", "Buxton", "Ilkley", "Skipton", "Whitby"],
             "NL": ["Haarlem", "Leiden", "Delft", "Groningen", "Nijmegen"], "DE": ["Freiburg", "Münster", "Hamburg", "Bremen"],
             "BE": ["Bruges", "Leuven"], "FR": ["Strasbourg", "Annecy", "Rennes"], "DK": ["Aarhus"], "IE": ["Galway", "Cork"]}
    kinds = ["Cycles", "Bike Shop", "Wheels", "E-Bikes", "Cycle Centre", "Velo", "Bike Works", "Pedal Power", "Spokes"]
    out = []
    n = 1000
    for _ in range(560):
        c = r.choices(list(towns), [60, 10, 10, 4, 6, 3, 4])[0]
        t = r.choice(towns[c])
        n += r.randint(1, 9)
        out.append(dict(cust_cd=f"C{n:05d}", name=f"{r.choice(['The ', '', '', ''])}{t} {r.choice(kinds)}", country=c, city=t,
                        price_list=r.choice(["PL-UK-RTL", "PL-UK-RTL", "PL-EU-RTL", "PL-KEY"]) if c == "GB" else "PL-EU-RTL",
                        credit_limit=r.choice([15000, 25000, 40000, 60000, 100000]), pt_cd=r.choice(["N30", "N30", "N45", "ADV"]),
                        status="ACTIVE" if r.random() > 0.07 else "ON HOLD", rep=r.choice(["IMORGAN", "ECHEN"])))
    return out


class World:
    def __init__(self):
        self.users = users()
        self.items = items()
        self.item = {i["itm_cd"]: i for i in self.items}
        self.suppliers = suppliers()
        self.sup = {s["sup_cd"]: s for s in self.suppliers}
        self.certs = certificates(self.suppliers)
        self.rates = rate_contracts(self.suppliers, self.items)
        self.warehouses = warehouses()
        self.stock = stock(self.items)
        self.ccs = cost_centres()
        self.budgets = budgets(self.ccs)
        self.taxes = tax_codes()
        self.pts = pay_terms()
        self.uoms = UOMS
        self.customers = customers()
        self.user = {u["user_id"]: u for u in self.users}
        self.std_cost()

    def std_cost(self):
        cur = {}
        for rc in self.rates:
            if rc["valid_from"] <= TODAY <= rc["valid_to"]:
                cur.setdefault(rc["itm_cd"], []).append(rc["rate"])
        r = rng("stdcost")
        for it in self.items:
            if it["itm_cd"] in cur:
                it["std_cost"] = round(min(cur[it["itm_cd"]]), 2)
            elif it["category"] == "FINISHED":
                it["std_cost"] = round(r.uniform(780, 1900), 2)
            else:
                it["std_cost"] = _base_price(it, r)

    def current_rate(self, sup_cd, itm_cd, on=TODAY):
        for rc in self.rates:
            if rc["sup_cd"] == sup_cd and rc["itm_cd"] == itm_cd and rc["valid_from"] <= on <= rc["valid_to"]:
                return rc["rate"]
        return None

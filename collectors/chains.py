"""
Chain catalog for NYC supermarkets.

Patterns are matched case-insensitively against the combined dba_name +
entity_name string (state file) or the name/brand fields (OSM). A match
produces:
  - chain_name: canonical name (e.g., "Whole Foods Market")
  - chain_type: "national", "local_nyc", or "independent"

A chain match also force-promotes `is_supermarket=True` -- if a name
matches a known grocery chain, we trust the chain over any name-keyword
or OSM-tag false negative. (Whole Foods has cafes inside; OSM might tag
the entrance as amenity=cafe; the chain rule wins.)
"""

import re

# Order matters within a list -- earliest match wins.
NATIONAL = [
    ("Whole Foods Market",   r"\bWHOLE\s*FOODS\b"),
    ("Trader Joe's",         r"\bTRADER\s*JOE"),
    ("Costco",               r"\bCOSTCO\b"),
    ("Sam's Club",           r"\bSAM'?S\s*CLUB\b"),
    ("BJ's Wholesale",       r"\bBJ'?S\b"),
    ("Walmart",              r"\bWAL[\s\-]?MART\b"),
    ("Target",               r"^TARGET\b|\bTARGET\s+(STORE|CORP|T-?\d)"),
    ("Aldi",                 r"\bALDI\b"),
    ("Lidl",                 r"\bLIDL\b"),
    ("Wegmans",              r"\bWEGMANS\b"),
    ("ShopRite",             r"\bSHOP[\s\-]?RITE\b"),
    ("Stop & Shop",          r"\bSTOP\s*&?\s*SHOP\b|\bSTOP\s+AND\s+SHOP\b"),
    ("Acme Markets",         r"\bACME\s*(MARKET|FRESH|SUPER|SAVE)"),
    ("Sprouts Farmers Market", r"\bSPROUTS\b"),
    ("The Fresh Market",     r"\bTHE\s+FRESH\s+MARKET\b"),
    ("Amazon Fresh",         r"\bAMAZON\s+FRESH\b"),
]

LOCAL_NYC = [
    ("Key Food",             r"\bKEY\s*FOOD"),
    ("Associated Supermarket", r"\bASSOCIATED\s*(SUPERMARKET|FOOD|MARKET)"),
    ("Met Food",             r"\bMET\s*FOODS?\b|\bMET\s*FRESH\b|\bMET\s*FOODMARKET\b"),
    ("C-Town",               r"\bC[-\s]?TOWN\b"),
    ("Bravo Supermarkets",   r"\bBRAVO\s*(SUPERMARKET|FRESH|MARKET|FOOD)"),
    ("Pioneer Supermarkets", r"\bPIONEER\s*(SUPERMARKET|FOOD|MARKET)"),
    ("Foodtown",             r"\bFOOD\s*TOWN\b|\bFOODTOWN\b"),
    ("Fine Fare",            r"\bFINE\s*FARE\b|\bFINEFARE\b"),
    ("Compare Foods",        r"\bCOMPARE\s*FOOD"),
    ("Gristedes",            r"\bGRISTEDES?\b"),
    ("Morton Williams",      r"\bMORTON\s*WILLIAMS\b"),
    ("Western Beef",         r"\bWESTERN\s*BEEF\b"),
    ("Food Bazaar",          r"\bFOOD\s*BAZAAR\b"),
    ("H Mart",               r"\bH[\s\-]MART\b"),
    ("Iavarone Bros",        r"\bIAVARONE\b"),
    ("Uncle Giuseppe's",     r"\bUNCLE\s*GIUSEPPE"),
    ("Citarella",            r"\bCITARELLA\b"),
    ("Eli's / Eli Zabar",    r"\bELI'?S\s*MARKET\b|\bELI\s+ZABAR\b|\bELI'?S\s+VINEGAR\b"),
    ("Westside Market",      r"\bWESTSIDE\s*MARKET\b"),
    ("Zabar's",              r"\bZABAR'?S\b"),
    ("Gourmet Garage",       r"\bGOURMET\s*GARAGE\b"),
    ("Food Emporium",        r"\bFOOD\s*EMPORIUM\b"),
    ("Food Universe",        r"\bFOOD\s*UNIVERSE\b"),
    ("Food Dynasty",         r"\bFOOD\s*DYNASTY\b"),
    ("Red Apple",            r"\bRED\s*APPLE\s*(SUPERMARKET|MARKET|FOOD)"),
    ("Gold City Supermarket", r"\bGOLD\s*CITY\s*SUPER"),
    ("NetCost Market",       r"\bNET[\s]?COST\b"),
    ("Gourmet Glatt",        r"\bGOURMET\s*GLATT\b"),
    ("Super Fresh",          r"\bSUPER[\s]?FRESH\b"),
    ("Cherry Valley",        r"\bCHERRY\s*VALLEY\b"),
    ("Amish Market",         r"\bAMISH\s*MARKET\b"),
    ("Best Market",          r"\bBEST\s*MARKET\b"),
    ("Trade Fair",           r"\bTRADE\s*FAIR\b"),
    ("Fairway Market",       r"\bFAIRWAY\b"),
    ("Patel Brothers",       r"\bPATEL\s*BROTHERS\b"),
    ("Apna Bazar",           r"\bAPNA\s*BAZ"),
    ("Stew Leonard's",       r"\bSTEW\s*LEONARD"),
    ("Whole Foods 365",      r"\b365\s+BY\s+WHOLE\b"),
    ("FreshDirect",          r"\bFRESH\s*DIRECT\b"),
    ("Garden of Eden",       r"\bGARDEN\s+OF\s+EDEN\b"),
    ("Mr. Piggy",            r"\bMR\.?\s*PIGGY\b"),
    ("Ideal Food Basket",    r"\bIDEAL\s*FOOD\s*BASKET\b"),
    ("Food Cellar",          r"\bFOOD\s*CELLAR\b"),
    ("Chinatown Supermarket", r"\bCHINATOWN\s*SUPERMARKET\b"),
    ("Island of Gold",       r"\bISLAND\s*OF\s*GOLD\b|\bI\.?O\.?G\.?\s*SUPER"),
    ("Eli's / Eli Zabar",    r"\bELIS\b"),  # no-apostrophe form
    ("Eagle Provisions",     r"\bEAGLE\s*PROVISIONS\b"),
    ("Sunac Natural Market", r"\bSUNAC\b"),
    ("D'Agostino",           r"\bD'?AGOSTINO\b"),
    ("Park Slope Food Coop", r"\bPARK\s+SLOPE\s+FOOD\s+COOP\b"),
    ("Brooklyn Fare",        r"\bBROOKLYN\s+FARE\b"),
    ("Mr. Mango",            r"\bMR\.?\s*MANGO\b"),
    ("Lifethyme Natural",    r"\bLIFETHYME\b"),
    ("Westerly Natural",     r"\bWESTERLY\s*NATURAL\b"),
    ("NetCost Market",       r"\bNET\s*COST\b"),
    ("Mrs. Green's",         r"\bMRS\.?\s*GREEN'?S\b"),
    ("Top Tomato",           r"\bTOP\s+TOMATO\b"),
    ("ShopFair Supermarket", r"\bSHOP\s*FAIR\b|\bSHOPFAIR\b"),
    ("Met Fresh / Met Food", r"\bMET\s+FRESH\b"),
]

# Compile once
def _compile(rows):
    return [(name, re.compile(pat)) for name, pat in rows]

NATIONAL_C = _compile(NATIONAL)
LOCAL_NYC_C = _compile(LOCAL_NYC)


def classify_chain(name: str):
    """Returns (chain_name, chain_type) or (None, None) if no match."""
    if not name:
        return None, None
    s = name.upper()
    for canonical, pat in NATIONAL_C:
        if pat.search(s):
            return canonical, "national"
    for canonical, pat in LOCAL_NYC_C:
        if pat.search(s):
            return canonical, "local_nyc"
    return None, None

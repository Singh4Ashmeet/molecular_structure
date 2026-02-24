"""
app.py – Molecular Theory Explained
Flask backend with SQLite, session auth, VSEPR AI explanation,
expanded compound library, user molecule search, and Render-ready config.
"""

import sqlite3
import os
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify, g
)
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)

# Render sets SECRET_KEY as an environment variable; fall back for local dev
app.secret_key = os.environ.get("SECRET_KEY", "molecular-theory-secret-key-2024")

# On Render the working dir is the repo root; keep DB in /tmp so it is writable
DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "database.db")
)

# ---------------------------------------------------------------------------
# Database Helpers
# ---------------------------------------------------------------------------

def get_db():
    """Open a database connection stored on Flask's g object."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables if they do not exist yet."""
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_scores (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            difficulty TEXT    NOT NULL,
            score      INTEGER NOT NULL,
            timestamp  TEXT    NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Auth Decorator
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Full Compound Library  (preset + searchable)
# Each entry:
#   formula, name, category, geometry, electronGeometry, bondAngle,
#   lonePairs, polarity, hybridisation, bondingType, reactivity, info
# ---------------------------------------------------------------------------

COMPOUND_LIBRARY = {
    # ── Inorganic – simple covalent ──────────────────────────────────────
    "H2O": {
        "formula": "H₂O", "name": "Water",
        "category": "Inorganic",
        "geometry": "Bent", "electronGeometry": "Tetrahedral",
        "bondAngle": "104.5°", "lonePairs": 2, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Universal solvent; participates in hydrogen bonding; highly reactive with metals and nonmetals.",
        "info": "Bent geometry due to 2 lone pairs on O compressing H–O–H from 109.5° to 104.5°."
    },
    "CO2": {
        "formula": "CO₂", "name": "Carbon Dioxide",
        "category": "Inorganic",
        "geometry": "Linear", "electronGeometry": "Linear",
        "bondAngle": "180°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp", "bondingType": "Covalent (2× double bond)",
        "reactivity": "Forms carbonic acid with water; greenhouse gas; used in fire extinguishers.",
        "info": "No lone pairs on C; two double bonds arrange linearly. Bond dipoles cancel perfectly."
    },
    "NH3": {
        "formula": "NH₃", "name": "Ammonia",
        "category": "Inorganic",
        "geometry": "Trigonal Pyramidal", "electronGeometry": "Tetrahedral",
        "bondAngle": "107°", "lonePairs": 1, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Strong base; forms ammonium salts with acids; used in fertilisers.",
        "info": "1 lone pair on N compresses H–N–H from 109.5° to 107°; trigonal pyramidal shape."
    },
    "CH4": {
        "formula": "CH₄", "name": "Methane",
        "category": "Organic",
        "geometry": "Tetrahedral", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp³", "bondingType": "Covalent (non-polar)",
        "reactivity": "Low reactivity; combustion and halogenation; primary component of natural gas.",
        "info": "Perfect tetrahedral geometry; no lone pairs; all C–H bond dipoles cancel."
    },
    # ── Inorganic – more ─────────────────────────────────────────────────
    "HCl": {
        "formula": "HCl", "name": "Hydrogen Chloride",
        "category": "Inorganic",
        "geometry": "Linear", "electronGeometry": "Linear",
        "bondAngle": "180°", "lonePairs": 3, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Strong acid in water; corrosive; reacts with metals and bases.",
        "info": "Diatomic molecule; 3 lone pairs on Cl; large electronegativity difference gives strong dipole."
    },
    "H2S": {
        "formula": "H₂S", "name": "Hydrogen Sulfide",
        "category": "Inorganic",
        "geometry": "Bent", "electronGeometry": "Tetrahedral",
        "bondAngle": "92°", "lonePairs": 2, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Toxic; weak acid; rotten-egg odour; dissolves in water to form hydrosulfuric acid.",
        "info": "Similar to water but bond angle is ~92° because S uses larger orbitals with less hybridisation."
    },
    "SO2": {
        "formula": "SO₂", "name": "Sulfur Dioxide",
        "category": "Inorganic",
        "geometry": "Bent", "electronGeometry": "Trigonal Planar",
        "bondAngle": "119°", "lonePairs": 1, "polarity": "Polar",
        "hybridisation": "sp²", "bondingType": "Covalent (polar)",
        "reactivity": "Acidic; forms sulfurous acid with water; air pollutant; used in food preservation.",
        "info": "1 lone pair on S bends the O–S–O from 120° to ~119°; resonance structures exist."
    },
    "SO3": {
        "formula": "SO₃", "name": "Sulfur Trioxide",
        "category": "Inorganic",
        "geometry": "Trigonal Planar", "electronGeometry": "Trigonal Planar",
        "bondAngle": "120°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp²", "bondingType": "Covalent (polar bonds, non-polar molecule)",
        "reactivity": "Reacts violently with water to form H₂SO₄; strong Lewis acid.",
        "info": "No lone pairs on S; 3 equivalent S=O bonds arranged in a perfect trigonal plane."
    },
    "PCl3": {
        "formula": "PCl₃", "name": "Phosphorus Trichloride",
        "category": "Inorganic",
        "geometry": "Trigonal Pyramidal", "electronGeometry": "Tetrahedral",
        "bondAngle": "100°", "lonePairs": 1, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Moisture-sensitive; hydrolyses to H₃PO₃; used in organic synthesis.",
        "info": "Like NH₃ but larger Cl atoms and a lone pair give a compressed 100° bond angle."
    },
    "PCl5": {
        "formula": "PCl₅", "name": "Phosphorus Pentachloride",
        "category": "Inorganic",
        "geometry": "Trigonal Bipyramidal", "electronGeometry": "Trigonal Bipyramidal",
        "bondAngle": "90°/120°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp³d", "bondingType": "Covalent",
        "reactivity": "Reacts violently with water; strong chlorinating agent.",
        "info": "5 bonding pairs; axial bonds 90° to equatorial; equatorial bonds 120° to each other."
    },
    "SF6": {
        "formula": "SF₆", "name": "Sulfur Hexafluoride",
        "category": "Inorganic",
        "geometry": "Octahedral", "electronGeometry": "Octahedral",
        "bondAngle": "90°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp³d²", "bondingType": "Covalent",
        "reactivity": "Extremely stable; electrical insulator; greenhouse gas.",
        "info": "6 identical S–F bonds arranged octahedrally; all bond dipoles cancel."
    },
    "NF3": {
        "formula": "NF₃", "name": "Nitrogen Trifluoride",
        "category": "Inorganic",
        "geometry": "Trigonal Pyramidal", "electronGeometry": "Tetrahedral",
        "bondAngle": "102.5°", "lonePairs": 1, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Moderately reactive; used in semiconductor manufacturing; potent greenhouse gas.",
        "info": "Similar to NH₃ but N–F bonds are less polar; lone pair gives pyramidal shape."
    },
    "ClF3": {
        "formula": "ClF₃", "name": "Chlorine Trifluoride",
        "category": "Inorganic",
        "geometry": "T-Shaped", "electronGeometry": "Trigonal Bipyramidal",
        "bondAngle": "87.5°", "lonePairs": 2, "polarity": "Polar",
        "hybridisation": "sp³d", "bondingType": "Covalent (polar)",
        "reactivity": "Extremely reactive; ignites most combustible materials spontaneously.",
        "info": "2 lone pairs occupy equatorial positions in a trigonal bipyramid, giving a T-shape."
    },
    "XeF2": {
        "formula": "XeF₂", "name": "Xenon Difluoride",
        "category": "Inorganic",
        "geometry": "Linear", "electronGeometry": "Trigonal Bipyramidal",
        "bondAngle": "180°", "lonePairs": 3, "polarity": "Non-polar",
        "hybridisation": "sp³d", "bondingType": "Covalent (hypervalent)",
        "reactivity": "Strong fluorinating agent; slowly hydrolyses in water.",
        "info": "3 lone pairs occupy equatorial positions; 2 F atoms are axial giving a linear shape."
    },
    "XeF4": {
        "formula": "XeF₄", "name": "Xenon Tetrafluoride",
        "category": "Inorganic",
        "geometry": "Square Planar", "electronGeometry": "Octahedral",
        "bondAngle": "90°", "lonePairs": 2, "polarity": "Non-polar",
        "hybridisation": "sp³d²", "bondingType": "Covalent (hypervalent)",
        "reactivity": "Powerful oxidiser; reacts violently with water.",
        "info": "2 lone pairs in axial positions; 4 F atoms in a square plane around Xe."
    },
    "H2O2": {
        "formula": "H₂O₂", "name": "Hydrogen Peroxide",
        "category": "Inorganic",
        "geometry": "Bent (at each O)", "electronGeometry": "Tetrahedral",
        "bondAngle": "111°", "lonePairs": 2, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Strong oxidiser; decomposes to H₂O + O₂; used as bleach and antiseptic.",
        "info": "Each O is sp³; O–O single bond with lone pairs; non-planar structure."
    },
    "N2O": {
        "formula": "N₂O", "name": "Nitrous Oxide",
        "category": "Inorganic",
        "geometry": "Linear", "electronGeometry": "Linear",
        "bondAngle": "180°", "lonePairs": 0, "polarity": "Polar",
        "hybridisation": "sp", "bondingType": "Covalent",
        "reactivity": "Anaesthetic (laughing gas); supports combustion; greenhouse gas.",
        "info": "N–N–O linear arrangement; small net dipole because N and O differ in electronegativity."
    },
    "NO2": {
        "formula": "NO₂", "name": "Nitrogen Dioxide",
        "category": "Inorganic",
        "geometry": "Bent", "electronGeometry": "Trigonal Planar",
        "bondAngle": "134°", "lonePairs": 0.5, "polarity": "Polar",
        "hybridisation": "sp²", "bondingType": "Covalent (radical)",
        "reactivity": "Brown toxic gas; air pollutant; dimerises to N₂O₄; strong oxidiser.",
        "info": "Odd-electron radical; unpaired electron acts like a half lone pair compressing angle less than 120°."
    },
    # ── Coordinate / Complex ─────────────────────────────────────────────
    "BF3": {
        "formula": "BF₃", "name": "Boron Trifluoride",
        "category": "Coordinate / Lewis Acid",
        "geometry": "Trigonal Planar", "electronGeometry": "Trigonal Planar",
        "bondAngle": "120°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp²", "bondingType": "Covalent (electron deficient)",
        "reactivity": "Strong Lewis acid; accepts lone pairs from bases; forms adducts (BF₃·NH₃).",
        "info": "Only 3 bonding pairs; flat trigonal planar; empty p orbital makes it a Lewis acid."
    },
    "BF4_minus": {
        "formula": "BF₄⁻", "name": "Tetrafluoroborate Ion",
        "category": "Coordinate / Complex Ion",
        "geometry": "Tetrahedral", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp³", "bondingType": "Covalent + Coordinate (dative bond from F⁻ to B)",
        "reactivity": "Stable, weakly coordinating anion used in ionic liquids and catalysis.",
        "info": "F⁻ donates a lone pair to empty p orbital of BF₃ forming a dative bond; tetrahedral product."
    },
    "NH4_plus": {
        "formula": "NH₄⁺", "name": "Ammonium Ion",
        "category": "Coordinate / Complex Ion",
        "geometry": "Tetrahedral", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5°", "lonePairs": 0, "polarity": "Non-polar (ion)",
        "hybridisation": "sp³", "bondingType": "3 covalent + 1 dative (coordinate) bond",
        "reactivity": "Weak acid; found in fertilisers; forms salts with anions.",
        "info": "NH₃ donates its lone pair to H⁺ via a dative bond; all 4 N–H bonds identical; perfect tetrahedral."
    },
    "H3O_plus": {
        "formula": "H₃O⁺", "name": "Hydronium Ion",
        "category": "Coordinate / Complex Ion",
        "geometry": "Trigonal Pyramidal", "electronGeometry": "Tetrahedral",
        "bondAngle": "113°", "lonePairs": 1, "polarity": "Polar (cation)",
        "hybridisation": "sp³", "bondingType": "Covalent + Coordinate bond",
        "reactivity": "Carrier of acidity in aqueous solution; formed when acids dissolve in water.",
        "info": "Water donates a lone pair to H⁺; resulting ion is pyramidal with one lone pair on O."
    },
    "Cu_NH3_4": {
        "formula": "[Cu(NH₃)₄]²⁺", "name": "Tetraamminecopper(II) Ion",
        "category": "Coordinate / Transition Metal Complex",
        "geometry": "Square Planar", "electronGeometry": "Square Planar",
        "bondAngle": "90°", "lonePairs": 0, "polarity": "Polar (cation)",
        "hybridisation": "dsp²", "bondingType": "4 dative (coordinate) bonds from NH₃ to Cu²⁺",
        "reactivity": "Deep blue colour; forms when excess NH₃ added to Cu²⁺ solution; used in qualitative analysis.",
        "info": "Cu²⁺ accepts 4 lone pairs from NH₃ ligands; square planar due to d⁹ Cu²⁺ Jahn-Teller distortion."
    },
    "Fe_CN_6": {
        "formula": "[Fe(CN)₆]⁴⁻", "name": "Hexacyanoferrate(II) Ion",
        "category": "Coordinate / Transition Metal Complex",
        "geometry": "Octahedral", "electronGeometry": "Octahedral",
        "bondAngle": "90°", "lonePairs": 0, "polarity": "Non-polar (anion)",
        "hybridisation": "d²sp³", "bondingType": "6 dative (coordinate) bonds (CN⁻ → Fe²⁺)",
        "reactivity": "Used in Prussian blue pigment; gives dark blue precipitate with Fe³⁺.",
        "info": "6 CN⁻ ligands donate lone pairs to Fe²⁺; strong field ligands cause low-spin configuration."
    },
    # ── Organic ─────────────────────────────────────────────────────────
    "C2H6": {
        "formula": "C₂H₆", "name": "Ethane",
        "category": "Organic – Alkane",
        "geometry": "Tetrahedral (at each C)", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp³", "bondingType": "Covalent (C–C σ, C–H σ)",
        "reactivity": "Low reactivity; combustion; free-radical halogenation.",
        "info": "Both carbons sp³; C–C single bond allows free rotation; non-polar molecule."
    },
    "C2H4": {
        "formula": "C₂H₄", "name": "Ethene (Ethylene)",
        "category": "Organic – Alkene",
        "geometry": "Trigonal Planar (at each C)", "electronGeometry": "Trigonal Planar",
        "bondAngle": "120°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp²", "bondingType": "Covalent (C=C: 1σ + 1π, C–H σ)",
        "reactivity": "Addition reactions (HBr, H₂O, Cl₂); polymerises to polyethylene; plant hormone.",
        "info": "Both carbons sp²; planar molecule; π bond restricts rotation around C=C."
    },
    "C2H2": {
        "formula": "C₂H₂", "name": "Ethyne (Acetylene)",
        "category": "Organic – Alkyne",
        "geometry": "Linear", "electronGeometry": "Linear",
        "bondAngle": "180°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp", "bondingType": "Covalent (C≡C: 1σ + 2π, C–H σ)",
        "reactivity": "Burns hot (welding); addition reactions; acidic C–H proton.",
        "info": "Both carbons sp; triple bond gives linear geometry; H–C≡C–H all collinear."
    },
    "C6H6": {
        "formula": "C₆H₆", "name": "Benzene",
        "category": "Organic – Aromatic",
        "geometry": "Trigonal Planar (hexagonal ring)", "electronGeometry": "Trigonal Planar",
        "bondAngle": "120°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp²", "bondingType": "Covalent (delocalised π system)",
        "reactivity": "Electrophilic aromatic substitution; resistant to addition; carcinogenic.",
        "info": "6 sp² carbons in a ring; delocalised π electrons above and below the plane; all angles 120°."
    },
    "CH3OH": {
        "formula": "CH₃OH", "name": "Methanol",
        "category": "Organic – Alcohol",
        "geometry": "Tetrahedral (at C), Bent (at O)", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5° (C), ~104° (O)", "lonePairs": 2, "polarity": "Polar",
        "hybridisation": "sp³ (C and O)", "bondingType": "Covalent (polar)",
        "reactivity": "Toxic; fuel; solvent; combustion; oxidised to formaldehyde.",
        "info": "OH group makes it polar and capable of hydrogen bonding; O has 2 lone pairs."
    },
    "C2H5OH": {
        "formula": "C₂H₅OH", "name": "Ethanol",
        "category": "Organic – Alcohol",
        "geometry": "Tetrahedral (at C), Bent (at O)", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5° (C), ~104° (O)", "lonePairs": 2, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Fermentation product; solvent; fuel; oxidised to ethanal then ethanoic acid.",
        "info": "Polar OH group enables hydrogen bonding and water miscibility; ethyl group is non-polar."
    },
    "CH2O": {
        "formula": "CH₂O", "name": "Formaldehyde (Methanal)",
        "category": "Organic – Aldehyde",
        "geometry": "Trigonal Planar", "electronGeometry": "Trigonal Planar",
        "bondAngle": "120°", "lonePairs": 0, "polarity": "Polar",
        "hybridisation": "sp²", "bondingType": "Covalent (C=O, C–H)",
        "reactivity": "Preservative; resin production; toxic; nucleophilic addition reactions.",
        "info": "sp² carbon; C=O bond is strongly polar; planar molecule with 120° angles."
    },
    "CH3COOH": {
        "formula": "CH₃COOH", "name": "Acetic Acid (Ethanoic Acid)",
        "category": "Organic – Carboxylic Acid",
        "geometry": "Trigonal Planar (at carbonyl C)", "electronGeometry": "Trigonal Planar",
        "bondAngle": "120° (at COOH)", "lonePairs": 2, "polarity": "Polar",
        "hybridisation": "sp³ (CH₃), sp² (COOH)", "bondingType": "Covalent (polar)",
        "reactivity": "Weak acid; esterification; reacts with bases and alcohols; vinegar component.",
        "info": "Carbonyl C is sp²; carboxyl group can donate H⁺; strong hydrogen bonding (forms dimers)."
    },
    "CCl4": {
        "formula": "CCl₄", "name": "Carbon Tetrachloride",
        "category": "Organic – Haloalkane",
        "geometry": "Tetrahedral", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar bonds, non-polar molecule)",
        "reactivity": "Solvent for non-polar substances; ozone-depleting; reacts with strong reducing agents.",
        "info": "Symmetric tetrahedral; all 4 C–Cl dipoles cancel; non-polar despite polar bonds."
    },
    "CHCl3": {
        "formula": "CHCl₃", "name": "Chloroform (Trichloromethane)",
        "category": "Organic – Haloalkane",
        "geometry": "Tetrahedral", "electronGeometry": "Tetrahedral",
        "bondAngle": "~109.5°", "lonePairs": 0, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Solvent; formerly anaesthetic; reacts slowly with O₂ to form toxic phosgene.",
        "info": "One H instead of Cl breaks symmetry; net dipole moment exists; denser than water."
    },
    "C3H8": {
        "formula": "C₃H₈", "name": "Propane",
        "category": "Organic – Alkane",
        "geometry": "Tetrahedral (at each C)", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5°", "lonePairs": 0, "polarity": "Non-polar",
        "hybridisation": "sp³", "bondingType": "Covalent (non-polar)",
        "reactivity": "LPG fuel; combustion; halogenation.",
        "info": "3-carbon chain; all sp³; London dispersion forces between molecules."
    },
    "C6H12O6": {
        "formula": "C₆H₁₂O₆", "name": "Glucose",
        "category": "Organic – Carbohydrate",
        "geometry": "Tetrahedral (at C), Bent (at O)", "electronGeometry": "Tetrahedral",
        "bondAngle": "109.5° (C), ~104° (O)", "lonePairs": 5, "polarity": "Polar",
        "hybridisation": "sp³", "bondingType": "Covalent (polar)",
        "reactivity": "Cellular energy source; glycolysis; fermentation; forms glycosidic bonds.",
        "info": "Ring form (pyranose) most common in solution; multiple –OH groups allow extensive H-bonding."
    },
}

# Molecule keys grouped for dropdown
PRESET_GROUPS = {
    "Inorganic": ["H2O", "CO2", "NH3", "HCl", "H2S", "SO2", "SO3",
                  "PCl3", "PCl5", "SF6", "NF3", "ClF3", "XeF2", "XeF4",
                  "H2O2", "N2O", "NO2"],
    "Coordinate / Complex": ["BF3", "BF4_minus", "NH4_plus", "H3O_plus",
                              "Cu_NH3_4", "Fe_CN_6"],
    "Organic": ["CH4", "C2H6", "C2H4", "C2H2", "C6H6",
                "CH3OH", "C2H5OH", "CH2O", "CH3COOH",
                "CCl4", "CHCl3", "C3H8", "C6H12O6"],
}

# ---------------------------------------------------------------------------
# VSEPR AI Explanations  (expanded — all compounds have one)
# ---------------------------------------------------------------------------

def build_explanation(key):
    """Generate a structured VSEPR explanation from the library entry."""
    d = COMPOUND_LIBRARY.get(key)
    if not d:
        return None
    return f"""
<strong>{d['name']} ({d['formula']}) – {d['geometry']}</strong><br><br>
<strong>Category:</strong> {d['category']}<br>
<strong>Electron Geometry:</strong> {d['electronGeometry']}<br>
<strong>Molecular Geometry:</strong> {d['geometry']}<br>
<strong>Bond Angle(s):</strong> {d['bondAngle']}<br>
<strong>Hybridisation:</strong> {d['hybridisation']}<br>
<strong>Lone Pairs on Central Atom:</strong> {d['lonePairs']}<br><br>
<strong>VSEPR Analysis:</strong><br>
{d['info']}<br><br>
<strong>Bonding:</strong> {d['bondingType']}<br>
<strong>Polarity:</strong> {d['polarity']}<br><br>
<strong>Reactivity:</strong> {d['reactivity']}
""".strip()


# ---------------------------------------------------------------------------
# Routes – Public
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    next_page = request.args.get("next", "/")

    if request.method == "POST":
        action = request.form.get("action")
        db = get_db()

        if action == "register":
            name     = request.form.get("name", "").strip()
            email    = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")

            if not name or not email or not password:
                flash("All fields are required for registration.", "error")
                return redirect(url_for("login"))

            existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                flash("An account with that email already exists.", "error")
                return redirect(url_for("login"))

            db.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password))
            )
            db.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("login"))

        elif action == "login":
            email    = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user     = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session["user_id"]   = user["id"]
                session["user_name"] = user["name"]
                flash(f"Welcome back, {user['name']}!", "success")
                safe_next = next_page if next_page.startswith("/") else "/"
                return redirect(safe_next)
            else:
                flash("Invalid email or password.", "error")
                return redirect(url_for("login"))

    return render_template("login.html", next=next_page)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# ---------------------------------------------------------------------------
# Routes – Protected
# ---------------------------------------------------------------------------

@app.route("/explorer")
@login_required
def explorer():
    return render_template("explorer.html", groups=PRESET_GROUPS, library=COMPOUND_LIBRARY)


@app.route("/compare")
@login_required
def compare():
    return render_template("compare.html", groups=PRESET_GROUPS, library=COMPOUND_LIBRARY)


@app.route("/learn")
@login_required
def learn():
    return render_template("learn.html")


@app.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db      = get_db()
    user_id = session["user_id"]

    if request.method == "POST":
        name  = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()

        if not name or not email:
            flash("Name and email cannot be empty.", "error")
        else:
            conflict = db.execute(
                "SELECT id FROM users WHERE email = ? AND id != ?", (email, user_id)
            ).fetchone()
            if conflict:
                flash("That email is already used by another account.", "error")
            else:
                db.execute(
                    "UPDATE users SET name = ?, email = ? WHERE id = ?",
                    (name, email, user_id)
                )
                db.commit()
                session["user_name"] = name
                flash("Profile updated successfully.", "success")

    user   = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    scores = db.execute(
        "SELECT difficulty, score, timestamp FROM quiz_scores "
        "WHERE user_id = ? ORDER BY timestamp DESC",
        (user_id,)
    ).fetchall()

    return render_template("profile.html", user=user, scores=scores)


# ---------------------------------------------------------------------------
# Routes – API (JSON)
# ---------------------------------------------------------------------------

@app.route("/ai-explain", methods=["POST"])
@login_required
def ai_explain():
    """Return a VSEPR explanation for any compound in the library."""
    data     = request.get_json(silent=True) or {}
    molecule = data.get("molecule", "").strip()

    # Try exact key match first, then case-insensitive search
    explanation = build_explanation(molecule)
    if not explanation:
        key_upper = molecule.upper().replace(" ", "")
        for k in COMPOUND_LIBRARY:
            if k.upper() == key_upper:
                explanation = build_explanation(k)
                break

    if not explanation:
        # Graceful fallback for unknown molecules
        return jsonify({
            "molecule": molecule,
            "explanation": (
                f"<strong>Molecule: {molecule}</strong><br><br>"
                "This compound is not yet in our built-in library. "
                "Here are general VSEPR guidelines:<br><br>"
                "• Count bonding pairs + lone pairs on central atom.<br>"
                "• Arrange them to minimise repulsion.<br>"
                "• Each lone pair reduces bond angles by ~2–2.5°.<br>"
                "• Repulsion order: Lone–Lone &gt; Lone–Bond &gt; Bond–Bond.<br><br>"
                "Common geometries:<br>"
                "2 pairs → Linear (180°) | 3 pairs → Trigonal Planar (120°) | "
                "4 pairs → Tetrahedral (109.5°) | 5 pairs → Trigonal Bipyramidal | "
                "6 pairs → Octahedral (90°)"
            )
        })

    return jsonify({"molecule": molecule, "explanation": explanation})


@app.route("/search-molecule", methods=["POST"])
@login_required
def search_molecule():
    """Search the compound library by name, formula, or category."""
    data  = request.get_json(silent=True) or {}
    query = data.get("query", "").strip().lower()

    if not query:
        return jsonify({"results": []})

    results = []
    for key, mol in COMPOUND_LIBRARY.items():
        if (query in mol["formula"].lower() or
                query in mol["name"].lower() or
                query in mol["category"].lower() or
                query in key.lower()):
            results.append({
                "key":      key,
                "formula":  mol["formula"],
                "name":     mol["name"],
                "category": mol["category"],
                "geometry": mol["geometry"],
                "polarity": mol["polarity"],
            })

    return jsonify({"results": results})


@app.route("/molecule-data", methods=["POST"])
@login_required
def molecule_data():
    """Return full data for a given compound key."""
    data = request.get_json(silent=True) or {}
    key  = data.get("key", "").strip()
    mol  = COMPOUND_LIBRARY.get(key)
    if not mol:
        return jsonify({"error": "Not found"}), 404
    return jsonify({"key": key, **mol})


@app.route("/save-score", methods=["POST"])
@login_required
def save_score():
    data       = request.get_json(silent=True) or {}
    difficulty = data.get("difficulty", "")
    score      = data.get("score", 0)

    if difficulty not in ("Easy", "Medium", "Hard"):
        return jsonify({"error": "Invalid difficulty."}), 400

    db = get_db()
    db.execute(
        "INSERT INTO quiz_scores (user_id, difficulty, score, timestamp) VALUES (?, ?, ?, ?)",
        (session["user_id"], difficulty, score,
         datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    db.commit()
    return jsonify({"status": "saved"})


# ---------------------------------------------------------------------------
# Entry Point  (local dev only – Render uses gunicorn)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    print("Database initialised.")
    print("Starting Molecular Theory Explained on http://localhost:5000")
    app.run(debug=True, port=5000)

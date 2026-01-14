import streamlit as st
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Outdoor Gear Wizard V7", page_icon="🧙‍♂️", layout="centered")
st.title("🧙‍♂️ Outdoor Gear Wizard")
st.caption("Sequentielle Planung mit festen Templates")

# --- 1. DEFINITION DER TEMPLATES (Die "Datenbank" im Code) ---

# Deine Rucksäcke
MY_PACKS = {
    'Skitour/Day': {'Name': 'Ortovox 26L (Skitour)', 'Gewicht': 1100, 'Kapazität': 26},
    'Tour':        {'Name': 'Wanderrucksack 40L', 'Gewicht': 1200, 'Kapazität': 40},
    'Trekking':    {'Name': 'Trekkingrucksack 50+10L', 'Gewicht': 1800, 'Kapazität': 60}
}

# Basis-Module (Items: Name, Gramm)
BASIS_WANDERN = [
    ('Wanderschuhe', 900), ('Wanderhose', 400), ('Merino Shirt', 200),
    ('Fleece Midlayer', 300), ('Hardshell Jacke', 300), ('Regenhose', 200),
    ('Wanderstöcke', 450), ('Erste-Hilfe-Kit', 250), ('Stirnlampe', 80),
    ('Hygiene-Kit', 150), ('Sonnenbrille', 40)
]

BASIS_SKITOUR = [
    ('Skischuhe', 3500), ('Tourenhose (Softshell)', 500), ('Merino Shirt', 200),
    ('Fleece Midlayer', 300), ('Hardshell Jacke', 300), ('Hardshell Hose', 400),
    ('Dicke Handschuhe', 150), ('Mütze', 50),
    ('LVS-Gerät', 200), ('Schaufel & Sonde', 600), ('Felle', 500), ('Skihelm', 400),
    ('Gletscherbrille', 50), ('Erste-Hilfe-Kit', 250), ('Stirnlampe', 80), ('Hygiene-Kit', 150)
]

BASIS_HOCHTOUR = [
    ('Bergstiefel (C)', 1400), ('Tourenhose', 500), ('Merino Shirt', 200),
    ('Fleece Midlayer', 300), ('Hardshell Jacke', 300), ('Hardshell Hose', 400),
    ('Gletscherbrille', 50), ('Dünne Handschuhe', 60), ('Mütze', 50),
    ('Steigeisen', 850), ('Eispickel', 450), ('Kletterhelm', 300), ('Klettergurt', 350),
    ('Erste-Hilfe-Kit', 250), ('Stirnlampe', 80), ('Hygiene-Kit', 150)
]

# Zusatz-Module
MODUL_KLETTERSTEIG = [('Klettersteigset', 500), ('Klettergurt', 350), ('Kletterhelm', 300)]
MODUL_SCHLAFEN_HUETTE = [('Seiden-Inlet', 130), ('Hüttenschuhe', 200)]
MODUL_SCHLAFEN_ZELT_SOMMER = [('Zelt (Anteil)', 1200), ('Isomatte (Schaum)', 350), ('Sommerschlafsack', 600)]
MODUL_SCHLAFEN_ZELT_WINTER = [('Zelt (Winter/Anteil)', 1500), ('Isomatte (Winter)', 600), ('Daunenschlafsack (-5)', 1000)]
MODUL_TECH_KIT = [('Power-Kit (Bank+Kabel)', 250)]

# --- 2. WIZARD UI (Sequentiell) ---

# Schritt 1: Basis
c1, c2 = st.columns(2)
with c1:
    tour_art = st.selectbox("1. Art der Tour", ["Wandern", "Skitour", "Hochtour"])
with c2:
    tage = st.number_input("2. Anzahl Tage", 1, 20, 1)

# Schritt 2: Bedingungen
c3, c4 = st.columns(2)
with c3:
    temp_bereich = st.select_slider("3. Temperatur", options=["Warm (>15°C)", "Kühl (0-15°C)", "Kalt (<0°C)"])
with c4:
    # Logik: Tagestour braucht keine Übernachtung
    if tage > 1:
        schlafen = st.selectbox("4. Übernachtung", ["Hütte", "Zelt"])
    else:
        schlafen = "Keine (Tagestour)"
        st.info("Tagestour (Keine Übernachtung)")

# Schritt 3: Extras
col_ex1, col_ex2, col_ex3 = st.columns(3)
with col_ex1:
    # Klettersteig Logik
    ks_disabled = (tour_art == "Hochtour") # Bei Hochtour immer dabei
    ks_value = True if tour_art == "Hochtour" else False
    if not ks_disabled:
        ks_value = st.checkbox("Klettersteig geplant?")
    else:
        st.markdown("✅ *Klettersteig (Inkl.)*")

with col_ex2:
    autark = st.checkbox("Selbstverpflegung (Kochen)?")

with col_ex3:
    # Wasserfilter & Co
    wasser_liter = st.slider("Wasser (L)", 0.5, 4.0, 2.0, 0.5)


# --- 3. LOGIK-ENGINE (Generierung) ---
final_list = [] # Liste aus Tupeln (Name, Gewicht)

# A. Basis laden
if tour_art == "Wandern":
    final_list.extend(BASIS_WANDERN)
elif tour_art == "Skitour":
    final_list.extend(BASIS_SKITOUR)
elif tour_art == "Hochtour":
    final_list.extend(BASIS_HOCHTOUR)

# B. Klettersteig Add-on (Nur wenn nicht Hochtour, da dort schon Basics drin sind, aber Set fehlt evtl)
if ks_value:
    # Prüfen ob Helm/Gurt schon da sind (um Dopplung zu vermeiden)
    current_names = [x[0] for x in final_list]
    for item in MODUL_KLETTERSTEIG:
        if item[0] not in current_names:
            final_list.append(item)

# C. Temperatur Modifikationen
if temp_bereich == "Kalt (<0°C)":
    final_list.append(('Daunenjacke (Iso)', 350))
    if tour_art == "Wandern": # Bei Ski/Hochtour schon dabei
        final_list.append(('Dicke Handschuhe', 150))
        final_list.append(('Mütze', 50))
elif temp_bereich == "Kühl (0-15°C)":
    # Evtl. leichte Handschuhe
    pass 

# D. Übernachtung
if tage > 1:
    final_list.extend(MODUL_TECH_KIT) # Strom braucht man fast immer
    
    # Wechselwäsche (Simpel: ab 3 Tagen 1 Shirt extra)
    if tage >= 3:
        final_list.append(('Wechselshirt Merino', 200))
        final_list.append(('Wechselsocken', 80))

    if schlafen == "Hütte":
        final_list.extend(MODUL_SCHLAFEN_HUETTE)
    elif schlafen == "Zelt":
        if temp_bereich == "Warm (>15°C)":
            final_list.extend(MODUL_SCHLAFEN_ZELT_SOMMER)
        else:
            final_list.extend(MODUL_SCHLAFEN_ZELT_WINTER)

# E. Verpflegung (Autark)
final_list.append(('Wasser (Inhalt)', int(wasser_liter * 1000)))
# Behälter
kap = 0
while kap < wasser_liter:
    final_list.append(('Trinkflasche/Blase', 100)) # Pauschalgewicht Behälter
    kap += 1.0

if autark:
    final_list.append(('Kocher & Topf', 400))
    final_list.append(('Löffel & Messer', 50))
    # Gas Logik
    if tage <= 6:
        final_list.append(('Gaskartusche 100g', 200))
    else:
        final_list.append(('Gaskartusche 230g', 380))
    # Essen (Pauschal 700g pro Tag)
    final_list.append(('Essen (Gesamt)', tage * 700))

# F. Rucksack-Wahl (Automatisch aus deinem Bestand)
pack_volumen_need = 0
# Heuristik für Volumen
if schlafen == "Zelt": pack_volumen_need += 25
if schlafen == "Hütte": pack_volumen_need += 10
if temp_bereich == "Kalt (<0°C)": pack_volumen_need += 10
if tour_art == "Skitour": pack_volumen_need += 10 # Felle/Helm brauchen Platz
pack_volumen_need += (tage * 2) # Essen/Kleidung pro Tag

chosen_pack = {}
if tour_art == "Skitour" or (tage == 1 and pack_volumen_need < 25):
    chosen_pack = MY_PACKS['Skitour/Day']
elif tage > 1 and schlafen == "Zelt":
    chosen_pack = MY_PACKS['Trekking'] # 50+10L
else:
    chosen_pack = MY_PACKS['Tour'] # 40L

final_list.append((chosen_pack['Name'], chosen_pack['Gewicht']))


# --- 4. ZUORDNUNG "AM KÖRPER" (Interaktiv) ---
st.divider()
st.subheader("🎒 Packliste & Gewicht")

# Wir erstellen eine Liste aller Namen für die Auswahlbox
all_item_names = [item[0] for item in final_list]

# Standard-Auswahl definieren (Was hat man meistens an?)
default_worn = [
    'Wanderschuhe', 'Bergstiefel (C)', 'Skischuhe', 'Tourenhose', 'Tourenhose (Softshell)', 
    'Wanderhose', 'Merino Shirt', 'Wanderstöcke', 'Klettergurt'
]
# Filtern, welche davon in der aktuellen Liste sind
preselect = [name for name in all_item_names if name in default_worn]

# Der User entscheidet final
worn_selection = st.multiselect(
    "Was trägst du am Körper? (Wird nicht im Rucksack gewogen)",
    options=all_item_names,
    default=preselect
)

# --- 5. BERECHNUNG & AUSGABE ---

rucksack_items = []
worn_items_list = []

total_weight = 0
pack_weight = 0

for name, weight in final_list:
    total_weight += weight
    
    # Check if item name is in the list of items appearing multiple times (like Bottles)
    # Problem: 'Trinkflasche/Blase' appears multiple times. Multiselect handles unique strings.
    # Fix: Wir summieren einfach basierend auf Namen.
    # Da die UI Selection auf Namen basiert, markieren wir Items als "Worn" wenn ihr Name in der Selection ist.
    
    if name in worn_selection:
        worn_items_list.append({'Item': name, 'Gramm': weight})
    else:
        rucksack_items.append({'Item': name, 'Gramm': weight})
        pack_weight += weight

# DataFrame für Checklist
df_pack = pd.DataFrame(rucksack_items)
df_pack['Check'] = False # Checkbox Spalte

c_res1, c_res2, c_res3 = st.columns(3)
c_res1.metric("🎒 Rucksack", f"{pack_weight/1000:.2f} kg")
c_res2.metric("👕 Am Körper", f"{(total_weight - pack_weight)/1000:.2f} kg")
c_res3.metric("📦 Rucksack-Wahl", chosen_pack['Name'])

st.write("### Deine Packliste")
if not df_pack.empty:
    # Data Editor für Checkboxen
    st.data_editor(
        df_pack, 
        column_config={
            "Check": st.column_config.CheckboxColumn("Gepackt?", default=False, width="small"),
            "Item": st.column_config.TextColumn("Ausrüstung"),
            "Gramm": st.column_config.NumberColumn("Gewicht (g)", format="%d g")
        },
        hide_index=True,
        use_container_width=True
    )
else:
    st.success("Rucksack ist leer! (Alles am Körper?)")

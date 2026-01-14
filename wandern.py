import streamlit as st
import pandas as pd
import altair as alt # Für schicke Diagramme

# --- TITEL & KONFIGURATION ---
st.set_page_config(page_title="Outdoor Gear Planner V3", page_icon="🏔️", layout="wide")
st.title("🏔️ Ultimate Outdoor Gear Planner V3")
st.caption("Mit Verbrauchs-Rechner (Essen, Wasser, Brennstoff)")

# --- 1. DATENBANK (Erweitert um Gas & Wasserbehälter) ---
data = {
    'Name': [
        'Merino Shirt', 'Synthetik Shirt', 'Fleece Pulli', 'Daunenjacke', 'Hardshell Jacke', 
        'Wanderhose', 'Softshellhose', 'Hardshellhose',
        'Leichte Wanderschuhe', 'Bergstiefel (Steigeisenfest)', 'Skischuhe',
        'Rucksack 40L', 'Rucksack 60L', 'Lawinenrucksack',
        'Daunenschlafsack -5°C', 'Sommerschlafsack +10°C', 
        'Isomatte (R-Wert 4)', 'Schaummatte (R-Wert 2)',
        'Zelt 2P', 'Biwacksack',
        'Gaskocher', 'Topfset Titan', 'Spork', 'Klappspaten',
        'Steigeisen', 'Eispickel', 'Klettersteigset', 'Helm', 'LVS-Set', 'Wanderstöcke',
        # NEU: Verbrauch & Behälter
        'Gaskartusche Klein (100g Gas)', 'Gaskartusche Mittel (230g Gas)', 
        'Wasserflasche 1L (Plastik)', 'Trinkblase 2L'
    ],
    'Kategorie': [
        'Baselayer', 'Baselayer', 'Midlayer', 'Isolation', 'Shell', 
        'Hose', 'Hose', 'Hose',
        'Schuhe', 'Schuhe', 'Schuhe',
        'Rucksack', 'Rucksack', 'Rucksack',
        'Schlafen_Sack', 'Schlafen_Sack', 
        'Schlafen_Matte', 'Schlafen_Matte',
        'Schlafen_Shelter', 'Schlafen_Shelter',
        'Küche', 'Küche', 'Küche', 'Hygiene',
        'Technik', 'Technik', 'Technik', 'Technik', 'Technik', 'Technik',
        'Verbrauch_Gas', 'Verbrauch_Gas',
        'Wasser_Behaelter', 'Wasser_Behaelter'
    ],
    'Gewicht_g': [
        150, 130, 300, 350, 250, 
        400, 500, 300,
        800, 1400, 3000,
        1200, 1600, 2500,
        900, 500, 
        600, 300,
        1500, 300,
        100, 200, 15, 150,
        800, 400, 500, 300, 700, 400,
        200, 380, # Bruttogewicht der Kartuschen (Inhalt + Stahl)
        40, 150
    ],
    'Temp_Min': [20, 25, 15, 5, 99, 99, 5, -10, 99, 99, 99, 99, 99, 99, -5, 10, -5, 10, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
    'Tags': ['Wandern']*34 # Vereinfacht für dieses Beispiel
}
df = pd.DataFrame(data)

# --- 2. SIDEBAR - EINGABEN ---
with st.sidebar:
    st.header("🗺️ Tour-Parameter")
    dauer_tage = st.number_input("Dauer (Tage)", min_value=1, value=3)
    temp = st.slider("Tiefsttemperatur (°C)", -20, 30, 10)
    wetter = st.selectbox("Wetter", ["Sonnig", "Wechselhaft", "Regen/Schnee"])
    
    tour_art = st.multiselect(
        "Art der Tour",
        ["Wandern", "Hochtour (Gletscher)", "Klettersteig", "Skitour"],
        default=["Wandern"]
    )
    
    st.header("🍱 Essen & Trinken")
    kochen = st.checkbox("Selbstversorgung (Kochen)?", value=True)
    wasser_kapazitaet = st.slider("Wasser-Kapazität (Liter)", 1.0, 4.0, 2.0, step=0.5)
    essen_pro_tag = st.slider("Essen pro Tag (Gramm)", 500, 1000, 700, help="Ultralight: 600g, Normal: 800g")


# --- 3. LOGIK-ENGINE ---
packliste = [] 
worn_items = []
consumables = [] # Neue Liste für Essen/Wasser/Gas-INHALT

# Hilfsfunktion (Repariert!)
def add_item(filter_col, filter_val, sort_col='Gewicht_g', asc=True, target_list=packliste, menge=1, name_contains=None):
    candidates = df[df[filter_col] == filter_val]
    if name_contains:
        candidates = candidates[candidates['Name'].str.contains(name_contains)]
    
    if not candidates.empty:
        best_item = candidates.sort_values(by=sort_col, ascending=asc).iloc[0].to_dict()
        best_item['Menge'] = menge
        # Wir markieren Items als 'Gear', 'Worn' oder 'Consumable' für die Anzeige
        if target_list == consumables:
            best_item['Typ'] = 'Verbrauch'
        elif target_list == worn_items:
            best_item['Typ'] = 'Am Körper'
        else:
            best_item['Typ'] = 'Ausrüstung'
        
        target_list.append(best_item)

# --- A. STANDARD EQUIPMENT (Wie vorher) ---
# Schuhe
if "Skitour" in tour_art:
    add_item('Kategorie', 'Schuhe', name_contains="Skischuhe", target_list=worn_items)
elif "Hochtour (Gletscher)" in tour_art:
    add_item('Kategorie', 'Schuhe', name_contains="Bergstiefel", target_list=worn_items)
else:
    add_item('Kategorie', 'Schuhe', name_contains="Leichte", target_list=worn_items)

# Kleidung
add_item('Kategorie', 'Hose', name_contains="Softshell" if temp < 5 else "Wanderhose", target_list=worn_items)
add_item('Kategorie', 'Baselayer', name_contains="Synthetik" if temp > 15 else "Merino", target_list=worn_items)

# Wechselwäsche
if dauer_tage > 1:
    menge_shirts = int(dauer_tage / 3)
    if menge_shirts >= 1:
        add_item('Kategorie', 'Baselayer', name_contains="Merino", menge=menge_shirts)

if temp < 15: add_item('Kategorie', 'Midlayer')
if temp < 5: add_item('Kategorie', 'Isolation')
if wetter != "Sonnig" or temp < 5: add_item('Kategorie', 'Shell')

# Schlafen
add_item('Kategorie', 'Schlafen_Sack', sort_col='Gewicht_g') # Vereinfacht: Nimmt leichtesten
add_item('Kategorie', 'Schlafen_Matte')
add_item('Kategorie', 'Schlafen_Shelter', name_contains="Zelt")

# Technik
if "Hochtour (Gletscher)" in tour_art:
    add_item('Kategorie', 'Technik', name_contains="Steigeisen")
    add_item('Kategorie', 'Technik', name_contains="Pickel")
    add_item('Kategorie', 'Technik', name_contains="Helm")
add_item('Kategorie', 'Hygiene', name_contains="Klappspaten")
add_item('Kategorie', 'Technik', name_contains="Wanderstöcke", target_list=worn_items)

# --- B. KÜCHE & VERBRAUCH (NEU!) ---

if kochen:
    # 1. Hardware
    add_item('Kategorie', 'Küche', name_contains="Gaskocher")
    add_item('Kategorie', 'Küche', name_contains="Topf")
    add_item('Kategorie', 'Küche', name_contains="Spork")
    
    # 2. Brennstoff Berechnung
    # Annahme: 25g Gas pro Tag für Wasser kochen (Morgens Kaffee, Abends Essen)
    gas_bedarf = dauer_tage * 25 
    
    # Wähle Kartusche
    if gas_bedarf <= 100:
        add_item('Kategorie', 'Verbrauch_Gas', name_contains="100g")
    else:
        # Wenn mehr als 100g, nimm die mittlere (oder mehrere, Logik vereinfacht)
        add_item('Kategorie', 'Verbrauch_Gas', name_contains="230g")

# --- C. ESSEN & WASSER ---

# 1. Wasser-Behälter (Das Leergewicht gehört zum Base Weight)
if wasser_kapazitaet <= 1.0:
    add_item('Kategorie', 'Wasser_Behaelter', name_contains="Flasche", menge=1)
else:
    # Bei mehr als 1L nehmen wir eine Trinkblase
    add_item('Kategorie', 'Wasser_Behaelter', name_contains="Trinkblase")

# 2. Wasser Inhalt (Das Wasser selbst)
# Das fügen wir manuell zur consumables Liste hinzu, da es nicht in der DB steht
consumables.append({
    'Name': 'Wasser (Startfüllung)',
    'Kategorie': 'Verbrauch_Wasser',
    'Gewicht_g': wasser_kapazitaet * 1000, # 1L = 1000g
    'Menge': 1,
    'Typ': 'Verbrauch'
})

# 3. Essen
consumables.append({
    'Name': 'Essen / Snacks',
    'Kategorie': 'Verbrauch_Essen',
    'Gewicht_g': essen_pro_tag, 
    'Menge': dauer_tage,
    'Typ': 'Verbrauch'
})

# --- D. RUCKSACK (Am Schluss, um Volumen zu schätzen) ---
# Hier stark vereinfachte Logik
rucksack_typ = "40L"
if dauer_tage > 3 or (kochen and dauer_tage > 1):
    rucksack_typ = "60L"
add_item('Kategorie', 'Rucksack', name_contains=rucksack_typ)


# --- 4. BERECHNUNG & VISUALISIERUNG ---

# Alle Listen zusammenführen für Auswertung
all_items = packliste + worn_items + consumables
df_all = pd.DataFrame(all_items)

# Gewicht berechnen
df_all['Total_Gewicht_g'] = df_all['Gewicht_g'] * df_all['Menge']

base_weight = df_all[(df_all['Typ'] == 'Ausrüstung')]['Total_Gewicht_g'].sum()
consumable_weight = df_all[(df_all['Typ'] == 'Verbrauch')]['Total_Gewicht_g'].sum()
worn_weight = df_all[(df_all['Typ'] == 'Am Körper')]['Total_Gewicht_g'].sum()
total_skin_out = base_weight + consumable_weight + worn_weight

# --- DASHBOARD ---
st.divider()

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("⚖️ Start-Gewicht (Total)", f"{total_skin_out/1000:.1f} kg")
c2.metric("🎒 Base Weight (Ausrüstung)", f"{base_weight/1000:.1f} kg", help="Nur Ausrüstung im Rucksack, ohne Essen/Wasser")
c3.metric("🥪 Verbrauch (Essen/Wasser)", f"{consumable_weight/1000:.1f} kg", help="Nimmt jeden Tag ab!")
c4.metric("👕 Worn Weight", f"{worn_weight/1000:.1f} kg")

# Diagramm (Donut Chart für Gewichtsverteilung)
chart_data = df_all.groupby('Typ')['Total_Gewicht_g'].sum().reset_index()
base = alt.Chart(chart_data).encode(theta=alt.Theta("Total_Gewicht_g", stack=True))
pie = base.mark_arc(outerRadius=120).encode(
    color=alt.Color("Typ"),
    order=alt.Order("Total_Gewicht_g", sort="descending"),
    tooltip=["Typ", "Total_Gewicht_g"]
)
text = base.mark_text(radius=140).encode(
    text=alt.Text("Total_Gewicht_g", format=".0f"),
    order=alt.Order("Total_Gewicht_g", sort="descending"),
    color=alt.value("black") 
)
st.write("### 📊 Gewichtsverteilung")
st.altair_chart(pie + text, use_container_width=True)


# Detail Tabellen
t1, t2, t3 = st.tabs(["🎒 Packliste (Rucksack)", "🥪 Verbrauch", "👕 Am Körper"])

with t1:
    st.dataframe(df_all[df_all['Typ']=='Ausrüstung'][['Menge', 'Name', 'Gewicht_g', 'Total_Gewicht_g']], use_container_width=True)

with t2:
    st.warning(f"Du startest mit {consumable_weight/1000:.1f} kg Essen & Wasser. Am letzten Tag sind davon fast 0 kg übrig.")
    st.dataframe(df_all[df_all['Typ']=='Verbrauch'][['Menge', 'Name', 'Gewicht_g', 'Total_Gewicht_g']], use_container_width=True)

with t3:
    st.dataframe(df_all[df_all['Typ']=='Am Körper'][['Menge', 'Name', 'Gewicht_g', 'Total_Gewicht_g']], use_container_width=True)

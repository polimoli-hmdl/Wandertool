import streamlit as st
import pandas as pd
import math
import altair as alt

# --- KONFIGURATION ---
st.set_page_config(page_title="Outdoor Gear Planner V6.2", page_icon="🏔️", layout="wide")
st.title("🏔️ Outdoor Gear Planner V6.2")
st.caption("Final Version: Stabilisierte Formatierung")

# --- 1. DATENBANK ---
data = {
    'Name': [
        # Rucksäcke
        'Tagesrucksack 25L', 'Tourenrucksack 45L', 'Trekkingrucksack 65L', 'Lawinenrucksack',
        
        # Kleidung (Körper)
        'Merino Shirt (Langarm)', 'Synthetik Shirt (Kurz)', 'Wanderhose', 'Hüttenschuhe',
        
        # Kleidung (Layer/Wetter)
        'Fleece (Midlayer)', 'Daunenjacke (Iso)', 'Hardshell Jacke', 
        'Leichte Regenhose', 'Alpine Hardshellhose',
        
        # Accessoires
        'Mütze & Handschuhe (Dünn)', 'Mütze & Handschuhe (Dick)', 
        'Sonnenbrille & Kappe', 'Gletscherbrille',
        
        # Schuhe
        'Trailrunner', 'Bergstiefel (B/C)', 'Skischuhe',
        
        # Schlafen
        'Daunenschlafsack -5°C', 'Sommerschlafsack +10°C', 'Seiden-Inlet',
        'Isomatte (R-Wert 4)', 'Schaummatte (R-Wert 2)',
        'Zelt 2P', 'Biwacksack',
        
        # Küche
        'Gaskocher (UL)', 'Topfset Titan', 'Löffel', 'Wasserfilter',
        'Gaskartusche 100g', 'Gaskartusche 230g',
        'Wasserflasche 1L', 'Trinkblase 2L', 'Trinkblase 3L',
        
        # Technik & Safety
        'Erste-Hilfe-Set', 'Stirnlampe', 'Powerbank 10k', 'Powerbank 20k', 'Ladegerät',
        'Steigeisen', 'Eispickel', 'Klettersteigset', 'Helm', 'LVS-Set', 'Wanderstöcke',
        'Steigfelle (Ski)', 'Klappspaten',
        'Seil 30m', 'Seil 50m',
        
        # Hygiene
        'Kulturbeutel (UL)', 'Mikrofaser-Handtuch'
    ],
    'Kategorie': [
        'Rucksack', 'Rucksack', 'Rucksack', 'Rucksack',
        'Baselayer', 'Baselayer', 'Hose', 'Schuhe_Camp',
        'Midlayer', 'Isolation', 'Shell', 
        'Hose_Regen', 'Hose_Regen',
        'Headwear', 'Headwear', 
        'Eyewear', 'Eyewear',
        'Schuhe', 'Schuhe', 'Schuhe',
        'Schlafen_Sack', 'Schlafen_Sack', 'Schlafen_Sack',
        'Schlafen_Matte', 'Schlafen_Matte',
        'Schlafen_Shelter', 'Schlafen_Shelter',
        'Küche', 'Küche', 'Küche', 'Küche',
        'Verbrauch_Gas', 'Verbrauch_Gas',
        'Wasser_Behaelter', 'Wasser_Behaelter', 'Wasser_Behaelter',
        'Safety', 'Safety', 'Elektronik', 'Elektronik', 'Elektronik',
        'Technik', 'Technik', 'Technik', 'Technik', 'Technik', 'Technik',
        'Technik', 'Hygiene',
        'Seil', 'Seil',
        'Hygiene', 'Hygiene'
    ],
    'Gewicht_g': [
        700, 1200, 1700, 2500,
        200, 130, 400, 200,
        300, 350, 300, 150, 450,
        100, 250,
        80, 50,
        700, 1400, 3000,
        900, 600, 130,
        600, 350, 1400, 250,
        80, 150, 15, 80, 200, 380,
        40, 150, 170,
        250, 80, 200, 400, 80,
        850, 450, 500, 300, 700, 400,
        500, 150,
        2100, 3500,
        150, 80
    ]
}
df = pd.DataFrame(data)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("🥾 Tour Konfigurator")
    dauer_tage = st.number_input("Dauer (Tage)", 1, 30, 3) 
    temp = st.slider("Tiefsttemperatur (°C)", -25, 30, 10)
    
    tour_art = st.multiselect("Tour-Typ", 
                             ["Wandern", "Hochtour", "Klettersteig", "Skitour"],
                             default=["Wandern"])
    
    # Bedingte Abfragen
    schlafen_typ = "Keine (Tagestour)"
    if dauer_tage > 1:
        schlafen_typ = st.selectbox("Übernachtung", ["Hütte", "Zelt/Biwak"])
    
    st.subheader("⚙️ Details")
    strom_zugang = False
    if dauer_tage > 1:
        strom_zugang = st.checkbox("Strom verfügbar?", value=False)
        
    seil_wahl = "Kein Seil"
    if "Hochtour" in tour_art or "Klettersteig" in tour_art:
        seil_wahl = st.selectbox("Seil", ["Kein Seil", "30m", "50m"])
        
    mit_filter = st.checkbox("Wasserfilter?", value=True)
    wasser_kap = st.slider("Wasser (L)", 0.5, 5.0, 2.0, 0.5)

# --- 3. LOGIK ---
packliste, worn_items, consumables = [], [], []

def add(kategorie, name_part=None, target=packliste, menge=1):
    subset = df[df['Kategorie'] == kategorie]
    if name_part:
        subset = subset[subset['Name'].str.contains(name_part, case=False)]
    if not subset.empty:
        item = subset.sort_values('Gewicht_g').iloc[0].to_dict()
        item['Menge'] = menge
        # Typ setzen
        if target == worn_items: 
            item['Typ'] = 'Am Körper'
        elif target == consumables: 
            item['Typ'] = 'Verbrauch'
        else: 
            item['Typ'] = 'Ausrüstung'
        target.append(item)

# === A. BASICS ===
add('Safety', 'Erste-Hilfe', packliste)
add('Safety', 'Stirnlampe', packliste)
add('Technik', 'Wanderstöcke', worn_items)

# Sonnenbrille & Kopfbedeckung
if "Hochtour" in tour_art or "Skitour" in tour_art:
    add('Eyewear', 'Gletscher', worn_items)
else:
    add('Eyewear', 'Sonnenbrille', worn_items)

if temp < 5 or "Skitour" in tour_art:
    add('Headwear', 'Dick', packliste)
else:
    add('Headwear', 'Dünn', packliste)

# === B. KLEIDUNG (Hier war der Fehler!) ===
if "Skitour" in tour_art:
    add('Schuhe', 'Skischuhe', worn_items)
elif "Hochtour" in tour_art:
    add('Schuhe', 'Bergstiefel', worn_items)
else:
    add('Schuhe', 'Trailrunner', worn_items)

add('Hose', 'Wanderhose', worn_items)

if temp < 15:
    add('Baselayer', 'Merino', worn_items)
else:
    add('Baselayer', 'Synthetik', worn_items)

if "Hochtour" in tour_art or "Skitour" in tour_art:
    add('Hose_Regen', 'Alpine', packliste)
else:
    add('Hose_Regen', 'Leichte', packliste)

add('Shell', 'Hardshell', packliste)

if temp < 15:
    add('Midlayer', 'Fleece', packliste)
if temp < 5:
    add('Isolation', 'Daunenjacke', packliste)

if dauer_tage > 1:
    add('Schuhe_Camp', 'Hüttenschuhe', packliste)
    add('Hygiene', 'Kulturbeutel', packliste)
    add('Hygiene', 'Handtuch', packliste)
    needed = math.ceil(dauer_tage / 2) - 1
    if needed > 0:
        add('Baselayer', 'Merino', packliste, menge=needed)

# === C. TECHNIK & ALPINE ===
if "Skitour" in tour_art:
    add('Technik', 'LVS', packliste)
    add('Technik', 'Felle', packliste)
    add('Technik', 'Helm', packliste)

if "Hochtour" in tour_art:
    add('Technik', 'Steigeisen', packliste)
    add('Technik', 'Eispickel', packliste)
    add('Technik', 'Helm', packliste)

if "Klettersteig" in tour_art:
    add('Technik', 'Klettersteigset', packliste)
    if not any(x['Name'] == 'Helm' for x in packliste):
        add('Technik', 'Helm', packliste)

if seil_wahl != "Kein Seil":
    add('Seil', seil_wahl.split(' ')[0], packliste)

if dauer_tage > 1:
    if strom_zugang:
        add('Elektronik', 'Ladegerät', packliste)
    else:
        if dauer_tage > 4:
            add('Elektronik', '20k', packliste)
        else:
            add('Elektronik', '10k', packliste)

# === D. KÜCHE & WASSER ===
if mit_filter:
    add('Küche', 'Filter', packliste)

fill = 0
while fill < wasser_kap:
    if wasser_kap - fill >= 2.0:
        add('Wasser_Behaelter', 'Trinkblase 2L', packliste)
        fill += 2
    else:
        add('Wasser_Behaelter', 'Flasche', packliste)
        fill += 1

if schlafen_typ == "Zelt/Biwak": 
    add('Küche', 'Kocher', packliste)
    add('Küche', 'Topf', packliste)
    add('Küche', 'Löffel', packliste)
    gas_g = dauer_tage * 14
    if gas_g <= 100:
        add('Verbrauch_Gas', '100g', packliste)
    else:
        add('Verbrauch_Gas', '230g', packliste)

# === E. SCHLAFEN ===
if dauer_tage > 1:
    if schlafen_typ == "Hütte":
        add('Schlafen_Sack', 'Inlet', packliste)
    else:
        add('Schlafen_Shelter', 'Zelt', packliste)
        
        if temp < 5:
            add('Schlafen_Matte', 'Isomatte', packliste)
            add('Schlafen_Sack', 'Daunen', packliste)
        else:
            add('Schlafen_Matte', 'Schaummatte', packliste)
            add('Schlafen_Sack', 'Sommer', packliste)
            
        add('Hygiene', 'Klappspaten', packliste)

# === F. RUCKSACK ===
if "Skitour" in tour_art:
    add('Rucksack', 'Lawinenrucksack', packliste)
else:
    has_tent = any('Zelt' in x['Name'] for x in packliste)
    has_rope = any('Seil' in x['Name'] for x in packliste)
    
    if dauer_tage == 1:
        if has_rope or "Hochtour" in tour_art:
            add('Rucksack', 'Tourenrucksack', packliste)
        else:
            add('Rucksack', 'Tagesrucksack', packliste)     
    else:
        if has_tent or dauer_tage > 5:
            add('Rucksack', 'Trekkingrucksack', packliste)
        else:
            add('Rucksack', 'Tourenrucksack', packliste)

# === G. VERBRAUCH ===
consumables.append({
    'Name': 'Wasser (Start)', 
    'Kategorie': 'Verbrauch_Wasser', 
    'Gewicht_g': wasser_kap * 1000, 
    'Menge': 1, 
    'Typ': 'Verbrauch'
})

if dauer_tage > 0:
    consumables.append({
        'Name': 'Essen', 
        'Kategorie': 'Verbrauch_Essen',
        'Gewicht_g': 700, 
        'Menge': dauer_tage, 
        'Typ': 'Verbrauch'
    })

# === OUTPUT ===
df_res = pd.DataFrame(packliste + worn_items + consumables)

if not df_res.empty:
    df_res['Gesamt'] = df_res['Gewicht_g'] * df_res['Menge']
    
    st.divider()
    cols = st.columns(4)
    cols[0].metric("🎒 Rucksack", f"{df_res[df_res['Typ']=='Ausrüstung']['Gesamt'].sum()/1000:.2f} kg")
    cols[1].metric("💧 Verbrauch", f"{df_res[df_res['Typ']=='Verbrauch']['Gesamt'].sum()/1000:.2f} kg")
    cols[2].metric("👕 Am Körper", f"{df_res[df_res['Typ']=='Am Körper']['Gesamt'].sum()/1000:.2f} kg")
    cols[3].metric("⚙️ System Total", f"{df_res['Gesamt'].sum()/1000:.2f} kg")
    
    t1, t2 = st.tabs(["Liste", "Verteilung"])
    with t1:
        st.dataframe(df_res[['Menge', 'Name', 'Typ', 'Gesamt']], use_container_width=True)
    with t2:
        c = alt.Chart(df_res).mark_arc().encode(
            theta='Gesamt', color='Typ', tooltip=['Name', 'Gesamt']
        )
        st.altair_chart(c, use_container_width=True)
else:
    st.warning("Keine Ausrüstung ausgewählt.")

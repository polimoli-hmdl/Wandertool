import streamlit as st
import pandas as pd
import math

# --- KONFIGURATION ---
st.set_page_config(page_title="Outdoor Gear Planner V6 (Final)", page_icon="🏔️", layout="wide")
st.title("🏔️ Outdoor Gear Planner V6 (Complete)")
st.caption("Mit korrigierter Logik für Tagestouren, Safety & Hygiene")

# --- 1. DATENBANK (Vollständig) ---
data = {
    'Name': [
        # Rucksäcke
        'Tagesrucksack 25L', 'Tourenrucksack 45L', 'Trekkingrucksack 65L', 'Lawinenrucksack',
        
        # Kleidung (Körper)
        'Merino Shirt (Langarm)', 'Synthetik Shirt (Kurz)', 'Wanderhose', 'Hüttenschuhe',
        
        # Kleidung (Layer/Wetter)
        'Fleece (Midlayer)', 'Daunenjacke (Iso)', 'Hardshell Jacke', 
        'Leichte Regenhose', 'Alpine Hardshellhose',
        
        # Accessoires (NEU)
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
        
        # Hygiene (NEU)
        'Kulturbeutel (UL: Zahnbürste/Paste/Mini-Seife)', 'Mikrofaser-Handtuch'
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
        700, 1200, 1700, 2500, # Rucksäcke
        200, 130, 400, 200, # Kleidung Base
        300, 350, 300, 150, 450, # Layers
        100, 250, # Handschuhe
        80, 50, # Brillen
        700, 1400, 3000, # Schuhe
        900, 600, 130, # Schlafsäcke
        600, 350, 1400, 250, # Matten/Zelt
        80, 150, 15, 80, 200, 380, # Küche
        40, 150, 170, # Wasser
        250, 80, 200, 400, 80, # Safety/Elektronik
        850, 450, 500, 300, 700, 400, # Alpine Gear
        500, 150, # Felle, Spaten
        2100, 3500, # Seile
        150, 80 # Hygiene Kit
    ]
}
df = pd.DataFrame(data)

# --- 2. SIDEBAR ---
with st.sidebar:
    st.header("🥾 Tour Konfigurator")
    dauer_tage = st.number_input("Dauer (Tage)", 1, 30, 1) # Default auf 1 zum Testen
    temp = st.slider("Tiefsttemperatur (°C)", -25, 30, 10)
    
    tour_art = st.multiselect("Tour-Typ", 
                             ["Wandern", "Hochtour", "Klettersteig", "Skitour"],
                             default=["Wandern"])
    
    # Bedingte Abfragen (erscheinen nur wenn nötig)
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
        if target == worn_items: item['Typ'] = 'Am Körper'
        elif target == consumables: item['Typ'] = 'Verbrauch'
        else: item['Typ'] = 'Ausrüstung'
        target.append(item)

# === A. BASICS (IMMER DABEI) ===
add('Safety', 'Erste-Hilfe', packliste)
add('Safety', 'Stirnlampe', packliste)
add('Technik', 'Wanderstöcke', worn_items)

# Sonnenbrille & Kopfbedeckung
if "Hochtour" in tour_art or "Skitour" in tour_art:
    add('Eyewear', 'Gletscher', worn_items) # Gletscherbrille
else:
    add('Eyewear', 'Sonnenbrille', worn_items)

if temp < 5 or "Skitour" in tour_art:
    add('Headwear', 'Dick', packliste) # Mütze & Handschuhe Dick
else:
    add('Headwear', 'Dünn', packliste)

# === B. KLEIDUNG ===
# Schuhe
if "Skitour" in tour_art: add('Schuhe', 'Skischuhe', worn_items)
elif "Hochtour" in tour_art: add('Schuhe', 'Bergstiefel', worn_items)
else: add('Schuhe', 'Trailrunner', worn_items)

# Hose & Shirts
add('Hose', 'Wanderhose', worn_items)
add('Baselayer', 'Merino' if temp < 15 else 'Synthetik', worn_items)

if "Hochtour" in tour_art or "Skitour" in tour_art:
    add('Hose_Regen', 'Alpine', packliste)
else:
    add('Hose_Regen', 'Leichte', packliste)

# Layering
add('Shell', 'Hardshell', packliste) # Immer Wind/Regenschutz
if temp < 15: add('Midlayer', 'Fleece', packliste)
if temp < 5: add('Isolation', 'Daunenjacke', packliste)

# Wechselwäsche & Camp (Nur Mehrtagestouren)
if dauer_tage > 1:
    add('Schuhe_Camp', 'Hüttenschuhe', packliste)
    add('Hygiene', 'Kulturbeutel', packliste)
    add('Hygiene', 'Handtuch', packliste)
    
    needed = math.ceil(dauer_tage / 2) - 1
    if needed > 0: add('Baselayer', 'Merino', packliste, menge=needed)
else:
    # Tagestour: Evtl nur Taschentücher, hier vereinfacht nix extra
    pass

# === C. TECHNIK & ALPINE ===
if "Skitour" in tour_art:
    add('Technik', 'LVS', packliste)
    add('Technik', 'Felle', packliste) # NEU: Felle
    add('Technik', 'Helm', packliste)  # NEU: Skihelm

if "Hochtour" in tour_art:
    add('Technik', 'Steigeisen', packliste)
    add('Technik', 'Eispickel', packliste)
    add('Technik', 'Helm', packliste)

if "Klettersteig" in tour_art:
    add('Technik', 'Klettersteigset', packliste)
    # Helm Check (vermeidet doppelte Helme)
    if not any(x['Name'] == 'Helm' for x in packliste):
        add('Technik', 'Helm', packliste)

if seil_wahl != "Kein Seil":
    add('Seil', seil_wahl.split(' ')[0], packliste)

# Strom
if dauer_tage > 1:
    if strom_zugang: add('Elektronik', 'Ladegerät', packliste)
    else: add('Elektronik', '20k' if dauer_tage > 4 else '10k', packliste)

# === D. KÜCHE & WASSER ===
if mit_filter: add('Küche', 'Filter', packliste)

# Behälter Logik
fill = 0
while fill < wasser_kap:
    if wasser_kap - fill >= 2.0:
        add('Wasser_Behaelter', 'Trinkblase 2L', packliste); fill += 2
    else:
        add('Wasser_Behaelter', 'Flasche', packliste); fill += 1

# Kochen (Nur bei Zelt oder wenn gewollt, hier vereinfacht an Zelt gekoppelt)
if schlafen_typ == "Zelt/Biwak" or (dauer_tage == 1 and False): # Tagestour kocht man meist nicht
    add('Küche', 'Kocher', packliste)
    add('Küche', 'Topf', packliste)
    add('Küche', 'Löffel', packliste)
    
    gas_g = dauer_tage * 14
    add('Verbrauch_Gas', '100g' if gas_g <= 100 else '230g', packliste)

# === E. SCHLAFEN (Nur Mehrtages) ===
if dauer_tage > 1:
    if schlafen_typ == "Hütte":
        add('Schlafen_Sack', 'Inlet', packliste)
    else:
        add('Schlafen_Shelter', 'Zelt', packliste)
        add('Schlafen_Matte', 'Isomatte' if temp < 5 else 'Schaummatte', packliste)
        add('Schlafen_Sack', 'Daunen' if temp < 5 else 'Sommer', packliste)
        add('Hygiene', 'Klappspaten', packliste) # Toilette draußen

# === F. RUCKSACK WAHL (Ganz am Ende) ===
# Logik: Volumen grob schätzen anhand der Items oder Szenario

# Sonderfall: Lawinenrucksack bei Skitour
if "Skitour" in tour_art:
    add('Rucksack', 'Lawinenrucksack', packliste)
else:
    # Volumen abschätzen
    has_tent = any('Zelt' in x['Name'] for x in packliste)
    has_rope = any('Seil' in x['Name'] for x in packliste)
    
    if dauer_tage == 1:
        # Tagestour
        if has_rope or "Hochtour" in tour_art: 
            add('Rucksack', 'Tourenrucksack 45L', packliste) # Viel Material
        else:
            add('Rucksack', 'Tagesrucksack 25L', packliste) # Leichte Wanderung
            
    else:
        # Mehrtagestour
        if has_tent or dauer_tage > 5:
            add('Rucksack', 'Trekkingrucksack 65L', packliste)
        else:
            # Hüttentour
            add('Rucksack', 'Tourenrucksack 45L', packliste)

# === VERBRAUCH ===
# 1. Wasser Startgewicht (Kapazität * 1000g)
consumables.append({
    'Name': 'Wasser (Start)', 
    'Kategorie': 'Wasser_Behaelter', # Damit keine leeren Felder entstehen
    'Gewicht_g': wasser_kap * 1000, 
    'Menge': 1, 
    'Typ': 'Verbrauch'
})

# 2. Essen (Nur wenn Dauer > 0)
if dauer_tage > 0:
    consumables.append({
        'Name': 'Essen', 
        'Kategorie': 'Verbrauch_Essen',
        'Gewicht_g': 700, # Fixwert oder Variable essen_pro_tag nutzen
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

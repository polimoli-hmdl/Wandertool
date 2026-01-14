import streamlit as st
import pandas as pd
import altair as alt

# --- TITEL & KONFIGURATION ---
st.set_page_config(page_title="Outdoor Gear Planner V4", page_icon="🏔️", layout="wide")
st.title("🏔️ Outdoor Gear Planner V4")
st.caption("Mit detaillierter Verpflegungs- und Wasserlogik")

# --- 1. DATENBANK (Erweitert um Wasserfilter) ---
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
        'Gaskartusche Klein (100g Gas)', 'Gaskartusche Mittel (230g Gas)', 
        'Wasserflasche 1L (Plastik)', 'Trinkblase 2L',
        # NEU:
        'Wasserfilter (Squeeze)', 'Chemie-Tabletten'
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
        'Wasser_Behaelter', 'Wasser_Behaelter',
        'Küche', 'Küche'
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
        200, 380, 
        40, 150,
        80, 20 # Filter leicht, Tabletten sehr leicht
    ],
    'Temp_Min': [20, 25, 15, 5, 99, 99, 5, -10, 99, 99, 99, 99, 99, 99, -5, 10, -5, 10, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99, 99],
    'Tags': ['Wandern']*36 
}
df = pd.DataFrame(data)

# --- 2. SIDEBAR - EINGABEN ---
with st.sidebar:
    st.header("🗺️ Tour-Parameter")
    dauer_tage = st.number_input("Dauer (Tage)", min_value=1, value=3)
    temp = st.slider("Erwartete Temp (°C)", -20, 35, 15)
    wetter = st.selectbox("Wetter", ["Sonnig", "Wechselhaft", "Regen/Schnee"])
    
    tour_art = st.multiselect(
        "Art der Tour",
        ["Wandern", "Hochtour (Gletscher)", "Klettersteig", "Skitour"],
        default=["Wandern"]
    )
    
    st.header("💧 Wasser & Quellen")
    # NEU: Wasserquellen Logik
    quellen_status = st.select_slider(
        "Verfügbarkeit Wasserquellen", 
        options=["Überall (Hütten/Bäche)", "Selten (1x tägl.)", "Keine / Trocken"]
    )
    mit_filter = st.checkbox("Wasserfilter einpacken?", value=True)
    
    # Automatische Empfehlung für Tragekapazität berechnen
    empfohlene_kapazitaet = 1.5 # Standard
    if quellen_status == "Selten (1x tägl.)":
        empfohlene_kapazitaet = 3.0
    elif quellen_status == "Keine / Trocken":
        empfohlene_kapazitaet = 4.0 # Mehr geht kaum zu tragen
    
    st.info(f"Empfohlene Trage-Kapazität für diese Quellen: {empfohlene_kapazitaet} L")
    wasser_kapazitaet = st.slider("Tatsächliche Kapazität (Liter)", 0.5, 6.0, empfohlene_kapazitaet, step=0.5)

    st.header("🍱 Essen & Kochen")
    kochen = st.checkbox("Gaskocher mitnehmen?", value=True)
    # Essen Slider
    essen_pro_tag = st.slider("Essen pro Tag (Gramm)", 400, 1200, 700)


# --- 3. GUIDES & BERECHNUNGEN (NEU) ---

# Kalorienbedarf Schätzung (Aktivitätsfaktor Wandern ca 1.5 - 2.0)
# Annahme: Durchschnittsmann/frau
kcal_base = 2500 # Aktivumsatz Minimum
if "Hochtour (Gletscher)" in tour_art or "Skitour" in tour_art:
    kcal_base += 1000 # Anstrengender

kcal_min = kcal_base * dauer_tage
kcal_comf = (kcal_base + 800) * dauer_tage # Mehr Snacks = bessere Laune

# Wasserbedarf (Trinken pro Tag, nicht Tragen!)
# Basis 2.5L + 0.1L pro Grad über 20°C
wasser_bedarf_daily = 2.5
if temp > 20:
    wasser_bedarf_daily += (temp - 20) * 0.1
if "Hochtour (Gletscher)" in tour_art:
    wasser_bedarf_daily += 0.5 # Höhe und trockene Luft

wasser_total_min = wasser_bedarf_daily * dauer_tage

# GUI Ausgabe Guide
with st.expander("📊 Verpflegungs-Guide (Deine Zielwerte)", expanded=True):
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("**🔥 Kalorien (Gesamttour)**")
        st.write(f"Existenzminimum: **{kcal_min:,.0f} kcal**")
        st.write(f"Komfort/Satt: **{kcal_comf:,.0f} kcal**")
        st.caption("Tipp: Nüsse und Schokolade haben die höchste Energiedichte.")
    with col_g2:
        st.markdown("**💧 Wasserbedarf (Trinken)**")
        st.write(f"Täglicher Bedarf ca.: **{wasser_bedarf_daily:.1f} Liter**")
        st.write(f"Muss getragen werden: **{wasser_kapazitaet} Liter** (Rest filtern/auffüllen)")
        if quellen_status == "Keine / Trocken" and wasser_kapazitaet < wasser_bedarf_daily:
            st.error("ACHTUNG: Du kannst weniger tragen als du pro Tag brauchst, aber es gibt keine Quellen!")

# --- 4. LOGIK-ENGINE ---
packliste = [] 
worn_items = []
consumables = []

def add_item(filter_col, filter_val, sort_col='Gewicht_g', asc=True, target_list=packliste, menge=1, name_contains=None):
    candidates = df[df[filter_col] == filter_val]
    if name_contains:
        candidates = candidates[candidates['Name'].str.contains(name_contains)]
    
    if not candidates.empty:
        best_item = candidates.sort_values(by=sort_col, ascending=asc).iloc[0].to_dict()
        best_item['Menge'] = menge
        if target_list == consumables:
            best_item['Typ'] = 'Verbrauch'
        elif target_list == worn_items:
            best_item['Typ'] = 'Am Körper'
        else:
            best_item['Typ'] = 'Ausrüstung'
        target_list.append(best_item)

# --- A. STANDARD EQUIPMENT ---
# Schuhe & Kleidung
if "Skitour" in tour_art:
    add_item('Kategorie', 'Schuhe', name_contains="Skischuhe", target_list=worn_items)
elif "Hochtour (Gletscher)" in tour_art:
    add_item('Kategorie', 'Schuhe', name_contains="Bergstiefel", target_list=worn_items)
else:
    add_item('Kategorie', 'Schuhe', name_contains="Leichte", target_list=worn_items)

add_item('Kategorie', 'Hose', name_contains="Softshell" if temp < 5 else "Wanderhose", target_list=worn_items)
add_item('Kategorie', 'Baselayer', name_contains="Synthetik" if temp > 15 else "Merino", target_list=worn_items)

if dauer_tage > 1:
    menge_shirts = int(dauer_tage / 3)
    if menge_shirts >= 1:
        add_item('Kategorie', 'Baselayer', name_contains="Merino", menge=menge_shirts)

if temp < 15: add_item('Kategorie', 'Midlayer')
if temp < 5: add_item('Kategorie', 'Isolation')
if wetter != "Sonnig" or temp < 5: add_item('Kategorie', 'Shell')

# Schlafen
add_item('Kategorie', 'Schlafen_Sack', sort_col='Gewicht_g')
add_item('Kategorie', 'Schlafen_Matte')
add_item('Kategorie', 'Schlafen_Shelter', name_contains="Zelt")

# Technik
if "Hochtour (Gletscher)" in tour_art:
    add_item('Kategorie', 'Technik', name_contains="Steigeisen")
    add_item('Kategorie', 'Technik', name_contains="Pickel")
    add_item('Kategorie', 'Technik', name_contains="Helm")
add_item('Kategorie', 'Hygiene', name_contains="Klappspaten")
add_item('Kategorie', 'Technik', name_contains="Wanderstöcke", target_list=worn_items)

# --- B. KÜCHE & VERBRAUCH ---

# NEU: Wasserfilter
if mit_filter:
    add_item('Kategorie', 'Küche', name_contains="Filter")

if kochen:
    add_item('Kategorie', 'Küche', name_contains="Gaskocher")
    add_item('Kategorie', 'Küche', name_contains="Topf")
    add_item('Kategorie', 'Küche', name_contains="Spork")
    
    # NEU: Gas Berechnung (14g pro Tag)
    gas_bedarf = dauer_tage * 14
    
    if gas_bedarf <= 100:
        add_item('Kategorie', 'Verbrauch_Gas', name_contains="100g")
    else:
        add_item('Kategorie', 'Verbrauch_Gas', name_contains="230g")

# --- C. ESSEN & WASSER BEHÄLTER ---

# Behälter-Logik (Flaschen vs Blase)
# Wir füllen auf bis die Kapazität erreicht ist
current_cap = 0
while current_cap < wasser_kapazitaet:
    if wasser_kapazitaet - current_cap >= 2.0:
        add_item('Kategorie', 'Wasser_Behaelter', name_contains="Trinkblase")
        current_cap += 2.0
    else:
        add_item('Kategorie', 'Wasser_Behaelter', name_contains="Flasche")
        current_cap += 1.0

# Wasser INHALT (Startgewicht)
consumables.append({
    'Name': 'Wasser (Startfüllung)',
    'Kategorie': 'Verbrauch_Wasser',
    'Gewicht_g': wasser_kapazitaet * 1000, 
    'Menge': 1,
    'Typ': 'Verbrauch'
})

# Essen
consumables.append({
    'Name': f'Essen ({essen_pro_tag}g/Tag)',
    'Kategorie': 'Verbrauch_Essen',
    'Gewicht_g': essen_pro_tag, 
    'Menge': dauer_tage,
    'Typ': 'Verbrauch'
})

# --- D. RUCKSACK ---
rucksack_typ = "40L"
if dauer_tage > 3 or (kochen and dauer_tage > 1) or wasser_kapazitaet > 3:
    rucksack_typ = "60L"
add_item('Kategorie', 'Rucksack', name_contains=rucksack_typ)


# --- 5. VISUALISIERUNG ---
st.divider()

all_items = packliste + worn_items + consumables
df_all = pd.DataFrame(all_items)
df_all['Total_Gewicht_g'] = df_all['Gewicht_g'] * df_all['Menge']

base_weight = df_all[(df_all['Typ'] == 'Ausrüstung')]['Total_Gewicht_g'].sum()
consumable_weight = df_all[(df_all['Typ'] == 'Verbrauch')]['Total_Gewicht_g'].sum()
worn_weight = df_all[(df_all['Typ'] == 'Am Körper')]['Total_Gewicht_g'].sum()
total_skin_out = base_weight + consumable_weight + worn_weight

c1, c2, c3, c4 = st.columns(4)
c1.metric("⚖️ Start-Gewicht", f"{total_skin_out/1000:.1f} kg")
c2.metric("🎒 Base Weight", f"{base_weight/1000:.1f} kg")
c3.metric("🥪 Verbrauch", f"{consumable_weight/1000:.1f} kg")
c4.metric("👕 Am Körper", f"{worn_weight/1000:.1f} kg")

# Chart
chart_data = df_all.groupby('Typ')['Total_Gewicht_g'].sum().reset_index()
base = alt.Chart(chart_data).encode(theta=alt.Theta("Total_Gewicht_g", stack=True))
pie = base.mark_arc(outerRadius=100).encode(
    color=alt.Color("Typ", scale=alt.Scale(domain=['Ausrüstung', 'Verbrauch', 'Am Körper'], range=['#3b8ed0', '#e04f5f', '#9e9e9e'])),
    tooltip=["Typ", "Total_Gewicht_g"]
)
st.altair_chart(pie, use_container_width=True)

# Listen
t1, t2 = st.tabs(["Details & Listen", "Debug/Datenbank"])
with t1:
    st.subheader("Deine Packliste")
    st.dataframe(df_all[['Menge', 'Name', 'Typ', 'Total_Gewicht_g']], use_container_width=True)
    
    if quellen_status == "Keine / Trocken":
        st.error("WARNUNG: Du hast angegeben, dass es KEINE Wasserquellen gibt. Dein 'Verbrauch'-Gewicht sinkt zwar, aber du musst ALLES Wasser von Anfang an tragen (falls deine Kapazität reicht). Wenn deine Kapazität (im Slider) kleiner ist als der Gesamtbedarf, wirst du durstig!")

with t2:
    st.dataframe(df)

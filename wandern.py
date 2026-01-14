import streamlit as st
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Outdoor Gear Wizard V8 (Excel)", page_icon="📊", layout="centered")
st.title("📊 Outdoor Gear Wizard V8")
st.caption("Datenbank: equipment.xlsx")

# --- 1. DATEN LADEN (Aus Excel) ---
@st.cache_data # Cache hält die Daten im Speicher, damit es schnell bleibt
def load_db():
    try:
        # Lese Excel, fülle leere Tags mit leerem String
        df = pd.read_excel("equipment.xlsx")
        df['Tags'] = df['Tags'].fillna("") 
        return df
    except FileNotFoundError:
        st.error("❌ 'equipment.xlsx' nicht gefunden! Bitte erstelle die Datei.")
        return pd.DataFrame()

df = load_db()

if df.empty:
    st.stop() # Stoppt die App, wenn keine Daten da sind

# Hilfsfunktion zum Suchen in Tags
def get_items_by_tag(tag):
    """Gibt eine Liste von Tupeln (Name, Gewicht) zurück, die den Tag enthalten."""
    subset = df[df['Tags'].str.contains(tag, case=False, na=False)]
    return list(zip(subset['Name'], subset['Gewicht_g']))

def get_pack_by_tag(tag):
    """Sucht Rucksäcke anhand Tag"""
    subset = df[(df['Kategorie'] == 'Rucksack') & (df['Tags'].str.contains(tag, case=False))]
    if not subset.empty:
        return subset.iloc[0].to_dict()
    return None

# --- 2. WIZARD UI ---

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
    if tage > 1:
        schlafen = st.selectbox("4. Übernachtung", ["Hütte", "Zelt"])
    else:
        schlafen = "Keine"
        st.info("Tagestour")

# Schritt 3: Extras
col_ex1, col_ex2, col_ex3 = st.columns(3)
with col_ex1:
    # Klettersteig Logik
    ks_disabled = (tour_art == "Hochtour") 
    ks_value = True if tour_art == "Hochtour" else False
    if not ks_disabled:
        ks_value = st.checkbox("Klettersteig?")
    else:
        st.markdown("✅ *Klettersteig (Inkl.)*")

with col_ex2:
    autark = st.checkbox("Selbstverpflegung?")

with col_ex3:
    wasser_liter = st.slider("Wasser (L)", 0.5, 4.0, 2.0, 0.5)


# --- 3. LOGIK-ENGINE (Excel-Basiert) ---
final_list = [] 

# A. Immer Basis
final_list.extend(get_items_by_tag("Basis"))

# B. Tour-Spezifisch
# Wir suchen nach Tags wie "Wandern", "Skitour", "Hochtour"
final_list.extend(get_items_by_tag(tour_art))

# C. Klettersteig (Wenn angehakt und NICHT Hochtour, um Dopplung zu meiden)
# (In Excel haben wir "Klettersteig" Items getaggt)
if ks_value and tour_art != "Hochtour":
    # Hole Items die NUR den Tag Klettersteig haben (oder wir filtern Duplikate später)
    ks_items = get_items_by_tag("Klettersteig")
    final_list.extend(ks_items)

# D. Temperatur
if temp_bereich == "Kalt (<0°C)":
    final_list.extend(get_items_by_tag("Kalt"))
elif temp_bereich == "Kühl (0-15°C)":
    # Hier könnten wir in Excel Items mit Tag "Kuehl" haben
    pass 

# E. Übernachtung & Dauer
if tage > 1:
    final_list.extend(get_items_by_tag("Tech")) # Powerbank etc
    
    if tage >= 3:
        final_list.extend(get_items_by_tag("Extra_Waesche"))

    if schlafen == "Hütte":
        final_list.extend(get_items_by_tag("Huette"))
    elif schlafen == "Zelt":
        if temp_bereich == "Warm (>15°C)":
            final_list.extend(get_items_by_tag("Zelt_Sommer"))
        else:
            final_list.extend(get_items_by_tag("Zelt_Winter"))

# F. Verpflegung (Manuell berechnet, da Variable Mengen)
final_list.append(('Wasser (Inhalt)', int(wasser_liter * 1000)))

# Behälter (Hole Gewicht aus Excel, berechne Anzahl)
container_item = get_items_by_tag("Container")[0] # Nimmt das erste Item mit Tag Container
kap = 0
while kap < wasser_liter:
    final_list.append(container_item) 
    kap += 1.0

if autark:
    final_list.extend(get_items_by_tag("Kochen"))
    
    # Gas Logik
    gas_tag = "Gas_Klein" if tage <= 6 else "Gas_Gross"
    final_list.extend(get_items_by_tag(gas_tag))
    
    # Essen
    final_list.append(('Essen (Gesamt)', tage * 700))

# G. Duplikate entfernen
# Wenn ein Item z.B. Tag "Wandern" UND "Basis" hat, ist es doppelt.
# Wir machen das über ein Dictionary (Name ist Key -> überschreibt Duplikate)
unique_dict = {name: gw for name, gw in final_list}
# Konvertiere zurück in Liste, sortiere alphabetisch (optional)
final_list_clean = list(unique_dict.items())


# H. Rucksack-Wahl (Logic bleibt im Code, Daten aus Excel)
pack_volumen_need = 0
if schlafen == "Zelt": pack_volumen_need += 25
if schlafen == "Hütte": pack_volumen_need += 10
if temp_bereich == "Kalt (<0°C)": pack_volumen_need += 10
if tour_art == "Skitour": pack_volumen_need += 10
pack_volumen_need += (tage * 2)

chosen_pack_row = None
if tour_art == "Skitour" or (tage == 1 and pack_volumen_need < 25):
    # Suche Rucksack mit Tag 'Rucksack_Ski' oder 'Rucksack_Day'
    chosen_pack_row = get_pack_by_tag("Rucksack_Ski")
elif tage > 1 and schlafen == "Zelt":
    chosen_pack_row = get_pack_by_tag("Rucksack_Trekking")
else:
    chosen_pack_row = get_pack_by_tag("Rucksack_Tour")

if chosen_pack_row:
    final_list_clean.append((chosen_pack_row['Name'], chosen_pack_row['Gewicht_g']))
else:
    st.warning("Kein passender Rucksack in Excel gefunden!")


# --- 4. ZUORDNUNG "AM KÖRPER" ---
st.divider()
st.subheader("🎒 Packliste")

# Lade Standard-Defaults aus Excel (Items die Tag 'Worn_Default' haben)
default_worn_items = get_items_by_tag("Worn_Default")
default_worn_names = [x[0] for x in default_worn_items]

# Filter: Nur was auch in der finalen Liste ist, wird vorausgewählt
all_item_names = [item[0] for item in final_list_clean]
preselect = [name for name in all_item_names if name in default_worn_names]

worn_selection = st.multiselect(
    "Was trägst du am Körper?",
    options=all_item_names,
    default=preselect
)

# --- 5. OUTPUT ---
rucksack_items = []
pack_weight = 0
total_weight = 0

for name, weight in final_list_clean:
    total_weight += weight
    if name not in worn_selection:
        rucksack_items.append({'Item': name, 'Gramm': weight})
        pack_weight += weight

c_res1, c_res2, c_res3 = st.columns(3)
c_res1.metric("🎒 Rucksack", f"{pack_weight/1000:.2f} kg")
c_res2.metric("👕 Am Körper", f"{(total_weight - pack_weight)/1000:.2f} kg")
if chosen_pack_row:
    c_res3.metric("📦 Rucksack", chosen_pack_row['Name'])

if rucksack_items:
    df_pack = pd.DataFrame(rucksack_items)
    st.data_editor(
        df_pack, 
        column_config={
            "Item": st.column_config.TextColumn("Equipment"),
            "Gramm": st.column_config.NumberColumn("Gewicht", format="%d g")
        },
        hide_index=True,
        use_container_width=True,
        num_rows="dynamic" # Erlaubt User Zeilen hinzuzufügen (nur temporär)
    )

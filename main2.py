from collections import defaultdict
import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# Načtení dat
df = pd.read_csv("reportv-16812456-cLnUE4byaeeI6INE.csv")

# Vyčištění dat
df = df.dropna(subset=["session_country_name", "tags"])


def extract_tags(x):
    if isinstance(x, list):
        return [str(tag).strip() for tag in x]
    if isinstance(x, str):
        try:
            val = ast.literal_eval(x)
            if isinstance(val, list):
                return [str(tag).strip() for tag in val]
            else:
                return [x.strip()]
        except:
            # Oddělíme tagy, pokud jsou např. "tag1, tag2"
            if ',' in x:
                return [tag.strip() for tag in x.split(',')]
            else:
                return [x.strip()]
    return []


# Kategorie podle prefixu
prefix_mapping = {
    'f': 'Function',
    'd': 'Documents',
    'tp': 'Technical parameters',
    's': 'Solution',
    'm': 'Mechanical paramaters',

}

# Rozdělení tagů do kategorií
categorized = defaultdict(list)
excluded_tags = {'lead', 'lead_h', 'None', 'ter', 'high', 'suspect_created', 'contact_updated', 'petr', 'contact_updated'}

df["tags"] = df["tags"].apply(extract_tags)

def split_tags(cell):
    if isinstance(cell, list):
        return cell
    if isinstance(cell, str):
        try:
            parsed = ast.literal_eval(cell)
            if isinstance(parsed, list):
                return parsed
        except:
            pass
        # Pokud to není seznam, tak rozdělíme podle čárky nebo mezer
        return [tag.strip() for tag in cell.replace(';', ',').split(',')]
    return []

# Kategorizace tagů podle prefixu
def categorize_tags(tagy):
    categorized_tags = defaultdict(list)
    for tag in tagy:
        if tag in excluded_tags:
            continue  # Přeskočí nežádoucí tagy
        if tag.endswith('_chat'):  # Odstraníme všechny tagy končící na _chat
            continue
        if '_' in tag:
            prefix = tag.split('_')[0]
        else:
            prefix = 'general'

        category = prefix_mapping.get(prefix, 'Request')
        categorized_tags[category].append(tag)
    return categorized_tags



# Mapování tagů na kategorie pro každý řádek v datech
df['categorized_tags'] = df['tags'].apply(categorize_tags)

# Mapa: počet záznamů podle zemí
country_counts = df["session_country_name"].value_counts().reset_index()
country_counts.columns = ["session_country_name", "count"]

st.title("🌍 The map of the chat users.")
st.markdown("Click on the map to see the numbers. Select the country to see the most common topics.")

# Mapa světa


fig = go.Figure(data=go.Scattergeo(
    locations=country_counts["session_country_name"],
    locationmode="country names",
    text=country_counts["count"],
    marker=dict(
        size=10,
        color=country_counts["count"],
        colorscale="Blues",
        colorbar_title="Count"
    )
))

fig.update_geos(projection_type="natural earth")

fig.update_layout(
    title="Chats according to the region.",
    height=300,
    margin={"r": 0, "t": 30, "l": 0, "b": 0}
)

st.plotly_chart(fig, use_container_width=True)
## Výběr země
countries = sorted(df["session_country_name"].unique())
countries.insert(0, "All")  # Přidáme možnost "All" na začátek

selected_country = st.selectbox("Select the country:", countries)

# Zobrazení témat podle země (nebo všech zemí)
if selected_country == "All":
    tags_list = df["categorized_tags"]
    st.subheader("📊 The chat topics for **all countries combined**")
else:
    tags_list = df[df["session_country_name"] == selected_country]["categorized_tags"]
    st.subheader(f"📊 The chat topics for {selected_country}")

# Sčítáme výskyty tagů v jednotlivých kategoriích
tag_counter = defaultdict(list)
for categories in tags_list:
    for category, tags in categories.items():
        tag_counter[category].extend(tags)

available_categories = sorted(tag_counter.keys())
selected_category = st.selectbox("Select the category:", available_categories)

if selected_category:
    # Počet výskytů jednotlivých tagů v dané kategorii
    tag_freq = pd.Series(tag_counter[selected_category]).value_counts().head(15)

    st.subheader(f"🔍 The topics in the selected category **{selected_category}** for {selected_country}")
    st.bar_chart(tag_freq)


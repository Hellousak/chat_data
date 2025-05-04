from collections import defaultdict
import streamlit as st
import pandas as pd
import plotly.express as px
import ast

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

st.title("🌍 Mapa zemí a tagů")
st.markdown("Zobraz mapu podle zemí. Po výběru země uvidíš nejčastější tagy dle kategorií.")

# Mapa světa
fig = px.choropleth(
    country_counts,
    locations="session_country_name",
    locationmode="country names",
    color="count",
    color_continuous_scale="Blues",
    title="Výskyt podle zemí"
)
st.plotly_chart(fig, use_container_width=True)

# Výběr země
selected_country = st.selectbox("Vyber zemi:", sorted(df["session_country_name"].unique()))

if selected_country:
    st.subheader(f"📊 Výběr kategorie tagů pro {selected_country}")
    tags_list = df[df["session_country_name"] == selected_country]["categorized_tags"]

    # Sčítáme výskyty tagů v jednotlivých kategoriích
    tag_counter = defaultdict(list)
    for categories in tags_list:
        for category, tags in categories.items():
            tag_counter[category].extend(tags)

    available_categories = sorted(tag_counter.keys())
    selected_category = st.selectbox("Vyber kategorii tagů:", available_categories)

    if selected_category:
        # Počet výskytů jednotlivých tagů v dané kategorii
        tag_freq = pd.Series(tag_counter[selected_category]).value_counts().head(15)

        st.subheader(f"🔍 Nejčastější tagy v kategorii **{selected_category}** pro {selected_country}")
        st.bar_chart(tag_freq)


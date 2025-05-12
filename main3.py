from collections import defaultdict
import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import altair as alt

st.set_page_config(layout="wide")

# Načtení dat
df = pd.read_csv("reportv-16812456-AUCiFlJlv6y7to1P.csv")

# Převeď textový čas na datetime objekt (opravený formát)
df['session_start_date'] = pd.to_datetime(df['session_start_date (GMT+0)'], format="%Y-%m-%d %H:%M:%S")

# Min/max datum pro omezení výběru
min_date = df['session_start_date'].min().date()  # získej minimální datum
max_date = df['session_start_date'].max().date()  # získej maximální datum

# 🎯 Date picker ve Streamlit sidebaru
st.sidebar.markdown("## Select the date")
start_date = st.sidebar.date_input("Od:", min_value=min_date, max_value=max_date, value=min_date)
end_date = st.sidebar.date_input("Do:", min_value=min_date, max_value=max_date, value=max_date)

# Filtrování dat podle zvoleného období
filtered_df = df[(df['session_start_date'].dt.date >= start_date) & (df['session_start_date'].dt.date <= end_date)]

# Ukázka – výpis počtu řádků
st.write(f"**{filtered_df.shape[0]}** chats from {start_date} to {end_date}")



# Vyčištění dat
filtered_df = filtered_df.dropna(subset=["session_country_name", "tags"])

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
            if ',' in x:
                return [tag.strip() for tag in x.split(',')]
            else:
                return [x.strip()]
    return []

prefix_mapping = {
    'f': 'Function',
    'd': 'Documents',
    'tp': 'Technical parameters',
    's': 'Solution',
    'm': 'Mechanical paramaters',
}

excluded_tags = {'lead', 'lead_h', 'None', 'ter', 'high', 'suspect_created', 'contact_updated', 'petr'}

filtered_df["tags"] = filtered_df["tags"].apply(extract_tags)

def categorize_tags(tagy):
    categorized_tags = defaultdict(list)
    for tag in tagy:
        if tag in excluded_tags:
            continue
        if tag.endswith('_chat'):
            continue
        if '_' in tag:
            prefix = tag.split('_')[0]
        else:
            prefix = 'general'
        category = prefix_mapping.get(prefix, 'Request')
        categorized_tags[category].append(tag)
    return categorized_tags

filtered_df['categorized_tags'] = filtered_df['tags'].apply(categorize_tags)

# Mapa
country_counts = filtered_df["session_country_name"].value_counts().reset_index()
country_counts.columns = ["session_country_name", "count"]

st.title("The map of the chat users.")
st.markdown("Click on the map to see the numbers. Select the country to see the most common topics.")

fig = px.choropleth(
    country_counts,
    locations="session_country_name",
    locationmode="country names",
    color="count",
    color_continuous_scale="Blues",
    title="Chats according to the region."
)
st.plotly_chart(fig, use_container_width=True)

# Výběr země
countries = sorted(df["session_country_name"].unique())
countries.insert(0, "All")

selected_country = st.selectbox("Select the country:", countries)

if selected_country == "All":
    tags_list = df["categorized_tags"]
    st.subheader("The chat topics for **all countries combined**")
else:
    tags_list = filtered_df[filtered_df["session_country_name"] == selected_country]["categorized_tags"]
    st.subheader(f"The chat topics for {selected_country}")

# Počítání tagů
tag_counter = defaultdict(list)
for categories in tags_list:
    for category, tags in categories.items():
        tag_counter[category].extend(tags)

available_categories = sorted(tag_counter.keys())
available_categories.insert(0, "All")

selected_category = st.selectbox("Select the category:", available_categories)

if selected_category:
    if selected_category == "All":
        all_tags = []
        for tags in tag_counter.values():
            all_tags.extend(tags)
        tag_freq = pd.Series(all_tags).value_counts().head(50)
        st.subheader(f"The top topics **across all categories** for {selected_country}")
    else:
        tag_freq = pd.Series(tag_counter[selected_category]).value_counts().head(50)
        st.subheader(f"The topics in the selected category **{selected_category}** for {selected_country}")

    tag_df = tag_freq.reset_index()
    tag_df.columns = ["tag", "count"]
    tag_df["index"] = tag_df.index  # přidáme index pro barvy

    # Barvy pro cyklické střídání
    colors = ["#211C84", "#4D55CC", "#7A73D1", "#B5A8D5"]
    tag_df["color"] = tag_df["index"].map(lambda i: colors[i % len(colors)])

    # Vykreslení grafu
    chart = (
        alt.Chart(tag_df)
        .mark_bar()
        .encode(
            x=alt.X("count", type="quantitative", title="Number of chats", axis=alt.Axis(format="d")),
            y=alt.Y("tag:N", title="Topic", sort="-x"),
            color=alt.Color("color:N", scale=None, legend=None)
        )
    )

    st.altair_chart(chart, use_container_width=True)




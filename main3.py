import streamlit as st
import pandas as pd
import plotly.express as px
import ast

st.set_page_config(layout="wide")

# Načtení dat
df = pd.read_csv("reportv-16812456-cLnUE4byaeeI6INE.csv")

# Vyčištění dat
df = df.dropna(subset=["session_country_name", "tags"])



# Bezpečné zpracování sloupce "tags"
def parse_tags(x):
    if isinstance(x, list):
        return x
    if isinstance(x, str):
        try:
            # Zkusíme parsovat seznam
            val = ast.literal_eval(x)
            if isinstance(val, list):
                return val
            else:
                return [str(val)]
        except:
            # Pokud selže parsování, vrátíme jako seznam s jedním prvkem
            return [x.strip()]
    return []

df["tags"] = df["tags"].apply(parse_tags)

# Mapa: počet záznamů podle zemí
country_counts = df["session_country_name"].value_counts().reset_index()
country_counts.columns = ["session_country_name", "count"]

st.title("🌍 Mapa zemí a tagů")
st.markdown("Zobraz mapu podle zemí. Po výběru země uvidíš nejčastější tagy.")

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

# Zobrazení top tagů pro vybranou zemi
if selected_country:
    st.subheader(f"📊 Top tagy pro {selected_country}")
    tags_list = df[df["session_country_name"] == selected_country]["tags"].explode()
    top_tags = tags_list.value_counts().head(10)
    st.bar_chart(top_tags)



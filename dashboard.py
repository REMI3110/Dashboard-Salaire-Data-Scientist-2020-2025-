import pandas as pd
import plotly.express as px
import pycountry
import streamlit as st

# -----------------------------
# Configuration de la page
# -----------------------------
st.set_page_config(page_title="Dashboard Salaires Data Science", layout="wide")

# -----------------------------
# Chargement du dataset
# -----------------------------
df = pd.read_csv("DataScience_salaries_2025.csv")

# Mapping des colonnes
df['experience_level'] = df['experience_level'].map({'EN':'Junior','MI':'Mid','SE':'Senior','EX':'Executive'})
df['company_size'] = df['company_size'].map({'S':'Small','M':'Medium','L':'Large'})
df['employment_type'] = df['employment_type'].map({'FT':'Full-time','PT':'Part-time','CT':'Contract','FL':'Freelance'})
df['remote_ratio'] = df['remote_ratio'].astype(int)

# Conversion ISO2 -> ISO3 pour la carte
def iso2_to_iso3(alpha2):
    try:
        return pycountry.countries.get(alpha_2=alpha2).alpha_3
    except:
        return None
df['country_iso3'] = df['employee_residence'].apply(iso2_to_iso3)

# -----------------------------
# Texte introductif
# -----------------------------
st.title("Dashboard Salaires Data Science 2020–2025")
st.markdown("""
Ce dashboard présente une analyse des salaires des professionnels en Data Science à travers le monde.
Vous pouvez explorer les données selon le niveau d'expérience, la taille de l'entreprise, le pourcentage de télétravail, le pays et l'année.
Utilisez les filtres sur la gauche pour affiner votre exploration.
""")

# -----------------------------
# Sidebar pour filtres
# -----------------------------
st.sidebar.header("Filtres")
exp_filter = st.sidebar.multiselect("Niveau d'expérience", df['experience_level'].unique(), default=df['experience_level'].unique())
size_filter = st.sidebar.multiselect("Taille entreprise", df['company_size'].unique(), default=df['company_size'].unique())
remote_filter = st.sidebar.slider("% Télétravail", 0, 100, (0,100))
country_filter = st.sidebar.multiselect("Pays", df['employee_residence'].unique(), default=df['employee_residence'].unique())
year_filter = st.sidebar.multiselect("Année", sorted(df['work_year'].unique()), default=sorted(df['work_year'].unique()))

# -----------------------------
# Appliquer filtres
# -----------------------------
df_filtered = df[
    (df['experience_level'].isin(exp_filter)) &
    (df['company_size'].isin(size_filter)) &
    (df['remote_ratio'] >= remote_filter[0]) &
    (df['remote_ratio'] <= remote_filter[1]) &
    (df['employee_residence'].isin(country_filter)) &
    (df['work_year'].isin(year_filter))
].copy()

# -----------------------------
# Résumé des salaires filtrés
# -----------------------------
st.subheader("Résumé des salaires filtrés")
st.markdown(f"- **Salaire moyen** : ${df_filtered['salary_in_usd'].mean():,.0f}")
st.markdown(f"- **Salaire minimum** : ${df_filtered['salary_in_usd'].min():,.0f}")
st.markdown(f"- **Salaire maximum** : ${df_filtered['salary_in_usd'].max():,.0f}")

# -----------------------------
# Visualisations
# -----------------------------

# ✅ Évolution des salaires dans le temps
st.subheader("Évolution des salaires moyens (2020–2025)")
st.markdown("Ce graphique montre l'évolution des salaires moyens au fil des années.")
mean_salary_year = df_filtered.groupby('work_year')['salary_in_usd'].mean().reset_index()
fig_year = px.line(mean_salary_year, x="work_year", y="salary_in_usd", markers=True,
                   title="Évolution des salaires moyens par année")
st.plotly_chart(fig_year, use_container_width=True)

# Distribution des salaires
st.subheader("Distribution générale des salaires")
fig_hist = px.histogram(df_filtered, x='salary_in_usd', nbins=50, title="Distribution des salaires en USD")
st.plotly_chart(fig_hist, use_container_width=True)

# Boxplot par expérience
st.subheader("Salaires par niveau d'expérience")
fig_exp = px.box(df_filtered, x='experience_level', y='salary_in_usd', 
                 color='experience_level',
                 color_discrete_map={'Junior':'#636EFA','Mid':'#EF553B','Senior':'#00CC96','Executive':'#AB63FA'})
st.plotly_chart(fig_exp, use_container_width=True)

# Moyenne par taille entreprise
st.subheader("Salaire moyen par taille d'entreprise")
mean_salary_company = df_filtered.groupby('company_size')['salary_in_usd'].mean().reset_index()
fig_size = px.bar(mean_salary_company, x='company_size', y='salary_in_usd', color='company_size',
                  color_discrete_map={'Small':'#636EFA','Medium':'#EF553B','Large':'#00CC96'})
st.plotly_chart(fig_size, use_container_width=True)

# Boxplot par % télétravail
st.subheader("Salaires par % télétravail")
df_filtered['remote_group'] = pd.cut(df_filtered['remote_ratio'], bins=[0,25,50,75,100], labels=['0-25','26-50','51-75','76-100'])
fig_remote = px.box(df_filtered, x='remote_group', y='salary_in_usd', color='remote_group',
                    color_discrete_map={'0-25':'#636EFA','26-50':'#EF553B','51-75':'#00CC96','76-100':'#AB63FA'})
st.plotly_chart(fig_remote, use_container_width=True)

# Boxplot par type de contrat
st.subheader("Salaires par type de contrat")
fig_type = px.box(df_filtered, x='employment_type', y='salary_in_usd', color='employment_type',
                  color_discrete_map={'Full-time':'#636EFA','Part-time':'#EF553B','Contract':'#00CC96','Freelance':'#AB63FA'})
st.plotly_chart(fig_type, use_container_width=True)

# Carte interactive par pays
st.subheader("Salaire moyen par pays")
mean_salary_country = df_filtered.groupby('country_iso3')['salary_in_usd'].mean().reset_index()
fig_map = px.choropleth(mean_salary_country,
                        locations="country_iso3",
                        color="salary_in_usd",
                        hover_name="country_iso3",
                        color_continuous_scale=px.colors.sequential.Plasma,
                        title="Salaire moyen par pays",
                        projection="natural earth")
st.plotly_chart(fig_map, use_container_width=True)

# Afficher les données filtrées
st.subheader("Données filtrées")
st.dataframe(df_filtered)

# Bouton pour télécharger le CSV filtré
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="Télécharger CSV filtré",
    data=csv,
    file_name="salaire_filtré.csv",
    mime="text/csv"
)

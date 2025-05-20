import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Load the data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp949')
    return df

df_gender_population = load_data('202504_202504_연령별인구현황_월간_남녀구분.csv')

# Preprocess the data for population pyramid
def preprocess_population_data(df):
    # Extract age columns for male and female
    male_cols = [col for col in df.columns if '남_' in col and '세' in col and '총인구수' not in col and '연령구간인구수' not in col]
    female_cols = [col for col in df.columns if '여_' in col and '세' in col and '총인구수' not in col and '연령구간인구수' not in col]

    # Extract age labels
    ages = [col.split('_')[-1].replace('세', '') for col in male_cols]

    # Create a new DataFrame for plotting
    plot_df = pd.DataFrame({'Age': ages})

    # For each administrative region, extract male and female populations
    regions_data = {}
    for index, row in df.iterrows():
        region_name = row['행정구역']
        male_population = [int(str(row[col]).replace(',', '')) for col in male_cols]
        female_population = [int(str(row[col]).replace(',', '')) for col in female_cols]
        regions_data[region_name] = {
            'Male': male_population,
            'Female': female_population
        }
    return plot_df, regions_data

plot_df, regions_data = preprocess_population_data(df_gender_population)

# Streamlit application
st.title('Age and Gender Population Distribution')

# Region selection
selected_region = st.selectbox('Select Administrative Region', list(regions_data.keys()))

if selected_region:
    data = regions_data[selected_region]
    male_pop = data['Male']
    female_pop = data['Female']

    # Create population pyramid
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=plot_df['Age'],
        x=[-p for p in male_pop],  # Negative for male population
        name='Male',
        orientation='h',
        marker=dict(color='skyblue')
    ))

    fig.add_trace(go.Bar(
        y=plot_df['Age'],
        x=female_pop,
        name='Female',
        orientation='h',
        marker=dict(color='lightcoral')
    ))

    # Determine dynamic x-axis range
    max_abs_pop = max(max(male_pop), max(female_pop))
    x_range_max = max_abs_pop * 1.2 # Add some padding

    fig.update_layout(
        title=f'Population Pyramid for {selected_region}',
        barmode='relative',
        bargap=0.2,
        height=700,
        xaxis_title='Population',
        yaxis_title='Age Group',
        xaxis=dict(tickvals=[-round(x_range_max/2), 0, round(x_range_max/2)], # Adjust tick values
                   ticktext=[f'{round(x_range_max/2):,}', '0', f'{round(x_range_max/2):,}'], # Formatted tick text
                   range=[-x_range_max, x_range_max]) # Adjust x-axis range dynamically
    )

    st.plotly_chart(fig, use_container_width=True)

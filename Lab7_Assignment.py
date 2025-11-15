import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page configuration with custom theme
st.set_page_config(
    page_title="Data Science Student Marks Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (works in both light and dark mode)
st.markdown("""
    <style>
    /* Metric styling that works in both themes */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        font-weight: 500;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.85rem;
    }
    
    /* Ensure metrics are visible in dark mode */
    [data-testid="metric-container"] {
        background-color: var(--background-color);
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    
    /* Light mode specific */
    @media (prefers-color-scheme: light) {
        .main {
            background-color: #f5f7fa;
        }
        h1 {
            color: #1f4788;
            font-weight: 700;
        }
        h2 {
            color: #2c5aa0;
            font-weight: 600;
        }
        h3 {
            color: #3d6ab3;
        }
    }
    
    /* Dark mode specific */
    @media (prefers-color-scheme: dark) {
        [data-testid="metric-container"] {
            background-color: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv('data_science_student_marks.csv')
    # Calculate average marks and total marks
    df['average_marks'] = df[['sql_marks', 'excel_marks', 'python_marks', 'power_bi_marks', 'english_marks']].mean(axis=1).round(2)
    df['total_marks'] = df[['sql_marks', 'excel_marks', 'python_marks', 'power_bi_marks', 'english_marks']].sum(axis=1)
    return df

df = load_data()

# Title and description
st.title("📊 Data Science Student Marks Dashboard")
st.markdown("### Explore and analyze student performance across different subjects and locations")
st.markdown("---")

# Sidebar filters
st.sidebar.header("🔍 Filters")
st.sidebar.markdown("Use the filters below to customize your view")

# Filter 1: Location filter
all_locations = ['All'] + sorted(df['location'].unique().tolist())
selected_location = st.sidebar.selectbox(
    "Select Location:",
    options=all_locations,
    index=0
)

# Filter 2: Age range slider
min_age = int(df['age'].min())
max_age = int(df['age'].max())
age_range = st.sidebar.slider(
    "Select Age Range:",
    min_value=min_age,
    max_value=max_age,
    value=(min_age, max_age)
)

# Filter 3: Subject selection
subjects = ['sql_marks', 'excel_marks', 'python_marks', 'power_bi_marks', 'english_marks']
subject_names = ['SQL', 'Excel', 'Python', 'Power BI', 'English']
selected_subjects = st.sidebar.multiselect(
    "Select Subjects to Display:",
    options=subject_names,
    default=subject_names
)

# Filter 4: Minimum average marks filter
min_avg = st.sidebar.slider(
    "Minimum Average Marks:",
    min_value=0,
    max_value=100,
    value=0
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** Use the filters to drill down into specific student segments!")

# Apply filters
filtered_df = df.copy()

if selected_location != 'All':
    filtered_df = filtered_df[filtered_df['location'] == selected_location]

filtered_df = filtered_df[(filtered_df['age'] >= age_range[0]) & (filtered_df['age'] <= age_range[1])]
filtered_df = filtered_df[filtered_df['average_marks'] >= min_avg]

# Main dashboard
if len(filtered_df) == 0:
    st.warning("⚠️ No data matches the selected filters. Please adjust your filter criteria.")
else:
    # Key Metrics Section
    st.header("📈 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Total Students",
            value=len(filtered_df),
            delta=f"{len(filtered_df) - len(df)} from total"
        )
    
    with col2:
        st.metric(
            label="Average Age",
            value=f"{filtered_df['age'].mean():.1f}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Avg Overall Score",
            value=f"{filtered_df['average_marks'].mean():.2f}",
            delta=None
        )
    
    with col4:
        st.metric(
            label="Top Score",
            value=f"{filtered_df['average_marks'].max():.2f}",
            delta=None
        )
    
    with col5:
        st.metric(
            label="Locations",
            value=filtered_df['location'].nunique(),
            delta=None
        )
    
    st.markdown("---")
    
    # Visualization Section
    st.header("📊 Visualizations")
    
    # Create two columns for visualizations
    viz_col1, viz_col2 = st.columns(2)
    
    # Visualization 1: Average Marks by Location (Bar Chart)
    with viz_col1:
        st.subheader("Average Marks by Location")
        location_avg = filtered_df.groupby('location')['average_marks'].mean().sort_values(ascending=False).reset_index()
        
        fig1 = px.bar(
            location_avg,
            x='location',
            y='average_marks',
            color='average_marks',
            color_continuous_scale='Blues',
            labels={'average_marks': 'Average Marks', 'location': 'Location'},
            title='Performance Comparison Across Cities'
        )
        fig1.update_layout(
            showlegend=False,
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    # Visualization 2: Subject Performance Distribution (Box Plot)
    with viz_col2:
        st.subheader("Subject Marks Distribution")
        
        # Prepare data for box plot
        subject_data = []
        subject_mapping = {
            'sql_marks': 'SQL',
            'excel_marks': 'Excel',
            'python_marks': 'Python',
            'power_bi_marks': 'Power BI',
            'english_marks': 'English'
        }
        
        for subject_col, subject_name in subject_mapping.items():
            if subject_name in selected_subjects:
                subject_data.extend([
                    {'Subject': subject_name, 'Marks': mark} 
                    for mark in filtered_df[subject_col]
                ])
        
        if subject_data:
            subject_df = pd.DataFrame(subject_data)
            fig2 = px.box(
                subject_df,
                x='Subject',
                y='Marks',
                color='Subject',
                title='Marks Distribution by Subject',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig2.update_layout(
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig2, use_container_width=True)
    
    # Visualization 3: Scatter Plot - Age vs Average Marks
    st.subheader("Age vs Average Marks Analysis")
    fig3 = px.scatter(
        filtered_df,
        x='age',
        y='average_marks',
        color='location',
        size='total_marks',
        hover_data=['student_id'],
        title='Student Performance by Age and Location',
        labels={'age': 'Age', 'average_marks': 'Average Marks'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig3.update_layout(height=450)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Visualization 4: Heatmap of Subject Performance
    st.subheader("Subject Performance Heatmap")
    
    # Calculate average marks for each subject by location
    subject_cols = ['sql_marks', 'excel_marks', 'python_marks', 'power_bi_marks', 'english_marks']
    heatmap_data = filtered_df.groupby('location')[subject_cols].mean().round(2)
    
    fig4 = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=['SQL', 'Excel', 'Python', 'Power BI', 'English'],
        y=heatmap_data.index,
        colorscale='RdYlGn',
        text=heatmap_data.values,
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        colorbar=dict(title="Avg Marks")
    ))
    
    fig4.update_layout(
        title='Average Subject Marks by Location',
        xaxis_title='Subject',
        yaxis_title='Location',
        height=400
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    st.markdown("---")
    
    # Data Summary Section
    st.header("📋 Data Summary")
    
    tab1, tab2, tab3 = st.tabs(["📊 Statistics", "🎓 Top Performers", "📁 Raw Data"])
    
    with tab1:
        st.subheader("Statistical Summary")
        
        # Subject statistics
        stats_df = filtered_df[subject_cols].describe().round(2)
        stats_df.columns = ['SQL', 'Excel', 'Python', 'Power BI', 'English']
        st.dataframe(stats_df, use_container_width=True)
        
        # Additional insights
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**📍 Location Distribution**")
            location_counts = filtered_df['location'].value_counts().reset_index()
            location_counts.columns = ['Location', 'Count']
            st.dataframe(location_counts, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("**🎂 Age Distribution**")
            age_counts = filtered_df['age'].value_counts().sort_index().reset_index()
            age_counts.columns = ['Age', 'Count']
            st.dataframe(age_counts, use_container_width=True, hide_index=True)
    
    with tab2:
        st.subheader("Top 10 Performers")
        top_students = filtered_df.nlargest(10, 'average_marks')[
            ['student_id', 'location', 'age', 'average_marks', 'total_marks']
        ].reset_index(drop=True)
        top_students.index = top_students.index + 1
        st.dataframe(top_students, use_container_width=True)
        
        st.markdown("**🏆 Best Subject Performance**")
        best_subjects = pd.DataFrame({
            'Subject': ['SQL', 'Excel', 'Python', 'Power BI', 'English'],
            'Highest Score': [
                filtered_df['sql_marks'].max(),
                filtered_df['excel_marks'].max(),
                filtered_df['python_marks'].max(),
                filtered_df['power_bi_marks'].max(),
                filtered_df['english_marks'].max()
            ],
            'Average Score': [
                filtered_df['sql_marks'].mean().round(2),
                filtered_df['excel_marks'].mean().round(2),
                filtered_df['python_marks'].mean().round(2),
                filtered_df['power_bi_marks'].mean().round(2),
                filtered_df['english_marks'].mean().round(2)
            ]
        })
        st.table(best_subjects)
    
    with tab3:
        st.subheader("Filtered Dataset")
        st.markdown(f"Showing **{len(filtered_df)}** records")
        
        # Display options
        show_all = st.checkbox("Show all columns", value=True)
        
        if show_all:
            st.dataframe(filtered_df, use_container_width=True)
        else:
            display_cols = st.multiselect(
                "Select columns to display:",
                options=filtered_df.columns.tolist(),
                default=['student_id', 'location', 'age', 'average_marks']
            )
            if display_cols:
                st.dataframe(filtered_df[display_cols], use_container_width=True)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=csv,
            file_name='filtered_student_marks.csv',
            mime='text/csv',
        )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>Data Science Student Marks Dashboard | Created with Streamlit 📊</p>
        <p style='font-size: 12px;'>Built for interactive data exploration and analysis</p>
    </div>
    """,
    unsafe_allow_html=True
)
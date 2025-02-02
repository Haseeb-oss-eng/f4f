import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO
import joblib

# Function to convert Google Drive link to a direct download URL
def convert_google_drive_link(url):
    try:
        file_id = url.split('/d/')[1].split('/')[0]
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    except IndexError:
        st.error("Invalid Google Drive URL.")
        return None

# Input for Google Drive URL
menu = st.sidebar.radio("Menu",["Dashboard","TreeDBH_cm Prediction"])

if menu=="Dashboard":
    urls = st.text_input("Enter Google Drive URL:")  
    csv_url = convert_google_drive_link(urls)
        
    if csv_url:
            response = requests.get(csv_url)
            # Ensure the response was successful (status code 200)
            if response.status_code == 200:
                @st.cache_data  
                def load_data():
                    data = StringIO(response.text)
                    ds = pd.read_csv(data)  # Load CSV data into a pandas DataFrame
                    return ds

                # Load the data
                df = load_data()
                df.columns = df.columns.str.strip()

                page = st.sidebar.radio('Select a Page', ['Summary Info', 'Farmers Information'])

                if page=="Summary Info":
                    # Streamlit App
                    st.title("Farmer Plantation Dashboard")

                    # Display the dataset
                    st.subheader("Dataset Overview")
                    st.write(df)

                    # Filters
                    st.sidebar.header("Filters")
                    district = st.sidebar.selectbox('District',df["District"].unique())
                    block = st.sidebar.selectbox('Block',df['Block'].unique())
                    plantation_type_filter = st.sidebar.selectbox("Select Plantation Type", df["plantation_type_dense_fruit"].unique())



                    # Apply filters
                    filtered_df = df[
                        (df["District"] == district)&
                        (df["Block"]==block)&
                        (df["plantation_type_dense_fruit"] == plantation_type_filter)
                    ]

                    # Display filtered data
                    st.subheader("Filtered Data")
                    st.write(filtered_df)

                    # Key Metrics
                    st.subheader("Key Metrics")
                    total_trees_planted = filtered_df["trees_planted"].sum()
                    total_payment_collected = filtered_df["amount"].sum()

                    st.metric("Total Trees Planted", total_trees_planted)
                    st.metric("Total Payment Collected", total_payment_collected)

                    # Visualizations
                    st.subheader("Visualizations")

                    # Bar chart: Trees Planted by Farmer
                    fig1 = px.bar(filtered_df, x="farmer_name", y="trees_planted", title="Trees Planted by Farmer")
                    st.plotly_chart(fig1)

                    # Pie chart: Payment Mode Distribution
                    fig2 = px.pie(filtered_df, names="mode_collection_cash_upi_banktransfer", title="Payment Mode Distribution")
                    st.plotly_chart(fig2)

                    # Bar chart: Tree Species Distribution
                    tree_species_columns = [
                        "mango_native", "mango_grafted_kesar", "lemon_sai_sharbati", "sitaphal_golden",
                        "awala", "peru", "chincha", "Jamun", "drumstick_Koimb", "bamboo", "karwand",
                        "arjun", "katesawar", "karanj", "kaduneem", "kanchan", "kadamb", "bhendi",
                        "shirish", "ain", "pimpal", "vad", "tamhan", "waval", "palas", "babhul", "bakul"
                    ]
                    tree_species_counts = filtered_df[tree_species_columns].sum()
                    fig3 = px.bar(tree_species_counts, title="Tree Species Distribution")
                    st.plotly_chart(fig3)

                    #acre and farmers land
                    land = px.scatter(filtered_df,x='total_land_area_acre',y='area_f4f_acre')
                    st.plotly_chart(land)

                elif page=='Farmers Information':
                    ###Data Available
                    st.header("Information")
                    info = ['farmer_name','District','Block',
                            'total_land_area_acre','area_f4f_acre','trees_planted','farmer_payment_date','contract_date'
                            ,'amount','mode_collection_cash_upi_banktransfer']
                    datas = ['water_available',	'electricity_available','kml_uploaded',	'contract uploaded',	
                            'land_record_uploaded',	'cc_training_uploaded?','soil_sample_collected?',
                            'drone_ortho_taken','farmer_payment_collected','baseline_survey']
                    tree_species_columns = [
                        "mango_native", "mango_grafted_kesar", "lemon_sai_sharbati", "sitaphal_golden",
                        "awala", "peru", "chincha", "Jamun", "drumstick_Koimb", "bamboo", "karwand",
                        "arjun", "katesawar", "karanj", "kaduneem", "kanchan", "kadamb", "bhendi",
                        "shirish", "ain", "pimpal", "vad", "tamhan", "waval", "palas", "babhul", "bakul"
                    ]
                    farmer = st.sidebar.selectbox('Farmer',df["farmer_name"])

                    farmer_df = df[df['farmer_name'] == farmer]

                    details = farmer_df[info]
                    st.write(details)


                    # Data Available
                    availabe_data = farmer_df[datas]
                    fig4 = px.bar(availabe_data, title="Data Available")
                    st.plotly_chart(fig4)


                    #farmer species 
                    species_farmer = farmer_df[tree_species_columns].sum()
                    fig5 = px.bar(species_farmer,title="Species")
                    st.plotly_chart(fig5)

                    #plants for each farmer
                    fig6 = px.bar(farmer_df,x='total_land_area_acre',y='area_f4f_acre')
                    st.plotly_chart(fig6)
                
                
            else:
                st.error("Failed to download the CSV file.")
    else:
        st.error("Enter the URL")
elif menu=='TreeDBH_cm Prediction':
            st.header("Prediction of TreeDBH_cm")
            Tree_species = st.text_input("Enter Tree Species:")
            TreeHeight_foot = st.number_input("Enter the Tree Height in foot:")
            TreeCrown_foot = st.number_input("Enter the Tree Crown in foot:")
            model = joblib.load('model_svr.pkl')
            def predict(input_data):
                prediction = model.predict(input_data)
                return prediction[0]
            new_data = pd.DataFrame({
                        'Tree species': [Tree_species],
                        'TreeHeight_foot': [TreeHeight_foot],
                        'TreeCrown_foot': [TreeCrown_foot]
                    })
            if st.button('Predict'):
                 predictions = predict(new_data)
                 st.success(f"Predicted TreeDBH_cm :{predictions:.3f}")

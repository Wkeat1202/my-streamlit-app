import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_species_info(species_name):
    url = "https://api.gbif.org/v1/species/match"
    params = {"name": species_name}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# species data
def get_occurrences(species_name, limit=50):
    url = "https://api.gbif.org/v1/occurrence/search"
    params = {"scientificName": species_name, "limit": limit}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data["results"]
    else:
        return None

# climate data
def get_climate_data(lat, lon, api_key="6b883220414471c6b8dfafd97423818b"):  
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,  
        "units": "metric" 
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching climate data: {e}")
        return None

# default is "Occurrence Data"
option = st.sidebar.radio("Select Data Type to Display", ("Occurrence Data", "Climate Data", "Global Average Temperature for the Past 40 Years"), index=0)

# Change the title based on the option selected
if option == "Occurrence Data":
    st.title("🌿 Biodiversity Data Explorer - Species Comparison")
elif option == "Climate Data":
    st.title("🌿 Biodiversity Data Explorer - Species Preferred Temperature for Survival")
else:
    st.title("🌍 Global Average Temperature for the Past 40 Years")

if option == "Global Average Temperature for the Past 40 Years":
    st.subheader("📊 Average Temperature per Year")
    
    df = pd.read_csv('weather.csv')

    df.dropna(inplace=True)
    avg_temperature = df.groupby('Year')['Mean Temperature (°C)'].mean()

    # graph
    plt.figure(figsize=(10, 6))
    plt.plot(avg_temperature.index, avg_temperature.values, marker='o', linestyle='-', color='b')

    plt.title('Average Temperature Per Year')
    plt.xlabel('Year')
    plt.ylabel('Average Temperature (°C)')
    plt.grid(True)
    plt.xticks(rotation=45)

    plt.tight_layout()

    # plotting
    st.pyplot(plt)

elif option == "Occurrence Data":
    species_name_1 = st.text_input("Enter first species name:", "Panthera tigris")
    species_name_2 = st.text_input("Enter second species name:", "Loxodonta africana")

    if st.button("Compare"):
        species_info_1 = get_species_info(species_name_1)
        species_info_2 = get_species_info(species_name_2)
        
        if species_info_1 and species_info_2:
            # information for species two
            st.subheader(f"🔎 Species Information: {species_name_1}")
            st.markdown(f"**Scientific Name:** {species_info_1.get('scientificName', 'N/A')}")
            st.markdown(f"**Kingdom:** {species_info_1.get('kingdom', 'N/A')}")
            st.markdown(f"**Phylum:** {species_info_1.get('phylum', 'N/A')}")
            st.markdown(f"**Class:** {species_info_1.get('clazz', 'N/A')}")
            st.markdown(f"**Order:** {species_info_1.get('order', 'N/A')}")
            st.markdown(f"**Family:** {species_info_1.get('family', 'N/A')}")
            st.markdown(f"**Genus:** {species_info_1.get('genus', 'N/A')}")
            st.markdown(f"**Species Key:** {species_info_1.get('key', 'N/A')}")
            
            if 'description' in species_info_1:
                st.markdown(f"**Description:** {species_info_1['description']}")

            # information for species two
            st.subheader(f"🔎 Species Information: {species_name_2}")
            st.markdown(f"**Scientific Name:** {species_info_2.get('scientificName', 'N/A')}")
            st.markdown(f"**Kingdom:** {species_info_2.get('kingdom', 'N/A')}")
            st.markdown(f"**Phylum:** {species_info_2.get('phylum', 'N/A')}")
            st.markdown(f"**Class:** {species_info_2.get('clazz', 'N/A')}")
            st.markdown(f"**Order:** {species_info_2.get('order', 'N/A')}")
            st.markdown(f"**Family:** {species_info_2.get('family', 'N/A')}")
            st.markdown(f"**Genus:** {species_info_2.get('genus', 'N/A')}")
            st.markdown(f"**Species Key:** {species_info_2.get('key', 'N/A')}")
            
            if 'description' in species_info_2:
                st.markdown(f"**Description:** {species_info_2['description']}")
            
            st.subheader("📍 Occurrence Data Comparison")
            
            # get data
            occurrences_1 = get_occurrences(species_name_1)
            occurrences_2 = get_occurrences(species_name_2)
            
            if occurrences_1 and occurrences_2:
                # make dataframe
                occ_df_1 = pd.DataFrame(occurrences_1)
                occ_df_2 = pd.DataFrame(occurrences_2)
                
                # data cleaning
                occ_df_1 = occ_df_1[['country', 'year', 'decimalLatitude', 'decimalLongitude']].dropna(subset=['year'])
                occ_df_2 = occ_df_2[['country', 'year', 'decimalLatitude', 'decimalLongitude']].dropna(subset=['year'])
                
                occ_df_1.columns = ['Country', 'Year', 'Latitude', 'Longitude']
                occ_df_2.columns = ['Country', 'Year', 'Latitude', 'Longitude']
                
                st.subheader(f"Occurrence Data for {species_name_1}")
                st.dataframe(occ_df_1)
                
                st.subheader(f"Occurrence Data for {species_name_2}")
                st.dataframe(occ_df_2)
                
           
                year_counts_1 = occ_df_1['Year'].value_counts().sort_index()
                year_counts_2 = occ_df_2['Year'].value_counts().sort_index()

                
                all_years = sorted(set(year_counts_1.index).union(year_counts_2.index))
                year_counts_1 = year_counts_1.reindex(all_years, fill_value=0)
                year_counts_2 = year_counts_2.reindex(all_years, fill_value=0)

                
                st.subheader("📈 Occurrences Over Time Comparison")

                fig, ax = plt.subplots()
                ax.plot(year_counts_1.index, year_counts_1.values, marker='o', label=species_name_1, color='blue')
                ax.plot(year_counts_2.index, year_counts_2.values, marker='o', label=species_name_2, color='red')
                
                ax.set_title('Occurrences Over Time Comparison')
                ax.set_xlabel('Year')
                ax.set_ylabel('Number of Occurrences')
                ax.legend()
                
                st.pyplot(fig)
                 #      Extract latitude and longitude for map plotting for both species
            latitudes_1 = [record.get("decimalLatitude") for record in occurrences_1 if record.get("decimalLatitude")]
            longitudes_1 = [record.get("decimalLongitude") for record in occurrences_1 if record.get("decimalLongitude")]
            latitudes_2 = [record.get("decimalLatitude") for record in occurrences_2 if record.get("decimalLatitude")]
            longitudes_2 = [record.get("decimalLongitude") for record in occurrences_2 if record.get("decimalLongitude")]

            if latitudes_1 and longitudes_1:
                occ_map_df_1 = pd.DataFrame({"latitude": latitudes_1, "longitude": longitudes_1})
                st.subheader(f"📍 Occurrences Map for {species_name_1}")
                st.map(occ_map_df_1)
            
            if latitudes_2 and longitudes_2:        
                occ_map_df_2 = pd.DataFrame({"latitude": latitudes_2, "longitude": longitudes_2})
                st.subheader(f"📍 Occurrences Map for {species_name_2}")
                st.map(occ_map_df_2)

elif option == "Climate Data":
    st.subheader("🌡️ Climate Data (Temperature) for Selected Locations")
    

    species_name_1 = st.text_input("Enter first species name:", "Panthera tigris")
    species_name_2 = st.text_input("Enter second species name:", "Loxodonta africana")
    

    species_info_1 = get_species_info(species_name_1)
    species_info_2 = get_species_info(species_name_2)
    
    if species_info_1 and species_info_2:
        # two species 
        occurrences_1 = get_occurrences(species_name_1, limit=1) 
        occurrences_2 = get_occurrences(species_name_2, limit=1)
        
        if occurrences_1 and occurrences_2:
            # take the latitudes and longitudes
            latitudes_1 = occurrences_1[0].get("decimalLatitude")
            longitudes_1 = occurrences_1[0].get("decimalLongitude")
            latitudes_2 = occurrences_2[0].get("decimalLatitude")
            longitudes_2 = occurrences_2[0].get("decimalLongitude")
            
            if latitudes_1 and longitudes_1:
                climate_data_1 = get_climate_data(latitudes_1, longitudes_1)
                if climate_data_1:
                    temp_1 = climate_data_1["main"]["temp"]
                    st.write(f"Temperature at {species_name_1} location ({latitudes_1}, {longitudes_1}): {temp_1}°C")
                else:
                    st.error(f"Could not fetch climate data for {species_name_1}")
            
            if latitudes_2 and longitudes_2:
                climate_data_2 = get_climate_data(latitudes_2, longitudes_2)
                if climate_data_2:
                    temp_2 = climate_data_2["main"]["temp"]
                    st.write(f"Temperature at {species_name_2} location ({latitudes_2}, {longitudes_2}): {temp_2}°C")
                else:
                    st.error(f"Could not fetch climate data for {species_name_2}")
                
            # Species Preferred Temperature for Survival
            if latitudes_1 and longitudes_1 and latitudes_2 and longitudes_2:
                st.subheader("🌡️ Species Preferred Temperature for Survival")
                
                temperature_data = {
                    species_name_1: temp_1 if latitudes_1 and longitudes_1 else None,
                    species_name_2: temp_2 if latitudes_2 and longitudes_2 else None
                }
                
                if all(value is not None for value in temperature_data.values()):
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.bar(temperature_data.keys(), temperature_data.values(), color=['blue', 'red'])
                    ax.set_xlabel('Species')
                    ax.set_ylabel('Temperature (°C)')
                    ax.set_title('Species Preferred Temperature for Survival')
                    st.pyplot(fig)
                else:
                    st.error("Unable to fetch temperature data for one or both species.")
        else:
            st.error("Could not retrieve occurrence data for one or both species.")
    else:
        st.error("Could not fetch species information for one or both species.")

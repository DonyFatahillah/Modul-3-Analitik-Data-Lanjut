import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector

# Function to establish connection to MySQL
def get_connection():
    try:
        connection = mysql.connector.connect(
            host='your-database-host',  # Ganti dengan alamat host database Anda
            user='your-username',        # Ganti dengan username Anda
            password='your-password',     # Ganti dengan password Anda
            database='your-database'      # Ganti dengan nama database Anda
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Function to fetch data from the database
def get_data_from_db():
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()  # Return an empty dataframe if the connection fails
    
    try:
        query = "SELECT * FROM pddikti_example"  # Ganti dengan nama tabel Anda
        df = pd.read_sql_query(query, conn)  # Use read_sql_query with mysql.connector
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()  # Return an empty dataframe if there's an error
    finally:
        conn.close()
    
    return df

# Title of the app
st.title('Streamlit Simple App')

# Adding sidebar navigation
page = st.sidebar.radio("Pilih halaman", ["Dataset", "Visualisasi", "Form Input"])

# Dataset Page
if page == "Dataset":
    st.header("Halaman Dataset")
    
    # Fetch data from the database
    data = get_data_from_db()

    # Display data in Streamlit
    if not data.empty:
        st.write(data)
    else:
        st.warning("Tidak ada data untuk ditampilkan.")

# Visualization Page
elif page == "Visualisasi":
    st.header("Halaman Visualisasi")
    
    # Fetch data from the database
    data = get_data_from_db()

    if not data.empty:
        # Filter by university
        selected_university = st.selectbox('Pilih Universitas', data['universitas'].unique())
        filtered_data = data[data['universitas'] == selected_university]

        # Create a new figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))

        for prog_studi in filtered_data['program_studi'].unique():
            subset = filtered_data[filtered_data['program_studi'] == prog_studi]
            subset = subset.sort_values(by='id', ascending=False)
            ax.plot(subset['semester'], subset['jumlah'], label=prog_studi)

        # Set plot titles and labels
        ax.set_title(f"Visualisasi Data untuk {selected_university}")
        ax.set_xlabel('Semester')
        ax.set_ylabel('Jumlah')
        ax.legend()
        ax.grid(True)  # Adding grid for better readability
        plt.xticks(rotation=90)  # Rotate x-axis labels vertically

        # Display figure in Streamlit
        st.pyplot(fig)
    else:
        st.warning("Data tidak tersedia untuk visualisasi.")

# Form Input Page
elif page == "Form Input":
    st.header("Halaman Form Input")
    
    # Input form
    with st.form(key='input_form'):
        input_semester = st.text_input('Semester')
        input_jumlah = st.number_input('Jumlah', min_value=0, format='%d')
        input_program_studi = st.text_input('Program Studi')
        input_universitas = st.text_input('Universitas')
        submit_button = st.form_submit_button(label='Submit Data')

    # On form submit, insert data into the database
    if submit_button:
        if input_semester and input_program_studi and input_universitas:
            conn = get_connection()
            if conn:
                cursor = conn.cursor()
                query = """
                INSERT INTO pddikti_example(semester, jumlah, program_studi, universitas)
                VALUES (%s, %s, %s, %s)
                """
                try:
                    cursor.execute(query, (input_semester, input_jumlah, input_program_studi, input_universitas))
                    conn.commit()
                    st.success("Data successfully submitted to the database!")
                except mysql.connector.Error as err:
                    st.error(f"Error inserting data: {err}")
                finally:
                    conn.close()
        else:
            st.warning("Mohon isi semua field pada form.")

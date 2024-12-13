import streamlit as st
import pandas as pd
import os
import base64

# Login function
def login():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "user" and password == "user":  # Replace with your authentication logic
            st.session_state['logged_in'] = True
            st.success("Login berhasil!")
        else:
            st.error("Username atau password salah.")

# Logout function
def logout():
    st.session_state['logged_in'] = False
    st.success("Anda Telah Log Out.")

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
else:
    # Fungsi untuk mengonversi gambar ke Base64
    def image_to_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Path ke gambar logo
    img_path = os.path.join('img', 'logo.png')  # Pastikan gambar berada di folder 'img' dan bernama 'logo.png'
    img_base64 = image_to_base64(img_path,)

    # Menampilkan gambar di tengah sidebar
    st.sidebar.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{img_base64}" alt="Logo" style="width: 250px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.markdown(
        """
        <div style="text-align: center; font-weight: bold;">
            Wisata Kabupaten Pasuruan
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Sidebar Menu
    menu = st.sidebar.radio("Pilih Menu", ["Home", "Rekomendasi Utility", "Rekomendasi Berdasarkan Kategori"])
    # Tambahkan tombol logout di sidebar
    if st.sidebar.button("Logout"):
        logout()
    st.sidebar.markdown(
        """
        <div style="text-align: center; font-weight: bold;">
            2024@byKelompok2
        </div>
        """, 
        unsafe_allow_html=True
    )

    # Path ke file CSV yang sudah ada
    wisata_file_path = os.path.join('data', 'data_wisata.csv')  # Ganti dengan path ke file 'data_wisata.csv'
    rating_file_path = os.path.join('data', 'data_rating.csv')  # Ganti dengan path ke file 'data_rating.csv'
    bobot_file_path = os.path.join('data', 'data_bobot.csv')  # Ganti dengan path ke file 'data_bobot.csv'

    # Home Page
    if menu == "Home":
        st.header("Selamat Datang di Aplikasi Rekomendasi Tempat Wisata di Kabupaten Pasuruan dengan Metode Utiliyt Based Recommendation")
        st.write("Aplikasi Rekomendasi Tempat Wisata di Kabupaten Pasuruan dengan Metode Utility-Based Recommendation adalah sebuah sistem yang dirancang untuk memberikan rekomendasi tempat wisata di Kabupaten Pasuruan berdasarkan preferensi dan kebutuhan pengguna. Metode yang digunakan, yaitu *utility-based recommendation*, mengandalkan analisis data yang telah dikumpulkan mengenai tempat wisata, rating atau penilaian pengguna, serta bobot dari berbagai atribut wisata (seperti lokasi, fasilitas, atau pemandangan). Sistem ini akan memberikan rekomendasi dengan menghitung skor utilitas untuk setiap tempat wisata, yang didasarkan pada tingkat kepuasan pengguna terhadap berbagai faktor yang relevan. Hasil dari perhitungan ini adalah urutan tempat wisata yang paling sesuai dengan preferensi pengguna, sehingga pengguna dapat lebih mudah menemukan tempat wisata yang sesuai dengan minat mereka, seperti Wisata Alam, Sejarah, Religi, Argo, Edukasi, Dan Kuliner. Dengan menggunakan aplikasi ini, wisatawan dapat memaksimalkan pengalaman mereka di Kabupaten Pasuruan dengan pilihan tempat wisata yang disesuaikan dengan kebutuhan dan preferensi individu.")
    # Rekomendasi Page
    elif menu == "Rekomendasi Utility":
        # Memuat dataset langsung dari file CSV yang sudah ada
        if os.path.exists(wisata_file_path) and os.path.exists(rating_file_path) and os.path.exists(bobot_file_path):
            # Muat dataset
            ratings = pd.read_csv(rating_file_path, header=None)
            wisata = pd.read_csv(wisata_file_path, header=None)
            bobot = pd.read_csv(bobot_file_path)

            # Tambahkan header untuk setiap dataset
            ratings.columns = ['ID Responden', 'Nama', 'Email', 'Umur', 'Jenis Kelamin', 'Asal Daerah'] + \
                            [f'Rating_{i}' for i in range(1, ratings.shape[1] - 6 + 1)]
            wisata.columns = ['No', 'Nama Wisata', 'Kategori']
            bobot.columns = ['NO', 'Atribut', 'kode', 'Bobot ']

            # Bersihkan nama kolom dengan menghapus spasi ekstra
            bobot.columns = bobot.columns.str.strip()

            # Tangani nilai yang hilang dengan menghapus baris yang mengandung nilai NaN
            ratings = ratings.dropna()  # Menghapus baris dengan nilai NaN

            # Konversi rating menjadi numerik dan pastikan pemetaan yang tepat
            rating_columns = [col for col in ratings.columns if 'Rating' in col]
            ratings[rating_columns] = ratings[rating_columns].apply(pd.to_numeric, errors='coerce')

            # Pastikan rating berada dalam rentang yang valid (misalnya, 1 hingga 5)
            ratings[rating_columns] = ratings[rating_columns].clip(lower=1, upper=5)

            # Hapus baris yang masih mengandung NaN setelah konversi dan pemotongan
            ratings = ratings.dropna(subset=rating_columns)

            # Buat matriks utilitas pengguna-item
            ratings_utility_matrix = ratings[rating_columns]
            ratings_utility_matrix.index = ratings['ID Responden']

            # Normalisasi rating (skala setiap rating responden menjadi rentang 0 hingga 1)
            normalized_ratings = ratings_utility_matrix.div(ratings_utility_matrix.max(axis=1), axis=0)

            # Inisialisasi bobot dari dataset bobot dan normalisasi mereka
            bobot['Bobot'] = bobot['Bobot'].astype(float)  # Perbaiki kolom 'Bobot'
            bobot['Bobot Normalisasi'] = bobot['Bobot'] / bobot['Bobot'].sum()

            # Buat pemetaan bobot dari kolom 'kode' ke 'Bobot Normalisasi'
            weights = dict(zip(bobot['kode'], bobot['Bobot Normalisasi']))

            # Pemetaan bobot ke kolom rating yang sesuai
            weight_mapping_filtered = {f'Rating_{i+1}': weights.get(f'K{i+1}', 0) for i in range(len(rating_columns))}

            # Hitung skor utilitas untuk setiap tempat wisata
            utility_scores = normalized_ratings.dot(pd.Series(weight_mapping_filtered))

            # Bersihkan kolom 'No' di 'wisata' untuk memastikan hanya berisi angka
            wisata['No'] = pd.to_numeric(wisata['No'], errors='coerce')  # Konversi menjadi numerik, nilai non-numerik jadi NaN
            wisata = wisata.dropna(subset=['No'])  # Hapus baris dengan 'No' NaN

            # Pastikan kolom 'No' bertipe integer
            wisata['No'] = wisata['No'].astype(int)

            # Inisialisasi daftar untuk menyimpan skor utilitas teragregasi untuk setiap tempat wisata
            aggregated_scores = []

            # Input jumlah rekomendasi yang diinginkan
            top_n = st.number_input("Masukkan jumlah rekomendasi yang diinginkan:", min_value=0, value=0, step=0)

            # Iterasi melalui setiap tempat wisata
            for spot_id in wisata['No']:  # Sekarang spot_id dipastikan merupakan angka
                # Ambil rating untuk tempat wisata saat ini dari setiap responden
                spot_ratings = ratings[rating_columns].apply(lambda row: row[spot_id - 1] if row[spot_id - 1] > 0 else 0, axis=1)
                
                # Normalisasi dan agregasi skor utilitas untuk tempat wisata ini di seluruh responden
                aggregated_scores.append({
                    'No': spot_id,
                    'Total Utility Score': spot_ratings.sum()
                })

            # Konversi skor teragregasi menjadi DataFrame
            aggregated_scores_df = pd.DataFrame(aggregated_scores)

            # Urutkan berdasarkan total skor utilitas (descending)
            top_spots = aggregated_scores_df.sort_values(by='Total Utility Score', ascending=False).head(top_n)

            # Pemetaan nama tempat wisata teratas dari dataframe 'wisata'
            top_spots_names = wisata.loc[wisata['No'].isin(top_spots['No']), 'Nama Wisata']

            # Siapkan output dengan tempat wisata teratas
            top_recommendations = pd.DataFrame({
                'Wisata': top_spots_names.values,
                'Total Utility Score': top_spots['Total Utility Score'].values
            })

            # Tampilkan rekomendasi tempat wisata teratas
            st.write(f"Top {top_n} Rekomendasi Tempat Wisata:")
            st.write(top_recommendations)

        else:
            st.warning("File CSV tidak ditemukan di folder data.")

    # Rekomendasi Berdasarkan Kategori Page
    elif menu == "Rekomendasi Berdasarkan Kategori":
        # Memuat dataset langsung dari file CSV yang sudah ada
        if os.path.exists(wisata_file_path) and os.path.exists(rating_file_path) and os.path.exists(bobot_file_path):
            # Muat dataset
            ratings = pd.read_csv(rating_file_path, header=None)
            wisata = pd.read_csv(wisata_file_path, header=None)
            bobot = pd.read_csv(bobot_file_path)

            # Tambahkan header untuk setiap dataset
            ratings.columns = ['ID Responden', 'Nama', 'Email', 'Umur', 'Jenis Kelamin', 'Asal Daerah'] + \
                            [f'Rating_{i}' for i in range(1, ratings.shape[1] - 6 + 1)]
            wisata.columns = ['No', 'Nama Wisata', 'Kategori']
            bobot.columns = ['NO', 'Atribut', 'kode', 'Bobot ']

            # Bersihkan nama kolom dengan menghapus spasi ekstra
            bobot.columns = bobot.columns.str.strip()

            # Tangani nilai yang hilang dengan menghapus baris yang mengandung nilai NaN
            ratings = ratings.dropna()  # Menghapus baris dengan nilai NaN

            # Konversi rating menjadi numerik dan pastikan pemetaan yang tepat
            rating_columns = [col for col in ratings.columns if 'Rating' in col]
            ratings[rating_columns] = ratings[rating_columns].apply(pd.to_numeric, errors='coerce')

            # Pastikan rating berada dalam rentang yang valid (misalnya, 1 hingga 5)
            ratings[rating_columns] = ratings[rating_columns].clip(lower=1, upper=5)

            # Hapus baris yang masih mengandung NaN setelah konversi dan pemotongan
            ratings = ratings.dropna(subset=rating_columns)

            # Buat matriks utilitas pengguna-item
            ratings_utility_matrix = ratings[rating_columns]
            ratings_utility_matrix.index = ratings['ID Responden']

            # Normalisasi rating (skala setiap rating responden menjadi rentang 0 hingga 1)
            normalized_ratings = ratings_utility_matrix.div(ratings_utility_matrix.max(axis=1), axis=0)

            # Inisialisasi bobot dari dataset bobot dan normalisasi mereka
            bobot['Bobot'] = bobot['Bobot'].astype(float)  # Perbaiki kolom 'Bobot'
            bobot['Bobot Normalisasi'] = bobot['Bobot'] / bobot['Bobot'].sum()

            # Buat pemetaan bobot dari kolom 'kode' ke 'Bobot Normalisasi'
            weights = dict(zip(bobot['kode'], bobot['Bobot Normalisasi']))

            # Pemetaan bobot ke kolom rating yang sesuai
            weight_mapping_filtered = {f'Rating_{i+1}': weights.get(f'K{i+1}', 0) for i in range(len(rating_columns))}

            # Hitung skor utilitas untuk setiap tempat wisata
            utility_scores = normalized_ratings.dot(pd.Series(weight_mapping_filtered))

            # Bersihkan kolom 'No' di 'wisata' untuk memastikan hanya berisi angka
            wisata['No'] = pd.to_numeric(wisata['No'], errors='coerce')  # Konversi menjadi numerik, nilai non-numerik jadi NaN
            wisata = wisata.dropna(subset=['No'])  # Hapus baris dengan 'No' NaN

            # Pastikan kolom 'No' bertipe integer
            wisata['No'] = wisata['No'].astype(int)

            # Menampilkan pilihan kategori untuk pemfilteran
            selected_category = st.selectbox("Pilih Kategori Wisata", wisata['Kategori'].unique())

            # Filter tempat wisata berdasarkan kategori yang dipilih
            filtered_wisata = wisata[wisata['Kategori'] == selected_category]

            # Inisialisasi daftar untuk menyimpan skor utilitas teragregasi untuk setiap tempat wisata
            aggregated_scores = []

            # Input jumlah rekomendasi yang diinginkan
            top_n = st.number_input("Masukkan jumlah rekomendasi yang diinginkan:", min_value=0, value=0, step=0)

            # Iterasi melalui tempat wisata yang telah difilter berdasarkan kategori
            for spot_id in filtered_wisata['No']:  # Sekarang spot_id dipastikan merupakan angka
                # Ambil rating untuk tempat wisata saat ini dari setiap responden
                spot_ratings = ratings[rating_columns].apply(lambda row: row[spot_id - 1] if row[spot_id - 1] > 0 else 0, axis=1)
                
                # Normalisasi dan agregasi skor utilitas untuk tempat wisata ini di seluruh responden
                aggregated_scores.append({
                    'No': spot_id,
                    'Total Utility Score': spot_ratings.sum()
                })

            # Konversi skor teragregasi menjadi DataFrame
            aggregated_scores_df = pd.DataFrame(aggregated_scores)

            # Urutkan berdasarkan total skor utilitas (descending)
            top_spots = aggregated_scores_df.sort_values(by='Total Utility Score', ascending=False).head(top_n)

            # Pemetaan nama tempat wisata teratas dari dataframe 'wisata'
            top_spots_names = filtered_wisata.loc[filtered_wisata['No'].isin(top_spots['No']), 'Nama Wisata']

            # Siapkan output dengan tempat wisata teratas
            top_recommendations = pd.DataFrame({
                'Wisata': top_spots_names.values,
                'Total Utility Score': top_spots['Total Utility Score'].values
            })

            # Tampilkan rekomendasi tempat wisata teratas berdasarkan kategori
            st.write(f"Top {top_n} Rekomendasi Tempat Wisata di Kategori '{selected_category}':")
            st.write(top_recommendations)

        else:
            st.warning("File CSV tidak ditemukan di folder data.")

import streamlit as st
from participants import peserta_putri, peserta_putra
import os
import uuid
from gtts import gTTS
import pygame
import hashlib
from time import sleep

pygame.mixer.init()

# Fungsi untuk menyimpan data ke file
def save_to_file(selected_options):
    with open("selected_antrian.txt", "w") as file:
        for option in selected_options:
            file.write(option + "\n")

# Fungsi untuk membaca data dari file
def read_from_file(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r") as file:
        return file.readlines()

# Fungsi untuk mendapatkan hash dari file
def get_file_hash(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Fungsi untuk mengkonversi teks ke suara
def text_to_speech(text, lang='id'):
    # Generate a unique filename
    unique_filename = f"announcement_{uuid.uuid4()}.mp3"
    
    # Convert text to speech
    tts = gTTS(text=text, lang=lang)
    tts.save(unique_filename)
    
    # Initialize pygame mixer
    pygame.mixer.music.load(unique_filename)
    pygame.mixer.music.play()
    
    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        continue
    
    # Clean up the file
    try:
        if os.path.exists(unique_filename):
            os.remove(unique_filename)
    except Exception as e:
        print(f"Error removing file: {e}")

# Fungsi untuk halaman Pemilihan Data
def show_selection_page():
    st.title("Pemilihan Data Peserta : ")
    
    # Gabungkan daftar peserta
    participants = peserta_putri + peserta_putra
    
    # Generate options with number.name format
    options = [f"{i+1}. {name}" for i, name in enumerate(participants)]
    
    # Allow users to select multiple options
    selected_options = st.multiselect("Pilih Nomor Antrian", options)
    
    # Button to submit selected options
    if st.button("Submit"):
        if selected_options:
            save_to_file(selected_options)  # Save selected options to file
            st.success("Data berhasil disimpan.")
        else:
            st.error("Tidak ada data yang dipilih.")

# Fungsi untuk halaman Tampilan Antrian
def show_announcement_page():
    st.header("JIKA NOMOR ABSEN DAN NAMA TERTERA MOHON HUBUNGI PJ YANG SUDAH DI TENTUKAN")
    
    # Buat tempat untuk menampilkan antrian
    placeholder = st.empty()
    
    # Dapatkan hash file saat ini
    current_hash = get_file_hash("selected_antrian.txt")
    
    # Simpan hash file untuk pengecekan di sesi berikutnya
    if 'last_hash' not in st.session_state:
        st.session_state.last_hash = current_hash
    
    # Loop untuk terus memperbarui halaman
    while True:
        # Baca data dari file
        lines = read_from_file("selected_antrian.txt")
        
        # Dapatkan hash file saat ini
        current_hash = get_file_hash("selected_antrian.txt")
        
        # Jika hash file berubah, tampilkan dan bacakan suara
        if current_hash != st.session_state.last_hash:
            st.session_state.last_hash = current_hash  # Update hash terakhir
            placeholder.text("Data Antrian:")
            for line in lines:
                st.title(line.strip())  # Tampilkan setiap baris dari file
                text_to_speech(line.strip())  # Konversi teks ke suara
                f = open('data_lewat.txt','a')
                f.write((line.strip()))
                f.close()
        
        # Tunda beberapa detik sebelum memeriksa lagi

        sleep(60)  # Adjust sleep time as necessary
        st.experimental_rerun()  # Rerun aplikasi untuk pembaruan



# Main interface
col1, col2 = st.columns([1, 1])

from streamlit_option_menu import option_menu
selected = option_menu(None, ['Pemilihan Data','Tampilan Antrian'], 
    icons=['house',"list-task", 'gear'], 
    menu_icon="cast", default_index=0, orientation="horizontal")

if selected == "Pemilihan Data":
    show_selection_page()
elif selected == "Tampilan Antrian":
    show_announcement_page()

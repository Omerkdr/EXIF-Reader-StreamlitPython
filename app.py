import streamlit as st
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import folium
from streamlit_folium import folium_static

def get_exif_data(image):
    exif_data = {}
    with Image.open(image) as img:
        exif = img._getexif()
        if exif is not None:
            for tag_id in exif:
                tag = TAGS.get(tag_id, tag_id)
                value = exif.get(tag_id)
                if isinstance(value, bytes):
                    value = value.decode()
                if tag == "GPSInfo":
                    gps_data = {}
                    for gps_tag_id in value:
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_value = value[gps_tag_id]
                        if isinstance(gps_value, bytes):
                            gps_value = gps_value.decode()
                        gps_data[gps_tag] = gps_value
                    value = gps_data
                exif_data[tag] = value
    return exif_data

def convert_to_degrees(value):
    degrees = value[0]
    minutes = value[1]
    seconds = value[2]
    return degrees + (minutes / 60) + (seconds / 3600)

st.title("EXIF Dosya Bilgisi Okuyucu ve Konum Bulucu")
uploaded_file = st.file_uploader("JPG veya PNG dosyanızı yükleyin", type=["jpg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Yüklenen dosya", use_column_width=True)
    st.write("Dosya adı:", uploaded_file.name)
    st.write("Dosya boyutu:", uploaded_file.size)
    exif_data = get_exif_data(uploaded_file)
    st.write("EXIF Bilgileri:")
    for key, value in exif_data.items():
        if key == "GPSInfo":
            st.write("GPS Bilgileri:")
            for gps_key, gps_value in value.items():
                st.write(f"{gps_key}: {gps_value}")
            if "GPSLatitude" in value and "GPSLongitude" in value:
                lat = convert_to_degrees(value["GPSLatitude"])
                lat_ref = value.get("GPSLatitudeRef")
                if lat_ref == "S":
                    lat = 0 - lat
                lon = convert_to_degrees(value["GPSLongitude"])
                lon_ref = value.get("GPSLongitudeRef")
                if lon_ref == "W":
                    lon = 0 - lon
                st.write(f"Koordinatlar: ({lat}, {lon})")
                map = folium.Map(location=[lat, lon], zoom_start=15)
                folium.Marker(location=[lat, lon]).add_to(map)
                folium_static(map)
        else:
            st.write(f"{key}: {value}")
else:
    st.write("Dosya yüklenemedi.")

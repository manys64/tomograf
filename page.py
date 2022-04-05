import base64
import io

import streamlit as st
from PIL import Image

import computed_tomography as ct
import save_dicom
import numpy as np
from skimage.io import imread


def normalize_image(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))


st.set_page_config(page_title="Tomograf")

# uklad obrotu max 180 stopni
# dla 360 bedzie o pol stopnia
# luk max 180 stopni
# 360 detektorow i emiterow
with st.sidebar:
    number_of_scans = st.number_input("Number of scans", 10, 360, 90, step=1)
    number_of_detectors = st.number_input("Number of detectors", 10, 180, 50, step=1)
    beam_extent = st.number_input("Beam extent", 10, 100, 50, step=1)
    sinogram = st.checkbox("Filter sinogram")

original_image = st.file_uploader("Choose image file", type=["png", "jpg", "jpeg", "dcm"])
# tutaj if jesli dicom to wykonuje wersje funkcji dla dicoma

if original_image:
    if original_image.type == "application/dicom":
        image, info = save_dicom.read_dicom(original_image)
        st.markdown("Name: " + str(info.get('PatientName')))
        st.markdown("ID: " + info.get('PatientID'))
        st.markdown("Comments: " + str(info.get('ImageComments')))
        image = (image - np.min(image)) / (np.max(image) - np.min(image))
    else:
        image = imread(original_image, True)
    st.image(image, "Original image")
    tomograph = ct.Tomograph()
    output = tomograph.scanner(image, number_of_detectors, number_of_scans, beam_extent, False)
    image_version = st.slider("Iteration", 1, len(output), len(output))
    st.image(normalize_image(output[image_version - 1]), "Proceed image")

    save_as = st.radio("Save as: ", ["JPG", "DICOM"])
    st.text(save_as)
    if save_as == "JPG":
        file_name = st.text_input("File name")
        file_name = file_name + ".jpg" if len(file_name) else "processed_file.jpg"
        result = Image.fromarray(normalize_image(output[image_version - 1]), "RGB")
        buffered = io.BytesIO()
        result.save(buffered, format="JPEG")
        data = base64.b64encode(buffered.getvalue()).decode()
        st.markdown(f'<a type="button" href="data:file/txt;base64,{data}" download="{file_name}">Save file</a>',
                    unsafe_allow_html=True)

    else:
        patient_name = st.text_input("Patient name")
        patient_id = st.number_input("Patient ID", 0, 100000, 0, 1)
        comment = st.text_area("Comment")
        patient_dict = {
            "PatientName": patient_name,
            "PatientID": patient_id,
            "ImageComments": comment
        }
        file_name = patient_name + ".dcm" if len(patient_name) else "processed_file.dcm"
        st.download_button("Save file", save_dicom.save_as_dicom(image, patient_dict), file_name)

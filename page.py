import skimage.io
import streamlit as st
import computed_tomography as ct
import save_dicom
import numpy as np
from skimage.io import imread


def normalize_image(data):
    return (data - np.min(data)) / (np.max(data) - np.min(data))


st.set_page_config(page_title="Tomograf")

with st.sidebar:
    number_of_scans = st.number_input("Number of scans", 10, 360, 90, step=1)
    number_of_detectors = st.number_input("Number of detectors", 10, 360, 180, step=1)
    beam_extent = st.number_input("Beam extent", 10, 180, 100, step=1)
    filter_sino = st.checkbox("Filter sinogram")

original_image = st.file_uploader("Choose image file", type=["png", "jpg", "jpeg", "dcm"])

if original_image:
    if original_image.type == "application/octet-stream":#windows
 #  if original_image.type == "application/dicom":#linux
        "Patient info:"
        image, info = save_dicom.read_dicom(original_image)
        st.write("Name: " + str(info.get('PatientName')))
        st.markdown("ID: " + info.get('PatientID'))
        st.markdown("Comments: " + str(info.get('ImageComments')))
        image = (image - np.min(image)) / (np.max(image) - np.min(image))
    else:
        image = imread(original_image, True)
    if filter_sino:
        "Program is in filtered sinogram mode"
    st.image(image, "Original image")
    tomograph = ct.Tomograph()
    output, sinogram = tomograph.scanner(image, number_of_detectors, number_of_scans, beam_extent, filter_sino)
    st.image(normalize_image(sinogram), "Final sinogram", 500)
    image_version = st.slider("Iteration", 1, len(output), len(output))
    st.image(normalize_image(output[image_version - 1]), "Proceed image")

    save_as = st.radio("Save as: ", ["JPG", "DICOM"])
    st.text(save_as)
    if save_as == "JPG":
        file_name = st.text_input("File name")
        file_name = file_name + ".jpg" if len(file_name) else "processed_file.jpg"
        if st.button("Save on disk"):
            skimage.io.imsave(file_name, np.array(normalize_image(sinogram)))

    else:
        patient_name = st.text_input("Patient name")
        patient_id = st.number_input("Patient ID", 0, value=0, step=1)
        comment = st.text_area("Comment")
        patient_dict = {
            "PatientName": patient_name,
            "PatientID": str(patient_id),
            "ImageComments": comment
        }
        file_name = patient_name + ".dcm" if len(patient_name) else "processed_file.dcm"
        if st.button("Save on disk"):
            save_dicom.save_as_dicom(file_name, np.array(normalize_image(output[len(output)-1])), patient_dict)

from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian
import pydicom._storage_sopclass_uids
import skimage.io as io
from skimage.util import img_as_ubyte
from skimage.exposure import rescale_intensity


def read_dicom(path):
    from pydicom import dcmread
    ds = dcmread(path)
    # assume dicom metadata identifiers are uppercase
    keys = {x for x in dir(ds) if x[0].isupper()} - {'PixelData'}
    meta = {x: getattr(ds, x) for x in keys}
    image = ds.pixel_array
    return image, meta


def convert_image_to_ubyte(img):
    return img_as_ubyte(rescale_intensity(img, out_range=(0.0, 1.0)))


def save_as_dicom(img, patient_data):
    # image = io.imread(img, as_gray=True)
    img_converted = convert_image_to_ubyte(img)

    # Populate required values for file meta information
    meta = Dataset()
    meta.MediaStorageSOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
    meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    meta.TransferSyntaxUID = pydicom.uid.ExplicitVRLittleEndian

    ds = FileDataset(None, {}, preamble=b"\0" * 128)
    ds.file_meta = meta

    ds.is_little_endian = True
    ds.is_implicit_VR = False

    ds.SOPClassUID = pydicom._storage_sopclass_uids.CTImageStorage
    ds.SOPInstanceUID = meta.MediaStorageSOPInstanceUID

    ds.PatientName = patient_data["PatientName"]
    ds.PatientID = patient_data["PatientID"]
    ds.ImageComments = patient_data["ImageComments"]

    ds.Modality = "CT"
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.FrameOfReferenceUID = pydicom.uid.generate_uid()

    ds.BitsStored = 8
    ds.BitsAllocated = 8
    ds.SamplesPerPixel = 1
    ds.HighBit = 7

    ds.ImagesInAcquisition = 1
    ds.InstanceNumber = 1

    ds.Rows, ds.Columns = img_converted.shape

    ds.ImageType = r"ORIGINAL\PRIMARY\AXIAL"

    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.PixelRepresentation = 0

    pydicom.dataset.validate_file_meta(ds.file_meta, enforce_standard=True)

    ds.PixelData = img_converted.tobytes()

    # return ds

    ds.save_as("file_name", write_like_original=False)

# input_image = 'Shepp_logan.jpg'
# patient_dict = {
#     "PatientName": 'Jan Nowak',
#     "PatientID": '11432',
#     "ImageComments": 'Kidney surgery tomograph photo'
# }
#
# # sprawdzone w https://www.imaios.com/en/Imaios-Dicom-Viewer
# save_as_dicom('shepp.dcm', input_image, patient_dict)
#
# image, meta = read_dicom('shepp.dcm')
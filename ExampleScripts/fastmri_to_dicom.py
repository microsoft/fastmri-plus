import datetime
import os
from pathlib import Path

import argparse
import h5py
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence
from pydicom.uid import generate_uid

import xmltodict

def fastmri_to_dicom(filename: Path,
    reconstruction_name: str,
    outfolder: Path,
    flip_up_down: bool = False,
    flip_left_right: bool = False) -> None:

    fileparts = os.path.splitext(filename.name)
    patientName = fileparts[0]
    f = h5py.File(filename,'r')

    if not outfolder:
        outfolder = Path(patientName)
        outfolder.mkdir(parents=bool, exist_ok=True)

    if 'ismrmrd_header' not in f.keys():
        raise Exception('ISMRMRD header not found in file')

    if reconstruction_name not in f.keys():
        raise Exception('Reconstruction name not found in file')

    # Get some header information
    head = xmltodict.parse(f['ismrmrd_header'][()])
    reconSpace = head['ismrmrdHeader']['encoding']['reconSpace'] # ['matrixSize', 'fieldOfView_mm']
    measurementInformation = head['ismrmrdHeader']['measurementInformation'] # ['measurementID', 'patientPosition', 'protocolName', 'frameOfReferenceUID']
    acquisitionSystemInformation = head['ismrmrdHeader']['acquisitionSystemInformation'] # ['systemVendor', 'systemModel', 'systemFieldStrength_T', 'relativeReceiverNoiseBandwidth' 'receiverChannels', 'coilLabel', 'institutionName']
    H1resonanceFrequency_Hz = head['ismrmrdHeader']['experimentalConditions']['H1resonanceFrequency_Hz']
    sequenceParameters = head['ismrmrdHeader']['sequenceParameters'] # ['TR', 'TE', 'TI', 'flipAngle_deg', 'sequence_type', 'echo_spacing']

    # Some calculated values
    pixelSizeX = float(reconSpace['fieldOfView_mm']['x'])/float(reconSpace['matrixSize']['x'])
    pixelSizeY = float(reconSpace['fieldOfView_mm']['y'])/float(reconSpace['matrixSize']['y'])

    # Get and prep pixel data
    img_data = f[reconstruction_name][:]
    slices = img_data.shape[0]

    if flip_left_right:
        img_data = img_data[:, :, ::-1]

    if flip_up_down:
        img_data = img_data[:, ::-1, :]

    image_max = 1024
    scale = image_max / np.percentile(img_data, 99.9)
    pixels_scaled = np.clip((scale * img_data), 0, image_max).astype('int16')
    windowWidth = 2 * (np.percentile(pixels_scaled, 99.9) - np.percentile(pixels_scaled, 0.1))
    windowCenter = windowWidth/2

    studyInstanceUid = generate_uid('999.')
    seriesInstanceUid = generate_uid('9999.')

    for s in range(0, slices):
        slice_filename = "%s_%03d.dcm"%(patientName, s)
        slice_full_path = outfolder/slice_filename
        slice_pixels = pixels_scaled[s,:,:]

        # File meta info data elements
        file_meta = FileMetaDataset()
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
        file_meta.MediaStorageSOPInstanceUID = "1.2.3"
        file_meta.ImplementationClassUID = "1.2.3.4"
        file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'

        # Main data elements
        ds = Dataset()

        dt = datetime.datetime.now()
        ds.ContentDate = dt.strftime('%Y%m%d')
        timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
        ds.SOPClassUID = '1.2.840.10008.5.1.4.1.1.4'
        ds.SOPInstanceUID = generate_uid('9999.')
        ds.ContentTime = timeStr
        ds.Modality = 'MR'
        ds.ModalitiesInStudy = ['', 'PR', 'MR', '']
        ds.StudyDescription = measurementInformation['protocolName']
        ds.PatientName = patientName
        ds.PatientID = patientName
        ds.PatientBirthDate = '19700101'
        ds.PatientSex = 'M'
        ds.PatientAge = '030Y'
        ds.PatientIdentityRemoved = 'YES'
        ds.MRAcquisitionType = '2D'
        ds.SequenceName = sequenceParameters['sequence_type']
        ds.SliceThickness = reconSpace['fieldOfView_mm']['z']
        ds.RepetitionTime = sequenceParameters['TR']
        ds.EchoTime = sequenceParameters['TE']
        ds.ImagingFrequency = H1resonanceFrequency_Hz
        ds.ImagedNucleus = '1H'
        ds.EchoNumbers = "1"
        ds.MagneticFieldStrength = acquisitionSystemInformation['systemFieldStrength_T']
        ds.SpacingBetweenSlices = reconSpace['fieldOfView_mm']['z'] # 2D, assume 0 slice spacing
        ds.FlipAngle = str(sequenceParameters['flipAngle_deg'])
        ds.PatientPosition = measurementInformation['patientPosition']
        ds.StudyInstanceUID = studyInstanceUid
        ds.SeriesInstanceUID = seriesInstanceUid
        ds.StudyID = measurementInformation['measurementID']
        ds.InstanceNumber = str(s+1)
        ds.ImagesInAcquisition = str(slices)
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = 'MONOCHROME2'
        ds.NumberOfFrames = "1"
        ds.Rows = slice_pixels.shape[0]
        ds.Columns = slice_pixels.shape[1]
        ds.PixelSpacing = [pixelSizeX, pixelSizeY]
        ds.PixelAspectRatio = [1, 1]
        ds.BitsAllocated = 16
        ds.BitsStored = 12
        ds.HighBit = 11
        ds.PixelRepresentation = 1 
        ds.SmallestImagePixelValue = 0
        ds.LargestImagePixelValue = 1024
        ds.BurnedInAnnotation = 'NO'
        ds.WindowCenter = str(windowCenter)
        ds.WindowWidth = str(windowWidth)
        ds.LossyImageCompression = '00'
        ds.StudyStatusID = 'COMPLETED'
        ds.ResultsID = ''

        ds.PixelData = slice_pixels

        ds.file_meta = file_meta
        ds.is_implicit_VR = False
        ds.is_little_endian = True
        ds.save_as(slice_full_path, write_like_original=False)

def main() -> None:
    parser = argparse.ArgumentParser(description='Convert fastMRI file to DICOMs')
    parser.add_argument('--filename' , type=str, help='File name', required=True)
    parser.add_argument('--reconstruction_name' , type=str, help='Reconstruction name', default='reconstruction_rss', required=False)
    parser.add_argument('--outfolder', type=str, help='Output folder', required = False)
    parser.add_argument('--flip_up_down', type=bool, help='Flip image up/down', default=True)
    parser.add_argument('--flip_left_right', type=bool, help='Flip image left/right', default=False)
    args = parser.parse_args()

    fastmri_to_dicom(filename = Path(args.filename),
        reconstruction_name=args.reconstruction_name,
        outfolder=args.outfolder,
        flip_up_down=args.flip_up_down,
        flip_left_right=args.flip_left_right)

if __name__ == '__main__':
    main()
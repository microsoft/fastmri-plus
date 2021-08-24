# fastMRI+: Clinical pathology annotations for the [fastMRI](https://fastmri.org) dataset

The [fastMRI](https://fastmri.org) dataset is a publicly available MRI raw (k-space) dataset. It has been used widely to train machine learning models for image reconstruction and has been used in [reconstruction challenges](https://ieeexplore.ieee.org/document/9420272). 

This repo includes clinical pathology annotations for this dataset. The entire knee dataset and approximately 1000 brain datasets have been labeled. The goal of providing these labels is to enable developers of image reconstruction models and algorithms to evaluate the performance of the developed techniques with a focus on the sections or regions that could contain clinical pathology.

## Limitations

Each image has labeled by a single radiologist and without the benefit of looking at other views and angles of the same subject, and should therefore be considered in that context. Specifically, the labels should not be considered clinical ground truth or an exhaustive list of all lesions but rather an indicatition of where a pathology could be present.

# Obtaining fastMRI raw data and images

The fastMRI raw data and reference images can be obtained from [fastmri.org](https://fastmri.org/dataset/). You will be able to download and use the data for academic purposes after signing the data sharing agreement. If you are looking for automation for downloading the dataset and [training fastMRI models](https://github.com/facebookresearch/fastMRI), please see the [InnerEye Deep Learning Toolkit](https://github.com/microsoft/InnerEye-DeepLearning/blob/main/docs/fastmri.md).

# Labeling procedure and generating DICOM images from fastMRI data

In order to label the data, DICOM files were generated from the fastMRI dataset, and we are providing a [`fastmri_to_dicom.py`](ExampleScripts/fastmri_to_dicom.py) to document the procedure. This script can be used like this:

```bash
python fastmri_to_dicom.py --filename fastmridatafile.h5
```

> Note: In the process of converting the images to DICOM, the pixel arrays were flipped (up/down) to provide a view that was closer to DICOM orientation and assist with labeling. This should be taken into consideration when using the labels. 

The labeling was performed by experienced radiologists using the [MD.ai](https://md.ai/).

# Working with the annotations

The [Annotations](Annotations/) folder contains a label file for each of the knee ([knee.csv](Annotations/knee.csv) and brain ([brain.csv](Annotations/brain.csv) datasets. The files contain one line for each annotation (bounding box) that was labeled by the radiologists. Datasets with no findings (no annotations) are not represented in the label files, however, you can see which files were reviewed in the [brain_file_list.csv](Annotations/brain_file_list.csv) and [knee_file_list.csv](Annotations/knee_file_list.csv). If a dataset (a fastMRI file) is listed in the file lists but not in the label files, it means that it has been reviewed, but there were no findings. 

The repo contains an [example jupyter notebook](ExampleScripts/example.ipynb), which illustrates how to read the labels and overlay them onto the image pixels.

## Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

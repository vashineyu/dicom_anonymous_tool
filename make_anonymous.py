"""
Version date: 20190314
"""
import os
import glob
import pydicom
import argparse
from pydicom.data import get_testdata_files
from pydicom.filereader import read_dicomdir

# FIELDS TO REMOVE
REMOVED_FIELDS = [
    'PatientName',                      # (0010,0010)
    'OtherPatientNames',                # (0010,1001)
    'PatientBirthName',                 # (0010,1005)
    'PatientMotherBirthName',           # (0010,1060)
    'ResponsiblePerson',                # (0010,2297)
    'ReferringPhysicianName',           # (0008,0090)
    'PerformingPhysicianName',          # (0008,1050)
    'OperatorsName',                    # (0008,1070)
    'OtherPatientIDs',                  # (0010,1000)
    'OtherPatientIDsSequence',          # (0010,1002)
    'PatientBirthDate',                 # (0010,0030)
    'PatientBirthTime',                 # (0010,0032)
    'EthnicGroup',                      # (0010,2160)
    'PatientBreedCodeSequence',         # (0010,2293)
    'BreedRegistrationSequence',        # (0010,2294)
    'BreedRegistrationNumber',          # (0010,2295)
    'BreedRegistryCodeSequence',        # (0010,2296)
    'PatientSpeciesCodeSequence',       # (0010,2202)
    'MilitaryRank',                     # (0010,1080)
    'BranchOfService',                  # (0010,1081)
    'Occupation',                       # (0010,2180)
    'PatientID',                        # (0010,0020)
    'IssuerOfPatientID',                # (0010,0021)
    'TypeOfPatientID',                  # (0010,0022)
    'MedicalRecordLocator',             # (0010,1090)
    'AdditionalPatientHistory',         # (0010,21B0)
    'LastMenstrualDate',                # (0010,21D0)
    'PatientSexNeutered',               # (0010,2203)
    'PregnancyStatus',                  # (0010,21C0)
    'PatientAddress',                   # (0010,1040)
    'CountryOfResidence',               # (0010,2150)
    'RegionOfResidence',                # (0010,2152)
    'PatientTelephoneNumbers',          # (0010,2154)
    'PatientInsurancePlanCodeSequence', # (0010,0050)
    'InsurancePlanIdentification',      # (0010,1050)
    'PatientPrimaryLanguageCodeSeq',    # (0010,0101)
    'PatientPrimaryLanguageCodeModSeq', # (0010,0102)
    'PatientReligiousPreference',       # (0010,21F0)
    'ResponsiblePersonRole',            # (0010,2298)
    'ResponsibleOrganization',          # (0010,2299)
    'AccessionNumber',                  # (0008,0050)
    'InstitutionName',                  # (0008,0080)
]

def parse_patient_record(patient_record):
    """Parse patient record.
    
    Args:
        patient_record (object): object from DICOMDIR level 0 object
        
    Returns:
        children_object
        appending_keys
    """
    patient_id = patient_record.PatientID
    #patient_name = patient_record.PatientName
    
    return patient_record.children, patient_id

def parse_study(study):
    """Parse study
    
    Args:
        study (object): object from DICOMDIR level 1 object (children of patient_record)
    
    Returns:
        children_object
        appending_keys
    """
    #study_id = study.StudyID
    study_date = study.StudyDate
    study_time = study.StudyTime
    study_des = study.StudyDescription
    
    return study.children, study_date, study_time, study_des

def parse_series(series):
    """Parse series
    
    Args:
        series (object): object from DICOMDIR level 2 object (children of study)
    Returns:
        children_object
        appending_keys
    """
    n_images = len(series.children)
    series_num = series.SeriesNumber
    series_moda = series.Modality
    series_des = series.SeriesDescription
    
    return series.children, n_images, series_num, series_moda, series_des

def parse_image(image):
    """Parse image
    
    Args:
        image (object): object from DICOMDIR level 3 object (children of series)
    Returns:
        appending_keys
    """
    relative_path = "/".join(image.ReferencedFileID)
    sop_class = image.ReferencedSOPClassUIDInFile
    syntax = image.ReferencedTransferSyntaxUIDInFile
    
    return relative_path, sop_class, syntax
    
def process_image(origin_path, target_path, rm_fileds_list):
    input_file = pydicom.dcmread(origin_path)
    for field in rm_fileds_list:
        if hasattr(input_file, field):
            delattr(input_file, field)
    input_file.save_as(target_path)
    
class Filehandler():
    """Maintain file handler to write message
    
    Args:
        filename (str): full path to save file
    """
    def __init__(self, filename):
        self.handler = open(filename, "w")
    
    def write_message(self, line):
        self.handler.writelines(line)
    
    def close(self):
        self.handler.close()

if __name__ == "__main__":
    args = argparse.ArgumentParser(description="anonymization program")
    args.add_argument("--dicomdir_path", help="full path to DICOMDIR") #"/raid/seanyu/check_hemmo/Image/0709_dicom-dir/"
    args = args.parse_args()
    print(args)
    
    dicomdir_file = read_dicomdir(os.path.join(args.dicomdir_path,"DICOMDIR"))
    file_object = Filehandler(filename=os.path.join(args.dicomdir_path, "anonymous_mapping.csv"))
    file_object.write_message("select,subject_id,dir_order,date,time,series_num,series_modality,series_description,n_images,origin_file_start,origin_file_end\n")

    for patient in dicomdir_file.patient_records:
        these_studies, this_pid, *_ = parse_patient_record(patient)
        print("Processing Subject: %s" % (this_pid))
        subj_path = os.path.join(args.dicomdir_path, "anonymous", this_pid)
        try:
            os.makedirs(subj_path)
        except:
            pass

        counter = 1
        for study in these_studies:
            these_seriess, this_sdate, this_stime, this_sdes, *_ = parse_study(study)
            for series in these_seriess:
                these_image_record, this_num_images, this_series_num, this_series_moda, this_series_des, *_ = parse_series(series)

                this_folder = "dir{}_date{}_snum{}_mod{}_des{}".format(str(counter).zfill(4),
                                                           this_sdate,
                                                           this_series_num,
                                                           this_series_moda,
                                                           this_series_des)
                # Create second-level folder
                series_path = os.path.join(subj_path, this_folder)
                try:
                    os.makedirs(series_path)
                except:
                    pass

                image_list = []
                for i,image in enumerate(these_image_record):
                    this_image_source, this_sop, this_syntax = parse_image(image)
                    # Read image, remove req fields, save to new_folder
                    t_file = os.path.join(series_path, "image"+str(i).zfill(5)+".dcm")
                    process_image(origin_path=os.path.join(args.dicomdir_path,this_image_source),
                                  target_path=t_file, 
                                  rm_fileds_list=REMOVED_FIELDS)

                    image_list.append(this_image_source)
                this_image_source_start = image_list[0]
                this_image_source_end = image_list[-1]

                this_info = "{},{},{},{},{},{},{},{},{},{},{}\n".format(str(0),this_pid, 
                                                      str(counter).zfill(4), 
                                                      this_sdate, 
                                                      this_stime, 
                                                      this_series_num, 
                                                      this_series_moda, 
                                                      this_series_des, 
                                                      this_num_images, 
                                                      this_image_source_start,
                                                      this_image_source_end)
                # Write info into files
                file_object.write_message(this_info)
                counter+=1
    file_object.close()
    print("FOLDER DONE")

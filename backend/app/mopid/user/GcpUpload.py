from fastapi import HTTPException
from sqlalchemy.orm import Session
from ...utils.functions import responseBody, dbCommit
from ...utils.classes import Logger,Timer, error_file, error_format, timing_file, timing_format
from google.cloud import storage
import os
from .model import Employees, Employers
import traceback
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="creds.json"
    

logger = Logger(__name__, error_file, error_format)
timingLogger = Logger('Timer:' + __name__, timing_file, timing_format)    
    
client = storage.Client.from_service_account_json(json_credentials_path="creds.json")
storage_client = storage.Client()

@Timer(timingLogger)
def get_size(filename):
    st = os.stat(filename)
    return st.st_size


@Timer(timingLogger)
def upload_file_in_gcp(db: Session, file, userId):
    '''
    Description - This method upload resume files in GCP in pdf format in mopid-resumes bucket and set its cache_control as no-store.
                  The file should be of pdf format and should not be exceeded 5 mb.
                  It is also update the file name and file access link in EMPLOYEES table in database.
                  
    Parameters  - db: Session, file, userId
    
    Returns     - message after successful run:- "File uploaded successfully"
    '''
    try:
        if file.file is None: 
            return responseBody(406, "Please send proper file")
        
        if len(file.file.read()) > 5000000:
            return responseBody(406, "File size too large! max file size: 5mb")
        
        if file.content_type != "application/pdf":
            return responseBody(406, "Invalid file format")
        
        # Creating bucket object  
        bucket = client.get_bucket('mopid')
        
        # Name of the object to be stored in the bucket
        object_name_in_gcs_bucket = bucket.blob(f"resumes/{userId}")   
        
        # Name of the object in local file system
        object_name_in_gcs_bucket.upload_from_file(file.file, content_type='application/pdf', rewind=True)      
        
        set_blob_cache_control('mopid', f"resumes/{userId}")
        # blob_metadata("mopid", f"resumes/{userId}")    
        
        dbDetails = db.query(Employees).filter(Employees.userId==userId).first()
        if dbDetails is None:
            dbDetails = Employees(userId=userId, resume=file.filename, resumeLink=f"https://storage.googleapis.com/mopid/resumes/{userId}")
            db.add(dbDetails)
        else:
            db.query(Employees).filter(Employees.userId==userId).update({"resume":file.filename})
    
        db.commit()
        
        logMsg = logger.return_log_msg(200,"File uploaded successfully")
        logger.logger.info(logMsg)
        return responseBody(200,"File uploaded successfully")
    except:
        traceback.print_exc()
        logMsg = logger.return_log_msg(500, "Something went wrong in uploadResume")
        logger.logger.exception(logMsg)
        raise HTTPException(status_code=500,detail="Something went wrong in uploadResume")
   


@Timer(timingLogger)
def download_file_from_gcp():
    '''
    Description - This method download files from GCP mopid-resumes bucket.
    
    Parameters  - None
    
    Returns     - Shows files from that bucket.
    '''
    try:
        buckets = list(storage_client.list_buckets())
        print(buckets)
        print(buckets[1].name)
        blobs = storage_client.list_blobs(buckets[1])
        for blob in blobs:
          print(blob)
          return responseBody(201, blob)
    except:
        traceback.print_exc()
        print("Something went wrong in GCP")



@Timer(timingLogger)
def delete_blob(bucket_name, blob_name):
    '''
    Description - This method delete files in GCP in mopid-resumes bucket.
    
    Parameters  - bucket_name, blob_name
    
    Returns     - print:- "Blob {given_blob_name} deleted."
    '''
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
    print(f"Blob {blob_name} deleted.")

@Timer(timingLogger)
def blob_metadata(bucket_name, blob_name):
    '''
    Description - This method print all metadata of given bucket and blob. So you can check all the properties associated with this bucket object.
    
    Parameters  - bucket_name, blob_name
    
    Returns     - print all metadata
    '''

    bucket = storage_client.bucket(bucket_name)

    # Retrieve a blob, and its metadata, from Google Cloud Storage.
    # Note that `get_blob` differs from `Bucket.blob`, which does not
    # make an HTTP request.
    blob = bucket.get_blob(blob_name)

    print(f"Blob: {blob.name}")
    print(f"Bucket: {blob.bucket.name}")
    print(f"ID: {blob.id}")
    print(f"Size: {blob.size} bytes")
    print(f"Updated: {blob.updated}")
    print(f"Cache-control: {blob.cache_control}")
    print(f"Content-type: {blob.content_type}")
    print(f"Content-language: {blob.content_language}")
    print(f"Metadata: {blob.metadata}")
    print(f"Medialink: {blob.media_link}")
    print(f"Custom Time: {blob.custom_time}")
    print("Temporary hold: ", "enabled" if blob.temporary_hold else "disabled")
    print(
        "Event based hold: ",
        "enabled" if blob.event_based_hold else "disabled",
    )
    if blob.retention_expiration_time:
        print(
            f"retentionExpirationTime: {blob.retention_expiration_time}"
        )

@Timer(timingLogger)
def set_blob_cache_control(bucket_name, blob_name):
    '''
    Description - This method sets cache_control as no-store for the given blob. So the access link for the obejct will always show the
                  latest upload. Firstly, Object versioning should be off in gcp bucket for successful run of this method. 
                  
    Parameters  - bucket_name, blob_name
    
    Returns     - None.
    '''
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(blob_name)
    metageneration_match_precondition = None

    # Optional: set a metageneration-match precondition to avoid potential race
    # conditions and data corruptions. The request to patch is aborted if the
    # object's metageneration does not match your precondition.
    metageneration_match_precondition = blob.metageneration

    blob.cache_control = "no-store"
    blob.patch(if_metageneration_match=metageneration_match_precondition)


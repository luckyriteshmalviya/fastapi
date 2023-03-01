from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4
import random
from fastapi import UploadFile, File 
import csv
import codecs

def dbCommit(db: Session, object):
    db.add(object)
    db.commit()
    db.refresh(object)

def responseBody(status_code : int, message : str, object = None):
    response =  {
        "status_code" : status_code,
        "message" : message
    }
    if object:
        response.update({"data" : object})
    return response


def getUniqueId():
    eventid = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
    return eventid


def generateRandomNumber():
    return random.randint(1000,9999)


def CSVToDict(data: UploadFile = File(...)):
    iterator = csv.reader(codecs.iterdecode(data.file, 'utf-8'), delimiter=',')
    result = []
    columns = next(iterator)
    col = len(columns)
    for row in iterator:
        data_object = {}
        for i in range(col):
            data_object[columns[i]] = row[i]
        result.append(data_object)
    return result
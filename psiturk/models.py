
import datetime
import io, csv, json
import traceback
import sys
import string
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text

from db import Base
from psiturk_config import PsiturkConfig

config = PsiturkConfig()
config.load_config()

TABLENAME = config.get('Database Parameters', 'table_name')
CODE_VERSION = config.get('Task Parameters', 'experiment_code_version')

class Participant(Base):
    """
    Object representation of a participant in the database.
    """
    __tablename__ = TABLENAME
   
    uniqueid =Column(String(128), primary_key=True)
    assignmentid =Column(String(128), nullable=False)
    workerid = Column(String(128), nullable=False)
    hitid = Column(String(128), nullable=False)
    ipaddress = Column(String(128))
    browser = Column(String(128))
    platform = Column(String(128))
    language = Column(String(128))
    cond = Column(Integer)
    counterbalance = Column(Integer)
    codeversion = Column(String(128))
    beginhit = Column(DateTime)
    beginexp = Column(DateTime)
    endhit = Column(DateTime)
    bonus = Column(Float, default = 0)
    status = Column(Integer, default = 1)
    if 'postgres://' in config.get('Database Parameters', 'database_url').lower():
        datastring = Column(Text)
    else:
        datastring = Column(Text(4294967295))
    
    def __init__(self, **kwargs):
        self.uniqueid = "{workerid}:{assignmentid}".format(**kwargs)
        for key in kwargs:
            setattr(self, key, kwargs[key])
        self.status = 1
        self.codeversion = CODE_VERSION
        self.beginhit = datetime.datetime.now()
    
    def __repr__(self):
        return "Subject(%s, %s, %s, %s)" % ( 
            self.uniqueid, 
            self.cond, 
            self.status,
            self.codeversion)
    
    def get_trial_data(self):
        try:
            trialdata = json.loads(self.datastring)
            trialdata = trialdata['data']
        except TypeError, ValueError:
            # There was no data to return.
            print("No trial data found in record:", self)
            return("")

        try:
            ret = []
            with io.BytesIO() as outstring:
                csvwriter = csv.writer(outstring)
                for trial in trialdata:
                    csvwriter.writerow((
                        self.uniqueid,
                        trial["current_trial"],
                        trial["dateTime"],
                        json.dumps(trial["trialdata"])))
                ret = outstring.getvalue()
            return ret
        except:
            print("Error reading record in get_trial_data:", self)
            return("")

    def get_structured_trial_data(self):
        try:
         
            structured_data = json.loads(self.datastring)#["data"]
            structured_data = structured_data["structured_data"]
        except TypeError, ValueError:
            # There was no data to return.
            print("No structured trial data found in record:", self)
            return("")

        try:

            ret = ""
            with io.BytesIO() as outstring:
                csvwriter = csv.writer(outstring)
                schema = [attr.strip() for attr in \
                string.split(config.get('Custom Trialdata Structure', 'attributes'),
                             ',')]
                for trial in structured_data:
                    trialdata = trial["customdata"]
                    trialdata_list = []

                    for key in trialdata:
                        try:
                            trialdata_list.append(trialdata[key])
                        except KeyError as e:
                            print("KeyError in structured data in record:", self)
                            print(e.__doc__)
                            print(e.message)
                            return("")
                    csvwriter.writerow([
                            self.uniqueid,
                            trial["current_trial"],
                            trial["dateTime"]
                        ] + trialdata_list)
                ret = outstring.getvalue()
            return ret
        except:
            #print("Error reading record:", self)
            print(traceback.format_exc())
            return("")
    
    def get_event_data(self):
        try:
            eventdata = json.loads(self.datastring)["eventdata"]
        except TypeError, ValueError:
            # There was no data to return.
            print("No event data found in record:", self)
            return("")
        
        try:
            ret = []
            with io.BytesIO() as outstring:
                csvwriter = csv.writer(outstring)
                for event in eventdata:
                    csvwriter.writerow((self.uniqueid, event["eventtype"], event["interval"], event["value"], event["timestamp"]))
                ret = outstring.getvalue()
            return ret
        except:
            print("Error reading record from get_event_data:", self)
            return("")
    
    def get_question_data(self):
        try:
            questiondata = json.loads(self.datastring)["questiondata"]
        except TypeError, ValueError:
            # There was no data to return.
            print("No question data found in record:", self)
            return("")
        
        try:
            ret = []
            with io.BytesIO() as outstring:
                csvwriter = csv.writer(outstring)
                for question in questiondata:
                    csvwriter.writerow((self.uniqueid, question, questiondata[question]))
                ret = outstring.getvalue()
            return ret
        except:
            print("Error reading record from get_question_data:", self)
            return("")
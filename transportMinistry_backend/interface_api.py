# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 16:09:28 2018

@author: BrunoAdmin

Notes:
    Webservice run on port 3000

"""
from flask import Flask, Response, request, send_file, jsonify, send_from_directory
import threading
import Lib.databaseInteraction as db
import Lib.algorithms as alg
import Lib.transportPlanning as plan
import os
import pandas as pd
app = Flask(__name__)
    
## Actual implementation
global url_prex
url_prex = '/api'
    
@app.route("{}/".format(url_prex), methods=['GET'])
def index(): 
    """
    Landing page
    """
    
    def html_process(tag, contents):
        # mini helper method to generate tag
        s = ""
        for c in contents:
            s += "<{}>{}</{}>".format(tag,c,tag)
        return s
    
    header = ["Welcome to Hope Church Life Group Transportation management web service documentation page"]
    header = html_process("h1",header)
    
    dc = ["I mean, you are actually not supposed to see this... But if you do, ya, here are some \
          of the RESTful api that you can call directly via url. JSON files or otherwise strings\
           will be returned. I hope you are developer, otherwise please use the proper interface to \
           interact with the system. IF YOU SIMPLY CALL THESE METHODS, YOU WILL PROBABLY SCREW \
           UP THE SYSTEM!!!! nuh i m just kidding..."]
    dc = html_process("p",dc)
    methods = ["[get ] /: webservice landing page, instructions of all available methods", ##
               "[get ] /readme: all the detailed requirements",
               "--- DB interaction ---",
               "[post] /editPerson: {'lg':value, 'name':value, 'postcode':value}", ##
               "[post] /deletePerson: {'lg':value, 'name':value}", ##
               "[post] /registerPerson: {'lg':value, 'name':value, 'postcode':value}", ##
               "[post] /addLG: {'lg':value, 'auth':value}", ##
               "[post] /deleteLG: {'lg':value, 'auth':value}",##
               "[get ] /nuclearbomb: reset everything",##
               "--- Event planning ---",
               "[post] /submit: ",
               "[post] /bestmatches: ",
               "--- Display info ---",
               "[get ] /whoisgoing/?event_id=<value> : show all the names who is going",
               "[get ] /showmembers/?auth=<value>&lg=<value> : who is in the lifegroup",
               "[get ] /"]
    methods = html_process("li",methods)
    
    
    h2 = ["The txt file has to be in this format in order to work"]
    h2 = html_process("h2",h2)
    
    txt_format = ["1st row: ['title1','title2',...]",
                  "2nd row: ['job1','job2',...]",
                  "Example is below (upload.txt):",
                  "--------------I am upload.txt------------------",
                  "['junior', 'graduate', 'parttime']",
                  "['marketing', 'accountant', 'banker']",
                  "--------------I am upload.txt------------------"]
    txt_format = html_process("p",txt_format)
    
    body = "<html><body>\
            {}{}\
            <ul>{}</ul>\
            </body></html>".format(header, dc, methods)
    
    return body    

## Reademe
@app.route("{}/readme".format(url_prex), methods=['GET'])
def read_me():
    return app.send_static_file('readme.html')

## DB direct modify
@app.route("{}/addLG".format(url_prex), methods=['POST'])
def add_LG(): ##
    """
    Register life group
    
    Requires:
        - lifegroup name
        
    Returns:
        - success / fail
    """
    try:
        ## receive file
        content = request.get_json()
        lg = content.get('lg')
        
        ## exec
        msg = db.LifeGroup(lg=lg)
        msg = msg.add_lg()
        
        return msg
    
    except Exception as e:
        return e
        #return "Some internal error existed"


@app.route("{}/deleteLG".format(url_prex), methods=['POST'])
def delete_LG(): ##
    """
    Delete life group
    
    Requires:
        - lifegroup name
        
    Returns:
        - success / fail
    """
    try:
        ## receive file
        content = request.get_json()
        lg = content.get('lg')
        msg = db.LifeGroup(lg).del_lg()
        return msg
    
    except Exception as e:
        return "Some internal error existed"
    
@app.route("{}/registerPerson".format(url_prex), methods=['POST'])
def add_person(): ##
    """
    Register person
    
    Requires:
        - person name
        - life group
        - postcode
        
    Returns:
        - success / fail
    """
    try:
        ## receive file
        content = request.get_json()
        lg = content.get('lg')
        name = content.get('name')
        postcode = content.get('postcode')
        
        msg = db.Person(lg = lg, name = name, postcode = postcode).add_db()
        return msg
        #return "Added successfully"
    
    except Exception as e:
        return "Some internal error existed"

@app.route("{}/editPerson".format(url_prex), methods=['POST'])
def edit_person():
    """
    Register life group
    
    Requires:
        - person name
        - life group
        - postcode
        
    Returns:
        - success / fail
    """
    try:
        ## receive file
        content = request.get_json()
        lg = content.get('lg')
        name = content.get('name')
        postcode = content.get('postcode')
        
        msg = db.Person(lg = lg, name = name, postcode = postcode).edit_db()
        return msg
        #return "Edited successfully"
    
    except Exception as e:
        return "Some internal error existed"
    

@app.route("{}/deletePerson".format(url_prex), methods=['POST'])
def delete_person():
    """
    Register life group
    
    Requires:
        - person name
        - life group
        
    Returns:
        - success / fail
    """
    try:
        ## receive file
        content = request.get_json()
        lg = content.get('lg')
        name = content.get('name')
        
        msg = db.Person(lg = lg, name = name).del_db()
        return msg
        #return "Deleted successfully"
    
    except Exception as e:
        return "Some internal error existed"

@app.route("{}/nuclearbomb".format(url_prex), methods=['GET'])
def reset(): ##
    """
    Reset db
    """
    msg = db.red_reset_button()
    return msg


## -------------------------------------------------------------
## ---------------- Event -------------------------------------
@app.route("{}/submit".format(url_prex), methods=['POST'])
def api_submit(): ##
    """
    Submit the person info that are going to one particular event.
    """
    try:
        ## receive file
        content = request.get_json()
        event = content.get('event_id')
        #event = CodeConverter.external2internal(event)
        lg = content.get('lg')
        name = content.get('name')
        driver_flag = content.get('isDriver')
        pc_vary = content.get('postcode_vary') # this can be asked in the front-end; if special postcode request is required
        
        ## fetching the method
        msg = plan.submit(event, lg, name, driver_flag, pc_vary)
        if type(msg) == tuple:
            return msg[0]
            
        else:
            return msg
    
    except Exception as e:
        return "Some internal error existed {}".format(e)

@app.route("{}/createEvent".format(url_prex), methods=['POST'])
def api_createEvent(): ##
    """
    Submit the person info that are going to one particular event.
    """
    try:
        ## receive file
        content = request.get_json()
        lg = content.get('lg')
        pc_from = content.get('postcode_from')
        pc_to = content.get('postcode_to')
        note = content.get('note')
        
        ## Event        
        e = plan.Event(lg= lg, note=note)
        e_id = e.create_event()
        return e_id
    
    except Exception as e:
        return "Some internal error existed {}".format(e)
    
@app.route("{}/bestmatches".format(url_prex), methods=['POST'])
def api_bestmatches(): ##
    """
    Submit the person info that are going to one particular event.
    """
    try:
        ## receive file
        content = request.get_json()
        event_id = content.get('event_id')
        
        ## Get drivers / passengers
        event_file = "Events_temp/{}.csv".format(event_id)
        file = pd.read_csv(event_file)
        
        condition_isDriver = file['driver'] != 0 #as for driver column, non-0 is capacity
        condition_isPassenger = file['driver'] == 0
        drivers = file[condition_isDriver]
        passengers = file[condition_isPassenger]
        
        map_drivers = {}
        map_passengers = {}
        
        for i, row in drivers.iterrows():
            ## Append drive into the dictionary
            name = row['name']
            info_pair = (row['postcode'], row['driver'])
            map_drivers.update({name: info_pair})
            
        for i, row in passengers.iterrows():
            ## Append passenger into the dictionary
            name = row['name']
            postcode = row['postcode']
            map_passengers.update({name: postcode})        
        
        ## trigger calculation
        mapping = alg.find_combinations(map_drivers, map_passengers)
        return jsonify(mapping)
    
    except Exception as e:
        return "Error: Please check again the input of Event ID or Lifegroup{}".format(e)


## ----------------End Event----------------------------------------
## -------------------------------------------------------------

## -------------------------------------------------------------
## ----------------Display Info------------------------------------

# Sending parameters via url
# Example: url/api/whoisgoing?eventID=<value>

@app.route("{}/whoisgoing".format(url_prex), methods=['GET'])
def show_pplgoing():
    
    try:
        # Parameters
        event_id = request.args.get('eventID', type = str)
        event_id = CodeConverter().external2internal(event_id)
        
        # Call function: read eventID file first
        file = pd.read_csv('Events_temp/{}.csv'.format(event_id))
        
        # retrieve all passengers (df) to list
        condition = file['driver'] == 0
        ls_array = file['name'].loc[condition].values.tolist()
        
        # retrieve all drivers, attach tag, to list
        condition = file['driver'] >= 1
        ls_drivers = file['name'].loc[condition].values.tolist()
        ls_drivers = ["{} (driving)".format(i) for i in ls_drivers]
        ls_drivers.extend(ls_array)
        
        return jsonify({"names":ls_drivers})
    except Exception as e:
        return "Event ID does not exist {}".format(e)


@app.route("{}/showmembers".format(url_prex), methods=['GET'])
def show_members():
    """
    This method shows all the members of a lifegroup.
    """
    # Parameters
    lg = request.args.get('lg', type = str)
    passcode = request.args.get('passcode', type = str)

    # call function
    members = db.show_person(lg=lg)
    
    if passcode != "1234":
        ls = []
        for name in members:
            ls.append(name[1])
            
        return jsonify({"members":ls})
    
    else:
        return jsonify({"members":members})


## ----------------End Display---------------------------------
## -------------------------------------------------------------





## -------------------------------------------------------------
## -------------------------------------------------------------

class CodeConverter(object):
    def __init__(self):
        pass
    
    def external2internal(self, eventID):
        # uq6-2018-05-01-20-13-26 to
        # [uq6]2018-05-01#20-13-26#
        ls_event = eventID.split('-')
        
        lg = ls_event[0]
        yy = ls_event[1]
        mm = ls_event[2]
        dd = ls_event[3]
        h = ls_event[4]
        m = ls_event[5]
        s = ls_event[6]
        
        encode = "[{}]{}-{}-{}#{}-{}-{}#".format(lg,yy,mm,dd,h,m,s)
        return encode
    
    def internal2external(self, eventID):
        # [uq6]2018-05-01#20-13-26# to
        # uq6-2018-05-01-20-13-26
        lg = eventID.split(']')[0][1:]
        yymmdd = eventID.split(']')[1].split('#')[0]
        hms = eventID.split('#')[1]
        encode = "{}-{}-{}".format(lg, yymmdd, hms)
        return encode
                            


### Scheduler
"""
Reference:
https://stackoverflow.com/questions/21214270/scheduling-a-function-to-run-every-hour-on-flask?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa

"""
if __name__ == "__main__":
    ## cd to absolute dir (depends on server)
    #os.chdir("/home/bruno1993/transport_api/")
    app.run(host="0.0.0.0", port=3000)
    
    
    
    
    
    
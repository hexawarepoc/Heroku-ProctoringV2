from datetime import datetime,date  
from PIL import Image
import numpy
import face_recognition
from collections import defaultdict
from pymongo import MongoClient
import base64
from base64 import b64decode
import datetime
from datetime import date
from flask import Flask, render_template, Response,request,render_template,session,send_file
from datetime import datetime,timedelta
import json
import dns.resolver
from datetime import timedelta
import pymongo
from bson.objectid import ObjectId
import io
import bcrypt
from flask import Flask
from flask_talisman import Talisman
import mimetypes
import pandas as pd
from flask_wtf.csrf import CSRFProtect
from wsgiref.simple_server import ServerHandler
from typing import Any, Dict
import traceback
import os
ServerHandler.server_software = "Fake Server Name Here"
OVERRIDE_HTTP_HEADERS: Dict[str, Any] = {"Server":None}
mimetypes.add_type('application/javascript', '.js')


mongo_uri="mongodb+srv://hexaware:cssJavascript@josh.xotyr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
cluster = MongoClient(mongo_uri)  
db=cluster["Proctoring_Josh"]     
#db=cluster["Test_Josh"]                  

app = Flask(__name__)
app.config["SECRET_KEY"]="secret"
csp = {
    'default-src': '\'self\'',
    'script-src': '\'self\'',
    'script-src-attr':  '\'unsafe-inline\'',
    'script-src-elem':  '\'self\'',
    'img-src': ["'self'", 'https: data:']
}
Talisman(app,content_security_policy=csp,strict_transport_security_preload=True)
csrf = CSRFProtect(app)

@app.after_request
def apply_caching(response):
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response

@app.after_request
def remove_header(response):
     del response.headers['X-Some-Custom-Header']
     return response

def insert_document(func_name,error):
    generated_at="local"                                                                                               # change generated_at when deploying to "WEB-APP"
    data = {"function_name":func_name,"error_msg":error,"error_timing":datetime.now(),"generated_at":generated_at}
    db.app_logs.insert_one(data)
    return data       

@app.route("/",methods=["GET"])
@app.route("/login.html",methods=["GET"])
def login():  
    try:
       session.pop('logged_in_user_role', None)
       return render_template("login.html")
    except Exception as ex:
        print(ex)
        insert_document("login",str(ex))                                                                                                                                                      
                                                 
@app.route("/logincheck" ,methods=["POST"])
def logincheck():
    try:
        global user_id,input_password
        user_id=request.form["username"]
        form_password=request.form["password"]
        form_password=base64.b64decode(form_password)
        form_password=form_password.decode('UTF-8')
        input_password=form_password.encode("utf-8")     
        user_details=db.master.find_one({"user_id":str(user_id)},{"facial_img":0})
        def user(user_id):
            global user_data,user_role,agent_ids,user_project
            user_data=list(db["master"].find({"user_id":user_id},{"role":1,"user_name":1}))
            user_role=user_data[0]["role"]
            session["user_name"]=user_data[0]["user_name"]
            if user_data[0]["role"]=="supervisor":
                user_data=list(db["master"].find({"user_id":str(user_id),"role":"supervisor"},{"project_name":1,"role":1,"project_id":1}))
                user_project_id=user_data[0]["project_id"]
                user_project=user_data[0]["project_name"]
                x=list(db.master.find({"project_name":user_project,"role":"agent","reports_to":session["user_id"]},{"user_id":1,"_id":0}))
                agent_ids=[]
                for i in range(0,len(x)):
                    agent_ids.append(x[i]["user_id"])
                user_data[0]["agent_names"]=agent_ids
                session["agent_ids"]=agent_ids
                session["user_project"]=user_project
                session["user_project_id"]=user_project_id
            return user_data[0]
        if user_details:
            session["user_id"]=user_id
            user(user_id)
            stored_password=user_details["password"]
            if bcrypt.checkpw(input_password,stored_password):
                session.permanent = True
                user_id=user_details["user_id"]
                global role
                role = user_details["role"]
                session['logged_in_user_role'] = role           
                session['logged_in_user_id'] = user_id                                                      
                if db.master.find_one({"user_id":user_id,"role":"supervisor"}):
                    data={"Status":"Success"}
                    return json.dumps(data)
                elif db.master.find_one({"user_id":user_id,"role":"super_admin"}):
                    data={"Status":"Success"}
                    return json.dumps(data)   
                else:
                    data={"Status":"Error","Msg":"Agents dont have access to this"}
                    return json.dumps(data)
            else:
                data={"Status":"Error","Msg":"Invalid username or password"}
                return json.dumps(data)
        else:
            data={"Status":"Error","Msg":"Invalid username or password"}
            return json.dumps(data) 
    except Exception as ex:
        print(ex) 
        insert_document("logincheck",str(ex))    


#get the list of projects with supervisors and agents
@app.route("/index.html",methods = ['POST', 'GET'])
def project_list():
    try:
        return render_template("index.html", data=[])                                                       
    except Exception as ex:
        print(ex)
        insert_document("project_list",str(ex))                



@app.route("/ProjectListData/<PageNo>",methods = ['GET'])
def ProjectListData(PageNo):
    try:
        if not session.get("logged_in_user_role"):
            return render_template("login.html",data="Session expired.Please login again.")
        project_id_list = list(db["master"].distinct("project_id"))
        project_list=[]
        for i in project_id_list:
            project_list.append(list(db["master"].find({"project_id":i},{"_id":0,"project_id":1,"user_id":1,"project_name":1,"role":1,"initials":1})))
        def projects(project):
            data={}
            agent_list=[]
            supervisor_list = []
            agentid_list=["1","2","3","4"]
            supervisor=[]
            for i in project:
                if i["role"]=="supervisor":
                    data["supervisor"]=i["user_id"]
                    supervisor_list.append(str(i["initials"]))
                    supervisor.append(i["user_id"])
                if i["role"]=="agent":
                    agent_list.append(str(i["initials"]))
                data["project_id"]=i["project_id"]
                data["project_name"]=i["project_name"]
                data["agent"] = agent_list
                data["supervisorlist"] = supervisor_list
                data["agentid"] = agentid_list
                data["number_of_agents"]=len(data["agent"])
                data["supervisor"]=supervisor
            return data
        
        final_data=[]
        for i in project_list:
            final_data.append(projects(i))
        if session['logged_in_user_role']=="supervisor":
            final_data=list(filter(lambda x:session["user_id"] in x["supervisor"], final_data))
        else:
            final_data=final_data                                                        
        return json.dumps(final_data, indent=2)                                                       
    except Exception as ex:
        print(ex)
        insert_document("project_list",str(ex))        
                
def login_user(role,user_id):
    try:
        project_id_list = list(db["master"].distinct("project_id"))
        project_list=[]
        for i in project_id_list:
            project_list.append(list(db["master"].find({"project_id":i},{"_id":0,"project_id":1,"user_id":1,"project_name":1,"role":1,"initials":1})))
        def projects(project):
            data={"current_user_role":role,"current_user_name":user_id}
            agent_list=[]
            supervisor_list = []
            agentid_list=["1","2","3","4"]
            for i in project:
                if i["role"]=="supervisor":
                    data["supervisor"]=i["user_id"]
                    supervisor_list.append(i["initials"])
                if i["role"]=="agent":
                    agent_list.append(i["initials"])
                data["project_id"]=i["project_id"]
                data["project_name"]=i["project_name"]
                data["agent"] = agent_list
                data["supervisorlist"] = supervisor_list
                data["agentid"] = agentid_list
                data["number_of_agents"]=len(data["agent"])
            return data
        final_data=[]
        for i in project_list:
            final_data.append(projects(i))   
        if session['logged_in_user_role']=="supervisor":
            final_data=list(filter(lambda final_data: final_data["supervisor"] ==session["user_id"], final_data))
        return render_template("index.html", data=final_data)
    except Exception as ex:
        print(ex)
        insert_document("login_user",str(ex))  

                                 
#get the list of onboarded agents
@app.route("/OnboardedAgent.html",methods = ['GET'])
def onboarded_agents():
    try:               
        return render_template("OnboardedAgent.html", ondata=[])                                                                                         
    except Exception as ex:
        print(ex)
        insert_document("onboarded_agents---",str(ex))       



@app.route("/OnboardedAgent/<PageNo>",methods = ['GET'])
def OnboardedAgent(PageNo):
    try:
        if not session.get("logged_in_user_role"):
            return render_template("login.html",data="Session expired.Please login again.")
        limit=10
        if(PageNo == "1"):
            offset=((int(PageNo)) * limit) - limit
        else:
            offset=((int(PageNo)) * limit) - limit
            offset=offset -1
        if session['logged_in_user_role']=="supervisor":
            all_details = list(db.master.find({"role":"agent","reports_to":session["logged_in_user_id"]},{"_id": 0, "user_id": 1, "user_name": 1, "onboarding_date": 1,"expiration_date": 1, "facial_img": 1, 
                                                "status": 1}).skip(offset).limit(limit))
            len_all_details = db.master.count_documents({"role":"agent","reports_to":session["logged_in_user_id"]})
        else:
            all_details = list(db.master.find({"role":"agent"},{"_id": 0, "user_id": 1, "user_name": 1, "onboarding_date": 1,"expiration_date": 1, "facial_img": 1, 
                                                "status": 1}).skip(offset).limit(limit))  
            len_all_details = db.master.count_documents({"role":"agent"})
        for i in all_details:
            for key in i.keys():
                if key == "onboarding_date":
                    i[key]=str(i[key].date())
                if key == "expiration_date":
                    i[key] = str(i[key].date())
                try:
                    if key == "facial_img":
                        i["facial_img"] = (base64.b64encode(i[key])).decode('utf-8')
                except Exception as ex:
                    print(ex)
        if(all_details):
            total={"total_rows":len_all_details,"data":all_details} 
            return json.dumps(total)
        else:
            return json.dumps([])
    except Exception as ex:
        print(ex)
        insert_document("OnboardedAgent",str(ex))  
                                                                   
#get the list of onboarded agents based on status
@app.route('/FilterOnboardedAgent',methods=["POST"])
def FilterOnboardedAgent():
    try:
        status= request.form["fstatus"]
        name= request.form["fname"]
        pageNo= request.form["pageNo"]
        limit=10
        if(pageNo == "1"):
            offset=((int(pageNo)) * limit) - limit
        else:
            offset=((int(pageNo)) * limit) - limit
            offset=offset -1 
        if session['logged_in_user_role']=="supervisor":
            if  status != "" and name != "": 
                query_result=list(db["master"].find({"status":status,"role":"agent","reports_to":session['logged_in_user_id'],"user_name":{"$regex":name,"$options":"i"}},{"_id": 0, "user_id": 1, "user_name": 1,
                "onboarding_date": 1, "expiration_date": 1, 
                "facial_img": 1, "status": 1}).sort("onboarding_date",pymongo.DESCENDING).skip(offset).limit(limit))    
                num_rows=db["master"].count_documents({"status":status,"role":"agent","reports_to":session['logged_in_user_id'],"user_name":{"$regex":name,"$options":"i"}})
            elif name != "" and  status== "":
                query_result=list(db["master"].find({"user_name":{"$regex":name,"$options":"i"},"reports_to":session['logged_in_user_id'],"role":"agent"},{"_id": 0, "user_id": 1, "user_name": 1,
                "onboarding_date": 1, "expiration_date": 1, 
                "facial_img": 1, "status": 1}).sort("onboarding_date",pymongo.DESCENDING).skip(offset).limit(limit))    
                num_rows=db["master"].count_documents({"status":status,"role":"agent","reports_to":session['logged_in_user_id'],"user_name":{"$regex":name,"$options":"i"}})

            elif status != "" and name =="":
                query_result=list(db["master"].find({"status":status,"reports_to":session['logged_in_user_id'],"role":"agent"},{"_id": 0, "user_id": 1, "user_name": 1,
                "onboarding_date": 1, "expiration_date": 1, 
                "facial_img": 1, "status": 1}).sort("onboarding_date",pymongo.DESCENDING).skip(offset).limit(limit))    
                num_rows=db["master"].count_documents({"status":status,"role":"agent","reports_to":session['logged_in_user_id'],"user_name":{"$regex":name,"$options":"i"}})
        
            else:
                query_result=list(db["master"].find({"role":"agent","reports_to":session['logged_in_user_id']},{"_id": 0, "user_id": 1, "user_name": 1,
                "onboarding_date": 1, "expiration_date": 1, 
                "facial_img": 1, "status": 1}).sort("onboarding_date",pymongo.DESCENDING).skip(offset).limit(limit))    
                num_rows=db["master"].count_documents({"status":status,"role":"agent","reports_to":session['logged_in_user_id'],"user_name":{"$regex":name,"$options":"i"}})
        else:

            if  status != "" and name != "": 
                query_result=list(db["master"].find({"status":status,"role":"agent","user_name":{"$regex":name, '$options' : 'i'}},{"_id": 0, "user_id": 1, "user_name": 1,
                "onboarding_date": 1, "expiration_date": 1, 
                "facial_img": 1, "status": 1}).sort("onboarding_date",pymongo.DESCENDING).skip(offset).limit(limit))    
                num_rows=db["master"].count_documents({"status":status,"role":"agent","user_name":{"$regex":name, '$options' : 'i'}})

            elif name != "" and  status== "":
                query_result=list(db["master"].find({"user_name":{"$regex":name, '$options' : 'i'},"role":"agent"},{"_id": 0, "user_id": 1, "user_name": 1,
                "onboarding_date": 1, "expiration_date": 1, 
                "facial_img": 1, "status": 1}).sort("onboarding_date",pymongo.DESCENDING).skip(offset).limit(limit))    
                num_rows=db["master"].count_documents({"status":status,"role":"agent","user_name":{"$regex":name, '$options' : 'i'}})

            elif status != "" and name =="":
                query_result=list(db["master"].find({"status":status,"role":"agent"},{"_id": 0, "user_id": 1, "user_name": 1,
                "onboarding_date": 1, "expiration_date": 1, 
                "facial_img": 1, "status": 1}).sort("onboarding_date",pymongo.DESCENDING).skip(offset).limit(limit))    
                num_rows=db["master"].count_documents({"status":status,"role":"agent","user_name":{"$regex":name, '$options' : 'i'}})
            else:
                query_result=list(db["master"].find({"role":"agent"},{"_id": 0, "user_id": 1, "user_name": 1,
                "onboarding_date": 1, "expiration_date": 1, 
                "facial_img": 1, "status": 1}).sort("onboarding_date",pymongo.DESCENDING).skip(offset).limit(limit))    
                num_rows=db["master"].count_documents({"status":status,"role":"agent","user_name":{"$regex":name, '$options' : 'i'}})

        for i in query_result:
            for key in i.keys():
                if key == "onboarding_date":
                    i[key]=str(i[key].date())
                if key == "expiration_date":
                    i[key]=str(i[key].date())
                if key == "facial_img":
                    i["facial_img"] = (base64.b64encode(i[key])).decode('utf-8')
        if(num_rows and query_result):
            total={"total_rows":num_rows,"data":query_result} 
            return json.dumps(total,indent=2)
        else:
            return json.dumps([],indent=2)
    except Exception as ex:
        print(ex)
        insert_document("FilterOnboardedAgent",str(ex))    
       
#filter agentwise results based on project name and date
@app.route("/AgentList.html")
def agentdetails_home():
    try:
        return render_template("AgentList.html", data=[])
    except Exception as ex:
        print(ex)
        insert_document("agentdetails_home",str(ex))  


#filter agentwise results based on project name and date
@app.route("/AgentListData/<PageNo>",methods=["GET"])
def AgentListData(PageNo):
    limit=3
    offset=0
    if(PageNo == "1"):
        pass
    else:
        limit=3*int(PageNo)
        offset=limit-3
    if not session.get("logged_in_user_role"):
        return render_template("login.html",data="Session expired.Please login again.")
    if session['logged_in_user_role']=="supervisor":
        data=list(db.dailySession.aggregate(
                [{"$match": {
                        "project_id":session["user_project_id"],
                        "reports_to":session["logged_in_user_id"]
                            } },
                {"$group": {"_id": {"name":"$user_id","project": "$project_name"},
                        "total_hours": {"$sum": "$total_hours"},"billable_hours":{"$sum":"$billable_hours"},
                        "non_billable_hours":{"$sum":"$non_billable hours"},
                        "COUNT": {"$sum": 1}}},
                        {"$sort":{"_id" :-1}}]))
        try: 
            flag_data=list(db.master.aggregate(
                [{"$match":{ "role":"agent"}},
                {"$group": {"_id": {"name":"$user_id","flags": "$flags"}}}]))
            for i in data:
                i["flags"]=0
                for j in flag_data:
                    if i["_id"]["name"]==j["_id"]["name"]:
                        i["flags"]=j["_id"]["flags"]
        except Exception as ex:
            print(ex)
            insert_document("AgentListData-flag data  ---- ",str(ex))
        data=data[offset:limit]  
    else:
        data=list(db.dailySession.aggregate(
            [{"$match": {
                            "project_id":session["user_project_id"]}},{                                                                                                                                                                                   
                "$group": {
                        "_id": {"name":"$user_id","project": "$project_name"},
                        "total_hours": {"$sum": "$total_hours"},
                        "billable_hours":{"$sum":"$billable_hours"},
                        "non_billable_hours":{"$sum":"$non_billable hours"},
                        "COUNT": {"$sum": 1 }}},
                        {"$sort":{"_id" :-1}}]))
        try:
            flag_data=list(db.master.aggregate(
                [{"$match":{ "role":"agent"}},
                {"$group": {"_id": {"name":"$user_id","flags": "$flags"}}}]))
            for i in data:
                i["flags"]=0
                for j in flag_data:
                    if i["_id"]["name"]==j["_id"]["name"]:
                        i["flags"]=j["_id"]["flags"] 
        except Exception as ex:
            print(ex)
            insert_document("AgentListData----flag data----",str(ex))
        data=data[offset:limit]
    try:
        for i in data:
            i["_id"]["user_name"]=list(db.master.find({"role":"agent","user_id":i["_id"]["name"]},{"user_name":1,"_id":0}))[0]["user_name"]
            i["_id"]["chart_name"]=i["_id"]["name"].replace(" ","") 
    except Exception as ex:
        print(ex)
        insert_document("AgentListData------",str(ex))
        data=[]
    return json.dumps(data)


@app.route("/GetName")
def GetName():
    try:
        if session['logged_in_user_role']=="supervisor":
            data=list(db.dailySession.aggregate(
                    [{                          
                "$match": {
                    "project_id":session["user_project_id"],
                    "reports_to": session["logged_in_user_id"]}},
                    {"$group":{"_id": {"name":"$user_id","project": "$project_name"},"total_hours": {"$sum": "$total_hours"},
                    "billable_hours":{"$sum":"$billable_hours"},"breaks":{"$sum":"$breaks"},                                                                                                                                                                  
                            "non_billable_hours":{"$sum":"$non_billable hours"},"COUNT": {"$sum": 1}}}])),
        else:
            data=list(db.dailySession.aggregate(
                    [{"$group": {"_id": {"name":"$user_id","project": "$user_project"}, "total_hours": {
                    "$sum": "$total_hours"},"billable_hours":{
                    "$sum":"$billable_hours"},
                    "breaks":{"$sum":"$breaks"},
                    "non_billable_hours":{"$sum":"$non_billable hours"},"COUNT": {"$sum": 1}}}]))
        try:
            for j in data:
                for i in j:
                    i["_id"]["user_name"]=list(db.master.find({"role":"agent","user_id":i["_id"]["name"]},{"user_name":1,"_id":0}))[0]["user_name"]
                    i["_id"]["chart_name"]=i["_id"]["name"].replace(" ","")
        except Exception as ex:
            print(ex)
            insert_document("GetName-for loop---",str(ex)) 
        return json.dumps(data[0])
    except Exception as ex:
        print(ex)
        insert_document("GetName----",str(ex))  



@app.route("/GetNameBYProject$project=<string:project>")
def GetNameBYProject(project):
    try:
        data=list(db.dailySession.aggregate(
                [{
                "$match": {
                        "project_name":project}}, {
                "$group": {
                        "_id": {"name":"$user_id","project": "$project_name"},
                        "total_hours": {
                        "$sum": "$total_hours"},
                        "billable_hours":{"$sum":"$billable_hours"},
                        "non_billable_hours":{"$sum":"$non_billable_hours"},
                        "COUNT": {"$sum": 1}}
                }]
        )),
        try:
            for j in data:
                for i in j:
                    i["_id"]["user_name"]=list(db.master.find({"role":"agent","user_id":i["_id"]["name"]},{"user_name":1,"_id":0}))[0]["user_name"]
                    i["_id"]["chart_name"]=i["_id"]["name"].replace(" ","")
        except Exception as ex:
            print(ex)
            insert_document("GetNameBYProject--- For loop",str(ex)) 
        return json.dumps(data[0],indent=2)
    except Exception as ex:
        print(ex)
        insert_document("GetNameBYProject---",str(ex)) 
   


#agentdetails/P001/
@app.route("/ProjectAgentList.html$project=<string:project>",methods=["GET"])
def projectagentdetails(project):
    try:
        if not project:
            project=session["user_project"]
        if session['logged_in_user_role']=="supervisor":
            data=list(db.dailySession.aggregate(
                    [{"$match": {"project_name":project},
                    "reports_to": session["logged_in_user_id"]},
                    {"$group": {"_id": {"name":"$user_id","project": "$project_name"},
                            "total_hours": {"$sum": "$total_hours"},"billable_hours":{"$sum":"$billable_hours"},
                            "non_billable_hours":{"$sum":"$non_billable hours"},
                            "COUNT": {"$sum": 1}}}]))
            try:
                flag_data=list(db.master.aggregate(
                    [{"$match":{ "role":"agent"}},
                    {"$group": {"_id": {"name":"$user_id","flags": "$flags"}}}]))
                for i in data:
                    i["flags"]=0
                    for j in flag_data:
                        if i["_id"]["name"]==j["_id"]["name"]:
                            i["flags"]=j["_id"]["flags"]  
            except Exception as ex:
                print(ex)
                insert_document("projectagentdetails-flagdata-----",str(ex)) 
        else:
            data=list(db.dailySession.aggregate(                                                                                                           
                [{"$match": {
                "project_name":project}},                                                                                                                                                                                                                               
                {"$group": {
                            "_id": {"name":"$user_id","project": "$project_name"},
                            "total_hours": {"$sum": "$total_hours"},
                            "billable_hours":{"$sum":"$billable_hours"},
                            "non_billable_hours":{"$sum":"$non_billable hours"},
                            "COUNT": {"$sum": 1 }}}]))
            try:
                flag_data=list(db.master.aggregate(
                    [{"$match":{ "role":"agent"}},
                    {"$group": {"_id": {"name":"$user_id","flags": "$flags"}}}]))
                for i in data:
                    i["flags"]=0
                    for j in flag_data:
                        if i["_id"]["name"]==j["_id"]["name"]:
                            i["flags"]=j["_id"]["flags"]  
            except Exception as ex:
                print(ex)
                insert_document("projectagentdetails-flagdata-----",str(ex)) 
        try:
            for i in data:
                i["_id"]["user_name"]=list(db.master.find({"role":"agent","user_id":i["_id"]["name"]},{"user_name":1,"_id":0}))[0]["user_name"]
                i["_id"]["chart_name"]=i["_id"]["name"].replace(" ","") 
        except Exception as ex:
                print(ex)
                insert_document("projectagentdetails-End for loop------",str(ex))
        return render_template("ProjectAgentList.html", data=data)
    except Exception as ex:
        print(ex)
        insert_document("projectagentdetails---",str(ex)) 


#agent view along with filters 
@app.route("/FiltersAgentList",methods=["POST"])
def FiltersAgentList():
    Project= request.form["Project"]
    if not Project:
        Project=session["user_project"]
    fro= request.form["fro"]
    to= request.form["to"]
    time_from = datetime.strptime(fro, "%Y-%m-%d").date()
    time_to=datetime.strptime(to, "%Y-%m-%d").date()
    time_from=datetime.combine(time_from,datetime.min.time())
    time_to=datetime.combine(time_to,datetime.min.time())
    if session['logged_in_user_role']=="supervisor":
        data=list(db.dailySession.aggregate(
                [{"$match": {
                        "project_name":Project,
                        "reports_to": session["logged_in_user_id"],
                        "session_date": {"$gte":time_from,"$lte":time_to} } },
                {"$group": {"_id": {"name":"$user_id","project": "$project_name"},
                        "total_hours": {"$sum": "$total_hours"},"billable_hours":{"$sum":"$billable_hours"},
                        "non_billable_hours":{"$sum":"$non_billable hours"},
                        "COUNT": {"$sum": 1}}}]))
        flag_data=list(db.master.aggregate(
            [{"$match":{ "role":"agent"}},
            {"$group": {"_id": {"name":"$user_id","flags": "$flags"}}}]))
        try:
            for i in data:
                i["flags"]=0
                for j in flag_data:
                    if i["_id"]["name"]==j["_id"]["name"]:
                        i["flags"]=j["_id"]["flags"]  
        except Exception as ex:
            print(ex)
            insert_document("FilterAgentList-----",str(ex)) 
    else:
        data=list(db.dailySession.aggregate(
            [{"$match": {
                        "project_name":Project,
                        "session_date": {"$gte":time_from,"$lte":time_to}}},
                        {                                                                                                                                                                                   
                "$group": {
                        "_id": {"name":"$user_id","project": "$project_name"},
                        "total_hours": {"$sum": "$total_hours"},
                        "billable_hours":{"$sum":"$billable_hours"},
                        "non_billable_hours":{"$sum":"$non_billable hours"},
                        "COUNT": {"$sum": 1 }}}]))
        
        flag_data=list(db.master.aggregate(
            [{"$match":{ "role":"agent"}},
            {"$group": {"_id": {"name":"$user_id","flags": "$flags"}}}]))
        try:
            for i in data:
                i["flags"]=0
                for j in flag_data:
                    if i["_id"]["name"]==j["_id"]["name"]:
                        i["flags"]=j["_id"]["flags"]  
        except Exception as ex:
            print(ex)
            insert_document("FilterAgentList----",str(ex)) 
    try:
        for i in data:
            i["_id"]["user_name"]=list(db.master.find({"role":"agent","user_id":i["_id"]["name"]},{"user_name":1,"_id":0}))[0]["user_name"]
            i["_id"]["chart_name"]=i["_id"]["name"].replace(" ","") 
    except Exception as ex:
        print(ex)
        insert_document("FilterAgentList---",str(ex)) 
    return json.dumps(data)

#display all the violation details.
@app.route('/ViolationMgmt.html',methods=["GET"])
def violation_details():
    try:
        return render_template("ViolationMgmt.html", data=[])
    except Exception as ex:
        print(ex)
        insert_document("violation_details----",str(ex)) 

@app.route('/ViolationMgmt/<PageNo>',methods=["GET"])
def ViolationMgmt(PageNo):
    if not session.get("logged_in_user_role"):
        return render_template("login.html",data="Session expired. Please login again.")
    limit=10
    if(PageNo == "1"):
        offset=((int(PageNo)) * limit) - limit
    else:
        offset=((int(PageNo)) * limit) - limit
        offset=offset -1
    if session['logged_in_user_role']=="supervisor":
        query_result = list(db.violation.find({"marked_as":"TBM","reports_to":session['logged_in_user_id']}, {"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                    "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))              
        query_result2 = db.violation.count_documents({"marked_as":"TBM","reports_to":session['logged_in_user_id']})
    else:
        query_result = list(db.violation.find({"marked_as":"TBM"}, {"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                    "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))              
        query_result2 = db.violation.count_documents({"marked_as":"TBM"})
    try:
        for i in query_result:
            i["_id"] = str(i["_id"])
            i["created_date"]=str(i["created_date"].date())
            i["violation_image"] = (base64.b64encode(i["violation_image"])).decode('utf-8')
            try:
                i["user_name"]=list(db.master.find({"role":"agent","user_id":i["user_id"]},{"user_name":1,"_id":0}))[0]["user_name"]
            except:
                continue
    except Exception as ex:
        print(ex)
        insert_document("violation_details(PageNo)---",str(ex)) 
    if(query_result and query_result2):
        total={"total_rows":query_result2,"data":query_result}
        return json.dumps(total,indent=2)
    else:
        return json.dumps([],indent=2)
    
        

today = date.today()
thirty_days_back= today - timedelta(days=30)
to=str(today)
fro=str(thirty_days_back)
time_from = datetime.strptime(fro, "%Y-%m-%d").date()




"""### THIS API IS NOT IN USE"""
#display  details based on project name and from and to date
######################################################################################################################
@app.route('/ViolationMgmt.html/<string:project>',defaults={"fro":fro,"to":to},methods=["GET"])
@app.route("/ViolationMgmt.html/<string:project>/<string:fro>/<string:to>")
def violation_details_filter(project,fro,to):
    try:
        time_from = datetime.strptime(fro, "%Y-%m-%d").date()
        time_to=datetime.strptime(to, "%Y-%m-%d").date()
        time_from=datetime.combine(time_from,datetime.min.time())
        time_to=datetime.combine(time_to,datetime.min.time())
        data=list(db.violation.find({"project_name":project,"created_date": {"$gte":time_from,"$lte":time_to},"role":"agent"}))
        for i in data:
                i["_id"]= str(i["_id"])
                i["date"]=str(i["date"].date())
                i["violation_image"]=(base64.b64encode(i["violation_image"])).decode('utf-8')
                try:
                    i["user_name"]=list(db.master.find({"role":"agent","user_id":i["user_id"]},{"user_name":1,"_id":0}))[0]["user_name"]
                except:
                    continue
        if session['logged_in_user_role']=="supervisor":
            x=[]
            for i in data:
                if i["user_id"] in session["agent_ids"]:
                    x.append(i)
            data=x
        return render_template("ViolationMgmt.html", data=data)
    except Exception as ex:
        insert_document("violation_details_filter---",str(ex)) 
################################################################################################################################################


@app.route('/escalated_agents/<PageNo>',methods=["GET"])
def escalated_agents(PageNo):
        limit=10
        if(PageNo == "1"):
            offset=((int(PageNo)) * limit) - limit
        else:
            offset=((int(PageNo)) * limit) - limit
            offset=offset -1 
        dbResponse = list(db.violation.find({"marked_as":"ES",}, {"_id": 1, "violation_type": 1, "user_id": 1, "marked_as": 1,
                                                "escalated_by": 1 ,"violation_image":1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
        dbResponse0 = db.violation.count_documents({"marked_as":"ES"})
        try:                                       
            for i in dbResponse:
                i["_id"] = str(i["_id"]) 
                i["created_date"]=str(i["created_date"])
                i["violation_image"] = (base64.b64encode(i["violation_image"])).decode('utf-8')
                i["user_name"]=list(db.master.find({"role":"agent","user_id":i["user_id"]},{"user_name":1,"_id":0}))[0]["user_name"]
            if session['logged_in_user_role']=="supervisor":
                data=[]
                for i in dbResponse:
                        if i["user_id"] in session["agent_ids"]:
                            data.append(i)
                dbResponse=data 
        except Exception as ex:
            print(ex)
            insert_document("escalated_agents(PageNo)----",str(ex))
        if(dbResponse and dbResponse0):
            total={"total_rows":dbResponse0,"data":dbResponse} 
            return json.dumps(total,indent=2) 
        else:
            return json.dumps([],indent=2)
    
# to update individual violations of a particulat violation image that takes in documnet ID as input
@app.route('/ViolationMgmt/<id>/<marked_as>/<user_id>',methods=["GET"])
def update_markedas(id,marked_as,user_id):
    try:
        db.violation.update_one({"_id": ObjectId(id)},{"$set": {"marked_as":marked_as,"escalated_by":session["user_name"]}})
        x=list(db.violation.aggregate(
                        [{"$match":{ "user_id":user_id, 
                        "marked_as":"ES"}},
                        {"$group": {"_id": {"user_id":"$user_id","project_name": "$project_name"},
                        "COUNT": {"$sum": 1}}}]))
        try:
            count=x[0]["COUNT"]
            db.master.update_one({"user_id":user_id,"role":"agent"},{"$set": {"flags":count}})
        except:
            print(ex)
        return Response(response=json.dumps({"message": "marked_as field updated successfully"}))
    except Exception as ex:
        print(ex)
        insert_document("update_markedas-----",str(ex))


                                                          
# to display list of projects to the super admin
@app.route("/Configurations.html",methods = ["GET"])
def configuration():
    try:
        if not session.get("logged_in_user_role"):
            return render_template("login.html",data="Session expired")
        project_names = list(db["master"].distinct("project_name"))
        return render_template("Configurations.html",data = project_names)
    except Exception as ex:
        print(ex)
        insert_document("configuration---",str(ex))

@app.route("/violation_update",methods = ["POST","GET"])
def violation_update():
    try:
        mobile=request.form["mobile"]
        book=request.form["book"]
        multiple=request.form["multiple"]
        no_person=request.form["no_person"]
        project_names = list(db["master"].distinct("project_name"))
        db.master.update_many({"project_name":request.form["projectName"],"role":"agent"},
                                                {"$set": {"violation_filter.mobile":mobile,"violation_filter.multiple_persons":multiple,
                                                        "violation_filter.book":book,"violation_filter.no_person":no_person}})
        return Response(response=json.dumps({"message": "violation_filter field updated successfully"}))
    except Exception as ex:
        print(ex)
        insert_document("violation_update-----",str(ex)) 

@app.route("/GetViolation",methods = ["GET"])
def GetViolation():
    try:
        data = list(db.violation.distinct("violation_type"))
        return json.dumps(data,indent=2)
    except Exception as ex:
        print(ex)
        insert_document("GetViolation----",str(ex))

@app.route("/GetProjectByConfigurations$project=<string:project_name>",methods = ["GET"])   
def configurations_list(project_name):
    try:
        data=list(db.master.find({"project_name":project_name,"role":"agent"},{"violation_filter":1,"_id":0}))
        return json.dumps(data[0])
    except Exception as ex:
        print(ex)
        insert_document("configurations_list----",str(ex)) 


#to display list of agents
@app.route('/UserManagement.html',methods=["GET"])
def userManagement():
    try:
        return render_template('UserManagement.html', data=[])
    except Exception as ex:
        print(ex)
        insert_document("userManagement-----",str(ex)) 


@app.route('/UserManagement/<PageNo>',methods=["GET"])
def userManagementData(PageNo):
    try:
        limit=10
        if(PageNo == "1"):
            offset=((int(PageNo)) * limit) - limit
        else:
            offset=((int(PageNo)) * limit) - limit
            offset=offset -1
        if not session.get("logged_in_user_role"):
            return render_template("login.html",data="Session expired")
        today = datetime.combine(date.today(), datetime.min.time())
        data=list(db.dailySession.find({"session_date_string":str(today)},{"_id":0,"user_id":1,"user_name":1,"project_name":1,"login_time":1,"logout_time":1,"session_status":1}).skip(offset).limit(limit))
        data1=db.dailySession.count_documents({"session_date_string":str(today)})
        for i in data:
            i["user_name"]=list(db.master.find({"role":"agent","user_id":i["user_id"]},{"user_name":1,"_id":0}))[0]["user_name"]
            for key in i.keys():
                if key == "login_time":
                    i[key] = str(i[key])
                if key == "logout_time":
                    i[key] = str(i[key])
        # if user_role=="supervisor":
        if session['logged_in_user_role']=="supervisor":
            x=[]
            for i in data:
                if i["user_id"] in session["agent_ids"]:
                    x.append(i)
            data=x
        if(data and data1):
            total={"total_rows":data1,"data":data} 
            return json.dumps(total,indent=2)
        else:
            return json.dumps([],indent=2)
    except Exception as ex:
        print(ex)
        insert_document("userManagementData----",str(ex)) 

@app.route('/FilterbyAgents',methods=["GET","POST"])
def FilterbyAgents():
    try:
        pageNo= request.form["pageNo"]
        name= request.form["fname"]
        project=""
        if session['logged_in_user_role']=="super_admin":
            project= request.form["fProject"]
        limit=10
        if(pageNo == "1"):
            offset=((int(pageNo)) * limit) - limit
        else:
            offset=((int(pageNo)) * limit) - limit
            offset=offset -1 
        today = datetime.combine(date.today(), datetime.min.time())
        if session['logged_in_user_role']=="supervisor":
            if  project != "" and name != "": 
                data=list(db.dailySession.find({"session_date_string":str(today),"reports_to":session['logged_in_user_id'],"project_name":project,"user_id":{"$regex":name, '$options' : 'i'}},
                {"_id": 0,"user_id": 1, "user_name": 1,"project_name":1,"login_time":1,"logout_time":1,"session_status": 1}).skip(offset).limit(limit))
                data2= db.dailySession.count_documents({"session_date_string":str(today),"project_name":project,"user_id":{"$regex":name, '$options' : 'i'}})
            elif name != "" and  project== "":
                data=list(db.dailySession.find({"session_date_string":str(today),"user_id":{"$regex":name, '$options' : 'i'},"reports_to":session['logged_in_user_id']},
                {"_id": 0, "user_id": 1, "user_name": 1,"project_name":1,"login_time":1,"logout_time":1,"session_status": 1}).skip(offset).limit(limit))
                data2=db.dailySession.count_documents({"session_date_string":str(today),"user_id":{"$regex":name, '$options' : 'i'}})
            elif project != "" and name =="":
                data=list(db.dailySession.find({"session_date_string":str(today),"project_name":project,"reports_to":session['logged_in_user_id']},
                {"_id": 0, "user_id": 1, "user_name": 1,"project_name":1,"login_time":1,"logout_time":1, "session_status": 1}).skip(offset).limit(limit))
                data2=db.dailySession.count_documents({"session_date_string":str(today),"project_name":project})
            else:
                data=list(db.dailySession.find({"session_date_string":str(today),"reports_to":session['logged_in_user_id']},
                {"_id": 0, "user_id": 1, "user_name": 1,"project_name":1,"login_time":1,"logout_time":1,"session_status": 1}).skip(offset).limit(limit))
                data2=db.dailySession.count_documents({"session_date_string":str(today)})
        else:
            if  project != "" and name != "": 
                data=list(db.dailySession.find({"session_date_string":str(today),"project_name":project,"user_id":{"$regex":name, '$options' : 'i'}},
                {"_id": 0,"user_id": 1, "user_name": 1,"project_name":1,"login_time":1,"logout_time":1,"session_status": 1}).skip(offset).limit(limit))
                data2= db.dailySession.count_documents({"session_date_string":str(today),"project_name":project,"user_id":{"$regex":name, '$options' : 'i'}})
            elif name != "" and  project== "":
                data=list(db.dailySession.find({"session_date_string":str(today),"user_id":{"$regex":name, '$options' : 'i'}},
                {"_id": 0, "user_id": 1, "user_name": 1,"project_name":1,"login_time":1,"logout_time":1,"session_status": 1}).skip(offset).limit(limit))
                data2=db.dailySession.count_documents({"session_date_string":str(today),"user_id":{"$regex":name, '$options' : 'i'}})
            elif project != "" and name =="":
                data=list(db.dailySession.find({"session_date_string":str(today),"project_name":project},
                {"_id": 0, "user_id": 1, "user_name": 1,"project_name":1,"login_time":1,"logout_time":1, "session_status": 1}).skip(offset).limit(limit))
                data2=db.dailySession.count_documents({"session_date_string":str(today),"project_name":project})
            else:
                data=list(db.dailySession.find({"session_date_string":str(today)},
                {"_id": 0, "user_id": 1, "user_name": 1,"project_name":1,"login_time":1,"logout_time":1,"session_status": 1}).skip(offset).limit(limit))
                data2=db.dailySession.count_documents({"session_date_string":str(today)})
        if data:
            for i in data:
                i["user_name"]=list(db.master.find({"role":"agent","user_id":i["user_id"]},{"user_name":1,"_id":0}))[0]["user_name"]
                for key in i.keys():
                    if key == "login_time":
                        i[key] = str(i[key])
                    if key == "logout_time":
                        i[key] = str(i[key])
            if(data and data2):
                total={"total_rows":data2,"data":data} 
                return json.dumps(total,indent=2)
        else:
            return json.dumps([],indent=2)
    except Exception as ex:
        print(ex)
        insert_document("FilterbyAgents-----",str(ex))

#to display live (online) agents
@app.route('/user_live/<PageNo>')
def user_live(PageNo):
    try:
        today = datetime.combine(date.today(), datetime.min.time())
        limit=10
        if(PageNo == "1"):
            offset=((int(PageNo)) * limit) - limit
        else:
            offset=((int(PageNo)) * limit) - limit
            offset=offset -1
        data = list(db.dailySession.find({"session_date_string": str(today), "session_status": "live"},
                                        {"_id": 0, "session_date_string": 0, 'billable_hours': 0, 'total_hours': 0,
                                        'non_billable_hours': 0, }).skip(offset).limit(limit))
        data1 = db.dailySession.count_documents({"session_date_string": str(today), "session_status": "live"})
        for i in data:
            i["user_name"]=list(db.master.find({"role":"agent","user_id":i["user_id"]},{"user_name":1,"_id":0}))[0]["user_name"]
            for key in i.keys():
                if key == "login_time":
                    i[key] = str(i[key])
                if key == "logout_time":
                    i[key] = str(i[key])
                if key == 'session_date':
                    i[key] = str(i[key])
        # if user_role=="supervisor":
        if session['logged_in_user_role']=="supervisor":
            x=[]
            for i in data:
                if i["user_id"] in session["agent_ids"]:
                    x.append(i)
            data=x
        if(data and data1):
            total={"total_rows":data1,"data":data} 
            return json.dumps(total,indent=2)
        else:
            return json.dumps([],indent=2) 
        
    except Exception as ex:
        print(ex)
        insert_document("user_live----",str(ex)) 


#display list of all the agents
@app.route('/users_list')
def user_list():
    try:
        today = datetime.combine(date.today(), datetime.min.time())
        data=list(db.dailySession.find({"session_date_string":str(today)},
            {"_id":0,"user_id":1,"user_id":1,"project_name":1,"login_time":1,"logout_time":1,"session_status":1}))
        if session['logged_in_user_role']=="supervisor":
            x=[]
            for i in data:
                if i["user_id"] in session["agent_ids"]:
                    x.append(i)
            data=x
        return json.dumps(data,indent=2)
    except Exception as ex:
        print(ex)
        insert_document("user_list------",str(ex))

@app.route("/GetProjectName",methods = ["GET"])
def GetProjectName():
    try:
        project_names = list(db["master"].distinct("project_name"))
        return json.dumps(project_names,indent=2)
    except Exception as ex:
        print(ex)
        insert_document("GetProjectName-------",str(ex))

@app.route('/FilterbyViolation',methods=["POST"])
def FilterbyViolation():
    try:
        violation= request.form["violation"]
        name= request.form["name"]
        pageNo= request.form["pageNo"]
        limit=10
        if(pageNo == "1"):
            offset=((int(pageNo)) * limit) - limit
        else:
            offset=((int(pageNo)) * limit) - limit
            offset=offset -1

        if session['logged_in_user_role']=="supervisor":
            if  violation != "" and name != "": 
                query_result = list(db.violation.find({"marked_as":"TBM","reports_to":session['logged_in_user_id'],"user_name":{"$regex":name,"$options":"i"},"violation_type":violation},{"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                        "reviewed_by": 1,"reports_to":session['logged_in_user_id'], "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
                num_rows = db.violation.count_documents({"marked_as":"TBM","user_name":{"$regex":name,"$options":"i"},"violation_type":violation})
            elif name != "" and  violation== "":
                query_result = list(db.violation.find({"marked_as":"TBM","reports_to":session['logged_in_user_id'],"user_name":{"$regex":name,"$options":"i"}}, {"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                        "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
                num_rows = db.violation.count_documents({"marked_as":"TBM","reports_to":session['logged_in_user_id'],"user_name":{"$regex":name,"$options":"i"}})
            elif violation != "" and name =="":
                query_result = list(db.violation.find({"marked_as":"TBM","reports_to":session['logged_in_user_id'],"violation_type":violation}, {"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                        "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
                num_rows = db.violation.count_documents({"marked_as":"TBM","reports_to":session['logged_in_user_id'],"violation_type":violation})
            else:
                query_result = list(db.violation.find({"marked_as":"TBM","reports_to":session['logged_in_user_id']}, {"_id": 1,"violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                        "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
                num_rows = db.violation.count_documents({"marked_as":"TBM","reports_to":session['logged_in_user_id']})
        else:
            if  violation != "" and name != "": 
                query_result = list(db.violation.find({"marked_as":"TBM","user_name":{"$regex":name,"$options":"i"},"violation_type":violation},{"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                        "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
                num_rows = db.violation.count_documents({"marked_as":"TBM","user_name":{"$regex":name, '$options' : 'i'},"violation_type":violation})
            elif name != "" and  violation== "":
                query_result = list(db.violation.find({"marked_as":"TBM","user_name":{"$regex":name,"$options":"i"}}, {"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                        "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
                num_rows = db.violation.count_documents({"marked_as":"TBM","user_name":{"$regex":name, '$options' : 'i'}})
            elif violation != "" and name =="":
                query_result = list(db.violation.find({"marked_as":"TBM","violation_type":violation}, {"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                        "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
                num_rows = db.violation.count_documents({"marked_as":"TBM","violation_type":violation})
            else:
                query_result = list(db.violation.find({"marked_as":"TBM"}, {"_id": 1, "violation_type": 1,"user_id":1, "user_name": 1, "marked_as": 1,
                                                        "reviewed_by": 1, "violation_image": 1,"project_name":1,"created_date":1}).sort("created_date",pymongo.DESCENDING).skip(offset).limit(limit))
                num_rows = db.violation.count_documents({"marked_as":"TBM"})
        
        for i in query_result:
            i["_id"] = str(i["_id"])
            i["created_date"]=str(i["created_date"].date())
            i["violation_image"] = (base64.b64encode(i["violation_image"])).decode('utf-8')
            i["user_name"]=list(db.master.find({"role":"agent","user_id":i["user_id"]},{"user_name":1,"_id":0}))[0]["user_name"]
        if(num_rows and query_result):
            total={"total_rows":num_rows,"data":query_result} 
            return json.dumps(total,indent=2)
        else:
            return json.dumps([],indent=2)
    except Exception as ex:
        print(ex)
        insert_document("FilterbyViolation-------",str(ex))
    
@app.route("/LogOut",methods = ["GET"])
def LogOut():
    try:
        session.pop('logged_in_user_role', None)
        session.pop('logged_in_user_id', None)       
        return render_template("login.html")
    except Exception as ex:
        print(ex)
        insert_document("LogOut-------",str(ex))
       

@app.route("/UploadExcel",methods=["POST"])
def UploadExcel():
    try:
        agent_data = request.json
        def_dict=defaultdict(list)
        for d in agent_data:
            for key,value in d.items():
                def_dict[key].append(value)
        try:
            df=pd.DataFrame(def_dict)
        except Exception as ex:
            insert_document("Upload Excel---Data Format Issue---",str(ex))
            df=pd.DataFrame()
        salt = bcrypt.gensalt()
        try:
            for i,r in df.iterrows():
                try:
                    emp=str(r["emp_id"])[-3:]
                except:
                    emp=str(r["emp_id"])
                name=str(r["first_name"]).lower()
                user_name=str(r["first_name"]).capitalize()+str(' ')+str(r["last_name"]).capitalize()
                df.loc[i,["user_name"]]=user_name
                df.loc[i,["user_id"]]=name+emp
                df.loc[i,["password_decoded"]]=str(name+emp+"@")
            for i in range(0,len(df)):
                agent_data=dict(df.iloc[i,:])
                del agent_data["first_name"]
                del agent_data["last_name"]
                agent_data['violation_filter']={"mobile":"on","book":"on","no_person":"on","multiple_persons":"on"}
                agent_data["time_nopersons"]=10.0
                agent_data["flags"]=0
                byte_password=agent_data["password_decoded"].encode("utf-8")
                hash = bcrypt.hashpw(byte_password,salt)
                agent_data["password"]=hash
                agent_data["onboarding_date"] = datetime.today()
                agent_data["expiration_date"] = datetime.today() +  timedelta(days=365)
                if db.master.find_one({"emp_id":agent_data["emp_id"],"role":"agent"},{"_id":0}):
                    break
                else:
                    db.master.insert_one(agent_data)
            return json.dumps({"Status":"Success"})
        except Exception as ex:
            print(ex)
            insert_document("Upload Excel---Logic Issue--",str(ex))
    except Exception as ex:
        insert_document("Upload Excel------",str(ex))
        print(ex)
        print(traceback.format_exc())

@app.route("/UploadImage",methods=["POST"])
def UploadImage():
        agent_data = request.json
        agent_data_new=[]
        emp_id_list=db.master.distinct("emp_id")
        emp_id_not_upload=[]
        try:
            for i in agent_data:
                obj = {}
                obj["emp_id"]=i["emp_id"]
                obj["facial_img"]=base64.b64decode(i["image"])
                array = numpy.array(Image.open(io.BytesIO(obj["facial_img"])))
                try:
                    obj["facial_data"] =(face_recognition.face_encodings(array)[0]).tolist()
                    agent_data_new.append(obj)
                except:
                   emp_id_not_upload.append(obj["emp_id"])
                   print(traceback.format_exc())
                   continue
            for i in agent_data_new:
                if i["emp_id"] in emp_id_list:
                    db.master.update_one({"emp_id":str(i["emp_id"])},{"$set":{"facial_img":i["facial_img"],"facial_data":i["facial_data"]}})        
                else:
                    emp_id_not_upload.append(i["emp_id"])
            return json.dumps(emp_id_not_upload)
        except Exception as ex:
            print(traceback.format_exc())
            insert_document("Upload Image--------",str(ex))  



@app.route('/DownloadAgentTemplate', methods=["GET"])
def DownloadAgentTemplate():
    try:
        file_path = 'agent_template.xlsx'
        return send_file(file_path, as_attachment=True)
    except Exception as ex:
        print(ex)
        insert_document("Download Agent Template-----",str(ex))  


@app.route('/DownloadAgentCredentialsFile', methods=["GET"])
def DownloadAgentCredentialsFile():
    try:
        data=list(db.master.find({"reports_to":session['logged_in_user_id']},{"user_name":1,"user_id":1,"password_decoded":1,"emp_id":1,"_id":0}))   ## change the data bases
        def_dict=defaultdict(list)
        for d in data:
            for key,value in d.items():
                def_dict[key].append(value)
        data=pd.DataFrame(def_dict)
        data.to_excel("agent_credentials.xlsx",index=False)
        file_path = 'agent_credentials.xlsx'
        return send_file(file_path, as_attachment=True)
    except Exception as ex:
        print(ex)
        insert_document("Download Agent Credentials File-----",str(ex))  


@app.route("/Error")
def Error():
    return render_template("Error.html")

if __name__ == "__main__":
    #app.run(host="localhost",port=5000, debug=True)#port=443,
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



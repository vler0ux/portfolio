import pandas as pd
import numpy as np
import json
import itertools
from flask import request, abort
from cached_resource import Resource, get_path_json_file, add_field_pipeline
from api_utils import *
from flask_restx import fields, Namespace
from api_replay_doc import *
from api_utils_doc import *
from models import *
from custom import Custom
from util.mongo_pandas import MongoPandasNoData 
from copy import deepcopy
from api_utils import sort_hours

custo = Custom()
ns = Namespace("API Replay", namespace_replay_desc_doc)

def register_api_replay(api, path, args):
    ns.add_resource(ApiReplayPunctuality, '/punctuality', resource_class_args = args)
    ns.add_resource(ApiReplayLoad, '/load', resource_class_args = args)
    ns.add_resource(ApiReplayExploitation, '/exploitation', resource_class_args = args)

    api.add_namespace(ns, path = path)

class ApiReplay(Resource):

    def init(self):
        self.default_params.update({"dt": 0.25, "is_map":None, "parent":None, "field" : "avg_stop_duration", "field_section" : "avg_real_duration", "punctuality": "punctuality_departure", "max_display" : 600, "quantile" : 10, "nb_versions": None, "speed_all" : False, "field_i18n": None, "type" : None, "reference" : None, "comparison" : None, "event" : None})
        self.reference_date_time = "service_date_time"

class ApiReplayExploitation(ApiReplay):
    @ns.doc(responses={200: 'Success', 404: 'Not found'})
    @ns.produces(["text/csv"])
    @ns.expect(model_payload_parent, validate = True)
    def post(self):
        self.pipeline += [
        {'$match': { 'trip_id': '10_982'}},
        {'$match': { "attached_service_date" :datetime(2024, 8, 15, 0, 0)}},
        {"$project": {
                    "_id": 0,
                    "route_id" : 1,
                    "direction" : "$sections.direction_id",
                    "vehicle_id" : 1,
                    "real_dist_COM" : 1,
                    "theoretical_dist_COM" : 1,
                    "trip_status": 1
                    }}]
                                
        val = self.mp.from_mongodb("exploitation", self.pipeline)#.drop_duplicates().reset_index(drop = True)
        val = val.melt(var_name="fields", value_name="values")

        return val
    
    post.__doc__ = replay_exploitation_version_doc
                        
class ApiReplayPunctuality(ApiReplay):
    def convert_sec_to_display_time(self, df, field):
        l = df[~df[field].isnull()].index
        df.loc[l,field+'_hour'] = (df.loc[l,field] / 3600)
        df.loc[l,field+'_min'] = ((df.loc[l,field]/3600) - df.loc[l,field+"_hour"].astype(int))*60
        df.loc[l,field+"_min"] = df.loc[l,field+"_min"].round()
        df.loc[l,field] = df.loc[l,field+"_hour"].astype(int).astype(str) + ":" + df.loc[l,field+"_min"].astype(int).astype(str).str.zfill(2) +  ":" + (df.loc[l,field] %60).astype(int).astype(str).str.zfill(2)
        df.drop(columns=[field+"_hour", field+"_min"], inplace = True)

        return df

    @ns.doc(responses={200: 'Success', 404: 'Not found'})
    @ns.produces(["text/csv"])
    @ns.expect(model_payload_parent, validate = True)
    def post(self):
        
        self.pipeline += [
            {'$match': { 'trip_id': '10_975'}},
            {'$match': { "attached_service_date" :datetime(2024, 9, 1, 0, 0)}},
            { "$unwind":"$sections" },
            {"$project": {
                    "_id": 0,
                    "start_stop_id":"$sections.stop_id_start_stop",
                    "end_stop_id":"$sections.stop_id_end_stop",
                    "theoretical_duration_end_stop":"$sections.theoretical_duration_end_stop",
                    "stop_sequence":"$sections.real_stop_sequence_start_stop",
                    "stop_sequence_stop":"$sections.real_stop_sequence_end_stop",
                    "theoretical_duration_section":"$sections.theoretical_duration_section",
                    "delta_departure":"$sections.delta_departure_start_stop",
                    "real_duration_section":"$sections.real_duration_section",
                    "real_duration_end_stop":"$sections.real_duration_end_stop",  
                    "time_dec":"$time_dec"
            }}]
    
        val = self.mp.from_mongodb("punctuality", self.pipeline)

        #conversion time_dec en secondes 
        val["time_dec_second"] = val["time_dec"]*3600
        val.sort_values("stop_sequence", inplace =True)

        #add delay on first stop
        val["real_time_dec_second"] = val["time_dec_second"] + val.loc[0,"delta_departure"]
    
        #add first stop of first section
        val0 = val.head(1)
        val0.drop(columns=["stop_sequence_stop", "end_stop_id"], inplace = True)
        val0.rename(columns={"start_stop_id" : "stop_id"}, inplace = True)
        val0["real_duration_end_stop"] = 0
        val0["theoretical_duration_end_stop"] = 0
        val0["real_duration_section"] = 0
        val0["theoretical_duration_section"] = 0

        #keep last stop information of sections
        val.drop(columns=["stop_sequence", "start_stop_id"], inplace = True)
        val.rename(columns={"end_stop_id" : "stop_id", "stop_sequence_stop" : "stop_sequence"}, inplace = True)

        # => all stops
        val = pd.concat([val0, val]).reset_index(drop=True)
        val.sort_values("stop_sequence", inplace = True)

        #propagate duration section and duration end stop
        val["cumul_real_duration_section"] = val["real_duration_section"].cumsum() 
        val["cumul_real_duration_end_stop"] = val["real_duration_end_stop"].cumsum()
        val["real_duration_end_stop_m1"] = val["real_duration_end_stop"].shift(1)
        val["real_duration_end_stop_m1"] = val["real_duration_end_stop_m1"].fillna(0)
        val["cumul_real_duration_end_stop_m1"] = val["real_duration_end_stop_m1"].cumsum()
        val["cumul_theoretical_duration_section"] = val["theoretical_duration_section"].cumsum() 
        val["cumul_theoretical_duration_end_stop"] = val["theoretical_duration_end_stop"].cumsum()
        val["theoretical_duration_end_stop_m1"] = val["theoretical_duration_end_stop"].shift(1)
        val["theoretical_duration_end_stop_m1"] = val["theoretical_duration_end_stop_m1"].fillna(0)
        val["cumul_theoretical_duration_end_stop_m1"] = val["theoretical_duration_end_stop_m1"].cumsum()
        val["real_departure_time"] = val["real_time_dec_second"] + val["cumul_real_duration_section"] + val["cumul_real_duration_end_stop"]
        val["real_arrival_time"] =  val["real_time_dec_second"]  + val["cumul_real_duration_section"] + val["cumul_real_duration_end_stop_m1"]
        val["theoretical_departure_time"] = val["time_dec_second"] + val["cumul_theoretical_duration_section"] + val["cumul_theoretical_duration_end_stop"]
        val["theoretical_arrival_time"] =  val["time_dec_second"]  + val["cumul_theoretical_duration_section"] + val["cumul_theoretical_duration_end_stop_m1"]

        #to display
        val = self.convert_sec_to_display_time(val, "real_departure_time")
        val = self.convert_sec_to_display_time(val, "real_arrival_time")
        val = self.convert_sec_to_display_time(val, "theoretical_departure_time")
        val = self.convert_sec_to_display_time(val, "theoretical_arrival_time")
        val = add_stops_info(self.mp, val, "stop_id", keep=["stop_name","city"])

        return val
    
    post.__doc__ = replay_punctuality_version_doc 

class ApiReplayLoad(ApiReplay):
    @ns.doc(responses={200: 'Success', 404: 'Not found'})
    @ns.produces(["text/csv"])
    @ns.expect(model_payload_parent, validate = True)
    def post(self):
        self.pipeline += [
            {'$match': { 'trip_id': "T2_2081"}},
            {'$match': { "attached_service_date" : datetime (2024, 8, 16, 0, 0)}},    
            {"$unwind":"$sections" },
            {"$project":{
                    "_id" : 0,
                    "start_stop_id": "$sections.start_stop_id",
                    "end_stop" :"$sections.end_stop_id", 
                    "stop_sequence" :"$sections.real_stop_sequence_x", 
                    "start_sequence" :"$sections.real_stop_sequence_y", 
                    "r_boarding": "$sections.r_boarding",
                    "v_boarding": "$sections.v_boarding",
                    "a_boarding": "$sections.a_boarding",
                    "r_load": "$sections.r_load",
                    "v_load": "$sections.v_load",
                    "a_load": "$sections.a_load",
                    "r_alighting": "$sections.r_alighting",
                    "v_alighting": "$sections.v_alighting",
                    "a_alighting": "$sections.a_alighting"
                }}]
        
        val = self.mp.from_mongodb("load", self.pipeline)#.drop_duplicates().reset_index(drop = True)

        #display last end_stop
        val["boarding"] = val["r_boarding"] + val["v_boarding"] + val["a_boarding"] 
        val["load"] = val["r_load"] + val["v_load"] + val["a_load"] 
        val["alighting"] = val["r_alighting"] + val["v_alighting"] + val["a_alighting"] 
        
        # substraction alighting and load last index
        val["last_load"] = val["load"].iloc[-1]- val["alighting"].iloc[-1]

        # add index 0
        val["alighting_add"] = val["alighting"].shift(1)
        val["alighting_add"] = val["alighting_add"].fillna(0)

        #concat _id and end_stop
        def1=val[["start_stop_id" , "stop_sequence" , "boarding", "load", "alighting_add"  ]]
        def1.rename(columns={"start_stop_id":"stop_id",  "boarding" :"boarding", "alighting_add":"alighting" },inplace=True)

        def2=val[["end_stop" , "start_sequence" , "boarding", "last_load"  , "alighting" ]]
        def2.rename(columns={ "end_stop":"stop_id" ,"start_sequence": "stop_sequence" , "boarding" :"boarding", "last_load": "load" },inplace=True)

        val=pd.concat([def1,def2]).drop_duplicates(subset=["stop_sequence"])
        val = add_stops_info(self.mp, val, "stop_id", keep=["stop_name","city"])
        
        return val
  
    post.__doc__ = replay_load_version_doc
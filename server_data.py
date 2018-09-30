
import json


class server_api_result :
    
    def __init__(self,status,description = '',data = '') :
        self.status = status
        self.data = data
        self.description = description
        
    def get_status(self) :
        return self.status
    
    def get_description(self) :
        return self.description
    
    def get_data(self) :
        return self.data
    
    def __str__(self) :
        try :
            return json.dumps({
                    'status' : self.status ,
                    'data' : self.data ,
                    'description' : self.description ,
                })
        except :
            print 'JSON Serializable Error ,Data :',{
                    'status' : self.status ,
                    'data' : self.data ,
                    'description' : self.description ,
                }
    
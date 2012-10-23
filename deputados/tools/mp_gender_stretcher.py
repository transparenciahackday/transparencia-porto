import couchdbkit
import csv
from datetime import datetime

local_server=couchdbkit.Server()
local_db=local_server['parlamento']

gender_list=list(csv.reader(open('mp_genero.csv'), delimiter='|'))

for doc in local_db.all_docs():
    try:
        doc=local_db.get(doc['id'])
        for each in gender_list:
            if doc['ar_id']==each[0] and each[1].strip()!='':
                doc['gender']=each[1]
                local_db.save_doc(doc)
                print doc['name'],
                print ' - ',
                print each[1]
                
        #local_db.save_doc(doc)
    except:
        pass
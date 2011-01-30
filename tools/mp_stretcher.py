import couchdbkit
import csv
from datetime import datetime

local_server=couchdbkit.Server()
local_db=local_server['parlamento']

mp_reader=list(csv.reader(open('MP.csv'), delimiter='|', quotechar='"'))
short_reader=list(csv.reader(open('short_oficial.csv'), delimiter='|'))

docs=[]

for mp in mp_reader:
    for short in short_reader:
        if mp[1] == short[0]:
            if mp[2]!='N/A':
                if mp[4]=='NULL':
                    mp[4]=''
                if mp[3]=='N/A':
                    mp[3]=''
                if len(mp[3])==10:
                        mp[3]=datetime.strptime(mp[3], '%d-%I-%Y').strftime('%Y-%I-%d')
                doc={'name': mp[2],
                     'short_name': short[1],
                     'profession': mp[4],
                     'birth_date': mp[3],
                     'ar_id': mp[1]}
                print doc['ar_id']
                docs.append(doc)

print '%d docs' % len(docs)

for doc in docs:
    local_db.save_doc(doc)
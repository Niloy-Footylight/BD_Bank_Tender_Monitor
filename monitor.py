
import requests, os, json, hashlib, smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

INCLUDE=["electrical","power","hvac","ac","chiller","ventilation","wiring"]
EXCLUDE=["software","it","vehicle","furniture"]

def relevant(t):
 t=t.lower()
 return any(k in t for k in INCLUDE) and not any(k in t for k in EXCLUDE)

def fid(x): return hashlib.md5(x.encode()).hexdigest()

banks=json.load(open('banks.json'))
state=json.load(open('state.json'))
new=[]

for b in banks:
 try:
  r=requests.get(b['url'])
  s=BeautifulSoup(r.text,'lxml')
  items=[]
  for a in s.find_all('a'):
   t=a.get_text(strip=True)
   h=a.get('href')
   if not t or not h: continue
   x=t+h
   if relevant(x): items.append({'t':t,'h':h,'id':fid(x)})
  old={i['id'] for i in state.get(b['url'],[])}
  n=[i for i in items if i['id'] not in old]
  for i in n: new.append(f"{b['bank']}: {i['t']} -> {i['h']}")
  state[b['url']]=items
 except: pass

open('state.json','w').write(json.dumps(state))

if new:
 m=MIMEText("
".join(new))
 m['Subject']='Electrical/AC Tenders'
 m['From']=os.environ['EMAIL_FROM']
 m['To']=os.environ['EMAIL_TO']
 s=smtplib.SMTP(os.environ['SMTP_HOST'],int(os.environ['SMTP_PORT']))
 s.starttls(); s.login(os.environ['SMTP_USERNAME'],os.environ['SMTP_PASSWORD']); s.send_message(m); s.quit()
 print('sent')
else: print('none')

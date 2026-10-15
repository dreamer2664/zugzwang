#!/usr/bin/env python3
"""Upload explicitly selected own-workspace artifacts to sole primary storagecode."""
from pathlib import Path
import argparse,base64,datetime,hashlib,http.client,json,mimetypes,os,re,subprocess,sys,urllib.error,urllib.parse,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.name;REPO='dreamer2664/storagecode';AGENTS=('zugzwang',);ALLOWED={'.zip','.gguf','.bin','.safetensors','.pt','.onnx','.wasm','.exe','.dll','.so','.tar','.gz','.luau','.lua','.rbxlx','.rbxl','.json','.md','.txt','.csv','.tsv','.pgn','.fen','.png','.jpg','.jpeg','.svg','.html','.htm','.js','.mjs','.css','.pdf','.toml','.yaml','.yml','.log'}
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z')
def token():
 value=os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN') or os.environ.get('CHATCODE_TOKEN')
 if not value:raise RuntimeError('Source your private env; no token in argv, URL or repo.')
 return value
def api(method,path,data=None):
 req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/'+path.lstrip('/'),data=json.dumps(data).encode() if data is not None else None,method=method,headers={'Authorization':'Bearer '+token(),'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28','Content-Type':'application/json','User-Agent':PROJECT+'-publisher'})
 with urllib.request.urlopen(req,timeout=180) as r:return json.load(r)
def put_file(path,content,message):
 for _ in range(6):
  try:old=api('GET','contents/'+urllib.parse.quote(path,safe='/'))
  except urllib.error.HTTPError as e:
   if e.code!=404:raise
   old=None
  payload={'message':message,'content':base64.b64encode(content).decode(),'branch':'main'}
  if old:payload['sha']=old['sha']
  try:return api('PUT','contents/'+urllib.parse.quote(path,safe='/'),payload)
  except urllib.error.HTTPError as e:
   if e.code not in (409,422):raise
 raise RuntimeError('Concurrent primary write: preserve receipt and retry; never overwrite blindly')
def append_row(path,row,identity,message):
 for _ in range(6):
  old=api('GET','contents/'+urllib.parse.quote(path,safe='/'));text=base64.b64decode(old['content']).decode()
  if identity in text:return {'already_present':True,'sha':old['sha']}
  payload={'message':message,'content':base64.b64encode((text.rstrip()+'\n'+row+'\n').encode()).decode(),'sha':old['sha'],'branch':'main'}
  try:return api('PUT','contents/'+urllib.parse.quote(path,safe='/'),payload)
  except urllib.error.HTTPError as e:
   if e.code not in (409,422):raise
 raise RuntimeError('Concurrent INDEX/PUSHES append conflict; preserve all rows and retry')
def own_file(agent,path):
 file=Path(path).resolve();own=(ROOT/'agents'/agent).resolve()
 if not file.is_file() or not file.is_relative_to(own):raise ValueError('Only an actual file inside your own agents/<name>/ tree is eligible')
 if any(x in ('.private','private') for x in file.parts) or file.name.startswith('.env') or 'PRIVATE' in file.name.upper():raise ValueError('Private/protected path refused')
 if file.suffix.lower() not in ALLOWED:raise ValueError('Unsupported deliverable format')
 secrets=[os.environ[k].encode() for k in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN') if os.environ.get(k)];keep=max(map(len,secrets),default=1)-1;tail=b'';h=hashlib.sha256();size=file.stat().st_size
 if size>=2*1024**3:raise ValueError('Per-asset 2GiB maximum; choose a smaller or split artifact')
 with file.open('rb') as src:
  for block in iter(lambda:src.read(1024*1024),b''):
   h.update(block);data=tail+block
   if any(k in data for k in secrets):raise ValueError('Known live credential in selected file; refuse')
   tail=data[-keep:] if keep else b''
 if file.suffix.lower()=='.zip':
  with zipfile.ZipFile(file) as z:
   if sum(x.file_size for x in z.infolist())>2*1024**3:raise ValueError('Archive uncompressed size exceeds safety limit')
   for info in z.infolist():
    name=Path(info.filename)
    if name.is_absolute() or '..' in name.parts or any(x in ('.private','private') for x in name.parts) or name.name.startswith('.env') or 'PRIVATE' in name.name.upper():raise ValueError('Unsafe or private ZIP path')
    if info.is_dir():continue
    tail=b''
    with z.open(info) as src:
     for block in iter(lambda:src.read(1024*1024),b''):
      data=tail+block
      if any(k in data for k in secrets):raise ValueError('Known credential in compressed ZIP entry')
      tail=data[-keep:] if keep else b''
 return file,h.hexdigest()
def upload(release,file,digest):
 existing=next((x for x in release['assets'] if x['name']==file.name),None)
 if existing:
  if existing.get('digest')!='sha256:'+digest:raise ValueError('Immutable release asset name collision or unverifiable old asset')
  return existing
 url=release['upload_url'].split('{')[0];parts=urllib.parse.urlsplit(url)
 if parts.scheme!='https' or parts.hostname!='uploads.github.com':raise ValueError('Unexpected release upload host')
 conn=http.client.HTTPSConnection(parts.hostname,timeout=900);target=parts.path+'?'+urllib.parse.urlencode({'name':file.name})
 conn.putrequest('POST',target);conn.putheader('Authorization','Bearer '+token());conn.putheader('Accept','application/vnd.github+json');conn.putheader('User-Agent',PROJECT+'-publisher');conn.putheader('Content-Type',mimetypes.guess_type(file.name)[0] or 'application/octet-stream');conn.putheader('Content-Length',str(file.stat().st_size));conn.endheaders()
 with file.open('rb') as src:
  for block in iter(lambda:src.read(1024*1024),b''):conn.send(block)
 response=conn.getresponse();body=response.read();conn.close()
 if response.status!=201:raise RuntimeError('Asset upload HTTP '+str(response.status)+'; preserve output and inspect safely')
 obj=json.loads(body)
 if obj['size']!=file.stat().st_size or obj.get('digest') and obj['digest']!='sha256:'+digest:raise RuntimeError('Remote byte count/digest mismatch')
 return obj
def main():
 p=argparse.ArgumentParser();p.add_argument('agent',choices=AGENTS);p.add_argument('--file',action='append',required=True,help='primary artifact first, then supporting assets');p.add_argument('--title',required=True);p.add_argument('--revision',required=True);a=p.parse_args()
 if not re.fullmatch(r'r\d{2,3}',a.revision):p.error('revision should look like r01')
 files=[own_file(a.agent,x) for x in a.file];primary,primary_sha=files[0];tag=f'{PROJECT}/{a.agent}/{a.revision}-{primary_sha[:12]}';sha=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
 try:rel=api('GET','releases/tags/'+urllib.parse.quote(tag,safe=''))
 except urllib.error.HTTPError as e:
  if e.code!=404:raise
  rel=api('POST','releases',{'tag_name':tag,'name':f'{PROJECT} / {a.agent} / {a.title} / {a.revision}','body':f'Immutable {PROJECT} deliverable candidate. Contents and actual validation are described in the selected evidence assets; release publication is not independent acceptance.\nPrimary SHA256: `{primary_sha}`\nSource: dreamer2664/{PROJECT}@{sha}','draft':False,'prerelease':False})
 assets=[]
 for file,digest in files:
  item=upload(rel,file,digest);assets.append({'name':file.name,'bytes':file.stat().st_size,'sha256':digest,'url':item['browser_download_url'],'remote_digest':item.get('digest'),'remote_bytes':item['size']})
 receipt={'project':PROJECT,'agent':a.agent,'published_at':now(),'revision':a.revision,'source_sha':sha,'release':rel['html_url'],'tag':tag,'primary_sha256':primary_sha,'assets':assets,'truth':'Published candidate; consult actual test evidence. Upload is not proof of correctness.'}
 own=ROOT/'agents'/a.agent/'evidence';own.mkdir(parents=True,exist_ok=True);local=own/f'{a.revision}-publication.json';local.write_text(json.dumps(receipt,indent=2)+'\n');folder=f'data/{PROJECT}/{a.agent}/{a.revision}-{primary_sha[:12]}'
 put_file(folder+'/publication.json',local.read_bytes(),f'{a.agent}: preserve actual release receipts')
 handoff=ROOT/'agents'/a.agent/'HANDOFF.md'
 if handoff.exists():
  data=handoff.read_bytes()
  if any(os.environ.get(k) and os.environ[k].encode() in data for k in ('CHATCODE_TOKEN','GITHUB_TOKEN','GH_TOKEN')):raise ValueError('Private credential in HANDOFF; refuse archive')
  put_file(folder+'/HANDOFF.md',data,f'{a.agent}: durable action/handoff record')
 identity=f'{PROJECT}/{a.agent}/{a.revision}-{primary_sha[:12]}'
 append_row('data/INDEX.md',f'| {now()[:10]} | {a.agent} | [{a.title}]({folder.removeprefix("data/")}/publication.json) | {identity}; [release]({rel["html_url"]}); primary SHA256 {primary_sha} |',identity,f'{a.agent}: index immutable project artifact')
 append_row('PUSHES.md',f'| {now()} | {a.agent} | {PROJECT} | `{sha[:12]}` | {identity}; [release]({rel["html_url"]}) |',identity,f'{a.agent}: record source+artifact checkpoint')
 receipt['primary_archive']='https://github.com/'+REPO+'/tree/main/'+folder;local.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2));return 0
if __name__=='__main__':sys.exit(main())

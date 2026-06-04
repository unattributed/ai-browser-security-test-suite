#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
ROOT=Path(__file__).resolve().parents[1]
EXAMPLE_ROOT=ROOT/'examples'/'browser-safe-ai-methods'
def payloads(): return sorted(EXAMPLE_ROOT.glob('*/variation-*.payload.txt'))
def get(url, timeout):
    with urlopen(url, timeout=timeout) as response:
        response.read(1)
        return response.status

def sample_response(url, payload, timeout, max_lines):
    body=json.dumps(payload).encode('utf-8')
    req=Request(url, data=body, headers={'Content-Type':'application/json'}, method='POST')
    lines=[]
    with urlopen(req, timeout=timeout) as response:
        status=response.status
        for raw in response:
            line=raw.decode('utf-8', errors='replace').strip()
            if line: lines.append(line)
            if len(lines)>=max_lines: break
    return status, lines
def main():
    ap=argparse.ArgumentParser(description='Exercise Browser-Safe AI example payloads against weak local ollama-webui.')
    ap.add_argument('--target-url',default='http://127.0.0.1:11435'); ap.add_argument('--model',default='gemma4:e2b')
    ap.add_argument('--out',type=Path,default=Path.home()/'browser-safe-ai-workshop'/'example-payload-smoke-test'/f'payload-smoke-{int(time.time())}.json')
    ap.add_argument('--timeout',type=float,default=60.0); ap.add_argument('--max-lines',type=int,default=2)
    args=ap.parse_args(); ps=payloads()
    if not ps: raise SystemExit(f'no payloads found under {EXAMPLE_ROOT}')
    base=args.target_url.rstrip('/')
    get(base+'/health', 10)
    get(base+'/api/browser-safe/target-contract', 10)
    results=[]; failures=[]
    for p in ps:
        prompt=p.read_text(encoding='utf-8')
        item={'payload':str(p.relative_to(ROOT)),'marker_present':'SYNTHETIC-LAB-MARKER' in prompt,'target_url':args.target_url,'model':args.model}
        try:
            status, lines=sample_response(base+'/api/generate', {'model':args.model,'prompt':prompt}, args.timeout, args.max_lines)
            item['status_code']=status; item['sample_lines']=lines; item['accepted']=status==200 and bool(lines)
        except HTTPError as exc:
            item['accepted']=False; item['status_code']=exc.code; item['error']=exc.read().decode('utf-8', errors='replace')[:500]
        except (URLError, TimeoutError, Exception) as exc:
            item['accepted']=False; item['error']=str(exc)
        if not item.get('accepted') or not item.get('marker_present'): failures.append(item)
        results.append(item)
    report={'schema_version':'browser-safe-ai-example-payload-smoke-test/v0.1','created_at_epoch':int(time.time()),'target_url':args.target_url,'model':args.model,'payload_count':len(ps),'accepted_count':sum(1 for r in results if r.get('accepted')),'failures':failures,'results':results}
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'report':str(args.out),'payload_count':report['payload_count'],'accepted_count':report['accepted_count'],'failure_count':len(failures)},indent=2))
    return 0 if not failures else 1
if __name__=='__main__': raise SystemExit(main())

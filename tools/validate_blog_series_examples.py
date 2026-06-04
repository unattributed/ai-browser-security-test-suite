#!/usr/bin/env python3
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
EXAMPLE_ROOT=ROOT/'examples'/'browser-safe-ai-methods'
COVERAGE_DOC=ROOT/'docs'/'workshop'/'blog-series-method-coverage.md'
VALID_DOM={'baseline','hidden_instruction','rendered_contradiction'}
VALID_IFRAME={'baseline','sandboxed_frame','srcdoc_hidden_context','nested_frame_chain'}
VALID_STORAGE={'baseline_no_state','cookie_state_boundary','local_storage_state_boundary','session_storage_state_boundary','combined_state_boundary'}
VALID_REDIRECT={'baseline','encoded','slow'}
SECTIONS=['## Blog reference','## Workshop lab','## Operator objective','## Method definition','## Start weak ollama-webui','## Payload','## Execute against weak ollama-webui','## Evidence to collect','## Expected result','## Reporting notes']
def dirs(): return sorted(p for p in EXAMPLE_ROOT.iterdir() if p.is_dir())
def vars_from(text,prefix): return re.findall(re.escape(prefix)+r'[^\s"\'`)]*variant=([A-Za-z0-9_]+)',text)
def validate():
    errors=[]
    if not EXAMPLE_ROOT.exists(): return [f'missing example root: {EXAMPLE_ROOT}']
    methods=dirs()
    if len(methods)<21: errors.append(f'expected at least 21 method folders, found {len(methods)}')
    coverage=COVERAGE_DOC.read_text(encoding='utf-8') if COVERAGE_DOC.exists() else ''
    for method in methods:
        readme=method/'README.md'
        if not readme.exists(): errors.append(f'{method.name}: missing README.md'); continue
        rt=readme.read_text(encoding='utf-8')
        if 'http://127.0.0.1:11435' not in rt or '$HOME/Workspace/ollama-webui' not in rt: errors.append(f'{method.name}: README missing weak target start details')
        docs=sorted(method.glob('variation-*.md')); payloads=sorted(method.glob('variation-*.payload.txt'))
        if len(docs)!=3: errors.append(f'{method.name}: expected exactly 3 variation docs, found {len(docs)}')
        if len(payloads)!=3: errors.append(f'{method.name}: expected exactly 3 payload files, found {len(payloads)}')
        if method.name not in coverage: errors.append(f'coverage doc missing method {method.name}')
        for doc in docs:
            text=doc.read_text(encoding='utf-8')
            for sec in SECTIONS:
                if sec not in text: errors.append(f'{doc.relative_to(ROOT)} missing {sec}')
            for term in ['SYNTHETIC-LAB-MARKER','http://127.0.0.1:11435','/home/foo/Workspace/unattributed.github.io/_posts','docs/workshop/labs/','$HOME/Workspace/ollama-webui']:
                if term not in text: errors.append(f'{doc.relative_to(ROOT)} missing {term}')
            pf=method/doc.name.replace('.md','.payload.txt')
            if not pf.exists(): errors.append(f'{doc.relative_to(ROOT)} missing paired payload {pf.name}')
            else:
                pt=pf.read_text(encoding='utf-8').strip()
                if 'SYNTHETIC-LAB-MARKER' not in pt: errors.append(f'{pf.relative_to(ROOT)} missing SYNTHETIC-LAB-MARKER')
                if pt not in text: errors.append(f'{doc.relative_to(ROOT)} does not embed exact paired payload')
            for v in vars_from(text,'/browser-safe/dom-render-mismatch'):
                if v not in VALID_DOM: errors.append(f'{doc.relative_to(ROOT)} invalid DOM variant {v}')
            for v in vars_from(text,'/browser-safe/iframe-frame-tree'):
                if v not in VALID_IFRAME: errors.append(f'{doc.relative_to(ROOT)} invalid iframe variant {v}')
            for v in vars_from(text,'/browser-safe/storage-state-boundary'):
                if v not in VALID_STORAGE: errors.append(f'{doc.relative_to(ROOT)} invalid storage variant {v}')
            for v in vars_from(text,'/browser-safe/redirect/start'):
                if v not in VALID_REDIRECT: errors.append(f'{doc.relative_to(ROOT)} invalid redirect variant {v}')
    return errors
def main():
    errors=validate()
    if errors:
        print('Blog series example validation failed:')
        for e in errors: print('-',e)
        return 1
    print(f'Validated {len(dirs())} Browser-Safe AI method example folders.')
    return 0
if __name__=='__main__': raise SystemExit(main())

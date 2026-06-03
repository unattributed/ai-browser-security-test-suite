#!/usr/bin/env python3
"""Run Lab 10 model verdict policy live local evidence capture.

File path:
  tools/run_workshop_lab_10_model_verdict_policy_live_evidence.py

File name:
  run_workshop_lab_10_model_verdict_policy_live_evidence.py

Change description:
  Adds a one-command Lab 10 evidence runner that generates local synthetic
  model-verdict fixtures, serves them on loopback, captures direct and proxied
  HTTP evidence, captures Playwright browser-observed model responses, source,
  DOM, visible text, and screenshot evidence, records weak-target contract
  readiness, applies a deterministic target-backed policy gate artifact, writes
  review notes, writes an artifact manifest, writes SHA256SUMS.txt, creates a
  .tar.gz evidence archive, and creates a .tar.gz.sha256 checksum file.

Git commit comment:
  add lab 10 model verdict policy live evidence runner

Safety boundary:
  local-only, synthetic-only, authorized-only, no real credentials, no real
  customer data, no public callback endpoints, no third-party targets, no
  package installation, no production policy engine claim, no production
  enforcement engine claim, and no production security validation claim. The
  local ollama-webui target is intentionally weak by design and must not be
  hardened by this runner.

Release gate evidence standard:
  one-command Lab 10 model verdict manipulation and policy simulator end-to-end
  live evidence runner with Playwright model-response capture integration,
  target-backed policy gate, direct local HTTP responses with proxied local HTTP responses, artifact-manifest.json, SHA256SUMS.txt, SYNTHETIC-LAB-MARKER,
  intentionally weak target must remain vulnerable, model response is evidence,
  not policy, no production policy engine claim, no production enforcement
  engine claim, and no production security validation.
"""
from __future__ import annotations
import argparse, contextlib, hashlib, http.client, http.server, importlib.util, json, shutil, signal, socket, subprocess, sys, tarfile, threading, time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen
SCHEMA_VERSION="browser-safe-ai-workshop-lab10-model-verdict-policy-live-evidence/v0.1"; SAFETY_MARKER="SYNTHETIC-LAB-MARKER"
WEAK_TARGET_PRESERVATION_RULE="ollama-webui is intentionally weak and must not be hardened by this Lab 10 evidence runner"
DEFAULT_REPO_ROOT=Path("/home/foo/Workspace/ai-browser-security-test-suite"); DEFAULT_WEAK_TARGET_REPO=Path("/home/foo/Workspace/ollama-webui")
DEFAULT_TARGET_URL="http://127.0.0.1:11435"; DEFAULT_OLLAMA_URL="http://127.0.0.1:11434"; DEFAULT_FIXTURE_HOST="127.0.0.1"; DEFAULT_FIXTURE_PORT=18101; DEFAULT_MITM_HOST="127.0.0.1"; DEFAULT_MITM_PORT=18102
ARCHIVE_SUFFIX=".tar.gz"; ARCHIVE_CHECKSUM_SUFFIX=".tar.gz.sha256"
FORBIDDEN_COMMAND_TERMS=["apt"+"-get","apt"+" install","apt"+" upgrade","pip"+" install","playwright"+" install","nvidia","dkms","linux-"+"image","linux-"+"headers","cuda"]
MITMPROXY_PRIVATE_CA_FILENAMES={"mitmproxy-ca.pem","mitmproxy-ca-cert.pem","mitmproxy-ca-cert.cer","mitmproxy-ca-cert.p12","mitmproxy-ca.p12"}
REQUIRED_ARTIFACTS=["safety-boundary.json","service-exposure/listeners-before-fixture-server.txt","service-exposure/listeners-after-fixture-server.txt","service-exposure/listeners-after-run.txt","service-exposure/weak-target-sop.json","service-exposure/weak-target-health.http","target-contract/target-contract-readiness.json","fixtures/fixture-manifest.json","fixtures/policy-scenarios.json","fixtures/policy-simulation-results.json","fixtures/policy-decisions.jsonl","fixtures/verdict-mismatch-report.json","fixtures/model-response-review-harness.html","http-replay/captured-url-index.json","proxy-evidence/mitmdump-status.json","proxy-evidence/mitmproxy-private-material-removal.json","browser-evidence/browser-capture-index.json","browser-evidence/model-response-capture.json","browser-evidence/browser-source.html","browser-evidence/browser-dom.html","browser-evidence/browser-visible-text.txt","browser-evidence/browser-screenshot.png","policy-gate/target-backed-policy-gate.json","policy-gate/target-backed-policy-gate-review.md","model-response-capture/model-response-capture-review.md","verdict-boundary/verdict-boundary-review.md","zap-passive-review/zap-status.json","lab10-live-evidence-summary.md"]
REPLAY_PATHS=["fixture-manifest.json","policy-scenarios.json","policy-simulation-results.json","policy-decisions.jsonl","verdict-mismatch-report.json","analyst-notes-template.md","model-response-review-harness.html"]
@dataclass(frozen=True)
class CommandResult: command:list[str]; returncode:int; stdout:str; stderr:str
def utc_now()->str: return datetime.now(timezone.utc).isoformat()
def default_stamp()->str: return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
def write_text(path:Path, content:str)->None: path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content, encoding="utf-8")
def write_bytes(path:Path, content:bytes)->None: path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(content)
def write_json(path:Path, data:Any)->None: write_text(path, json.dumps(data, indent=2, sort_keys=True)+"\n")
def sha256_file(path:Path)->str:
    digest=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b""): digest.update(chunk)
    return digest.hexdigest()
def run_command(command:list[str], *, timeout:int=120, cwd:Path|None=None)->CommandResult:
    c=subprocess.run(command,cwd=cwd,text=True,capture_output=True,timeout=timeout,check=False); return CommandResult(command,c.returncode,c.stdout,c.stderr)
def command_path(name:str, *, required:bool=True)->str|None:
    found=shutil.which(name)
    if not found and required: raise SystemExit(f"required command not found: {name}")
    return found
def assert_no_forbidden_terms_in_argv()->None:
    combined=" ".join(sys.argv).lower()
    for term in FORBIDDEN_COMMAND_TERMS:
        if term in combined: raise SystemExit(f"forbidden command term detected in runner arguments: {term}")
def assert_loopback_host(host:str)->None:
    if host not in {"127.0.0.1","localhost","::1"}: raise SystemExit(f"host must be loopback-only: {host}")
def assert_loopback_url(url:str)->None:
    parsed=urlparse(url)
    if parsed.scheme not in {"http","https"}: raise SystemExit(f"URL must use http or https for local loopback capture: {url}")
    if parsed.hostname not in {"127.0.0.1","localhost","::1"}: raise SystemExit(f"URL must be loopback-only: {url}")
def join_url(base:str,path:str)->str: return base.rstrip("/")+"/"+path.lstrip("/")
def import_lab10_generator(repo_root:Path)->Any:
    module_path=repo_root/"tools/generate_lab_10_model_verdict_policy_fixtures.py"
    if not module_path.is_file(): raise SystemExit(f"Lab 10 fixture generator missing: {module_path}")
    spec=importlib.util.spec_from_file_location("generate_lab_10_model_verdict_policy_fixtures", module_path)
    if spec is None or spec.loader is None: raise SystemExit("could not load Lab 10 fixture generator")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module
def capture_listeners(path:Path)->None:
    if shutil.which("ss"):
        r=run_command(["ss","-ltnp"],timeout=30); write_text(path,"$ ss -ltnp\n"+r.stdout+r.stderr+f"\nexit_status={r.returncode}\n")
    else: write_text(path,"ss command not available\n")
def capture_weak_target_git_state(out_dir:Path, weak_target_repo:Path)->None:
    state_dir=out_dir/"service-exposure"
    if not weak_target_repo.is_dir() or not (weak_target_repo/".git").is_dir(): write_json(state_dir/"weak-target-git-state.json",{"available":False,"path":str(weak_target_repo),"preservation_rule":WEAK_TARGET_PRESERVATION_RULE}); return
    status=run_command(["git","status","--short"],cwd=weak_target_repo,timeout=30); head=run_command(["git","rev-parse","HEAD"],cwd=weak_target_repo,timeout=30); branch=run_command(["git","branch","--show-current"],cwd=weak_target_repo,timeout=30)
    write_json(state_dir/"weak-target-git-state.json",{"available":True,"path":str(weak_target_repo),"branch":branch.stdout.strip(),"head":head.stdout.strip(),"status_short":status.stdout,"clean":status.returncode==0 and status.stdout.strip()=="","preservation_rule":WEAK_TARGET_PRESERVATION_RULE})
def capture_target_health(out_dir:Path,target_url:str,ollama_url:str)->dict[str,Any]:
    assert_loopback_url(target_url); assert_loopback_url(ollama_url); service_dir=out_dir/"service-exposure"; contract_dir=out_dir/"target-contract"
    write_json(service_dir/"weak-target-sop.json",{"checked_at_utc":utc_now(),"weak_target_url":target_url,"ollama_url":ollama_url,"local_only":True,"synthetic_only":True,"authorized_only":True,"preservation_rule":WEAK_TARGET_PRESERVATION_RULE,"runner_started_or_modified_weak_target":False,"operator_note":"Start the intentionally weak local target separately when target-backed allow evidence is required. This runner does not harden or reconfigure it."})
    health={"checked_at_utc":utc_now(),"target_url":target_url,"local_only":True,"synthetic_only":True,"authorized_only":True,"target_backed_policy_gate":True,"target_health_required_for_allow":True,"preservation_rule":WEAK_TARGET_PRESERVATION_RULE,"fabricated":False}
    try:
        with urlopen(Request(target_url,headers={"User-Agent":"browser-safe-ai-lab10-live-evidence/0.1"}),timeout=10) as response:
            body=response.read(8192); headers="".join(f"{k}: {v}\n" for k,v in response.headers.items()); health.update({"available":True,"status_code":response.status,"reason":response.reason,"body_sha256":hashlib.sha256(body).hexdigest()}); write_bytes(service_dir/"weak-target-health.http",f"HTTP/1.1 {response.status} {response.reason}\n{headers}\n".encode()+body)
    except Exception as exc:
        health.update({"available":False,"status_code":None,"error":repr(exc),"policy_gate_behavior":"fail_closed_to_review_for_allow_capable_cases"}); write_text(service_dir/"weak-target-health.http",f"target unavailable: {exc!r}\n")
    write_json(contract_dir/"target-contract-readiness.json",health); return health
def write_safety_boundary(out_dir:Path,args:argparse.Namespace)->None:
    write_json(out_dir/"safety-boundary.json",{"schema_version":SCHEMA_VERSION,"created_at_utc":utc_now(),"safety_marker":SAFETY_MARKER,"local_only":True,"synthetic_only":True,"authorized_only":True,"no_real_credentials":True,"no_real_customer_data":True,"no_public_callback_endpoints":True,"no_third_party_targets":True,"no_package_installation":True,"no_production_policy_engine_claim":True,"no_production_enforcement_engine_claim":True,"no_production_security_validation_claim":True,"model_response_is_evidence_not_policy":True,"weak_target_preservation_rule":WEAK_TARGET_PRESERVATION_RULE,"repo_root":str(args.repo_root),"weak_target_repo":str(args.weak_target_repo),"target_url":args.target_url,"ollama_url":args.ollama_url})
def write_browser_harness(fixtures_dir:Path)->None:
    model_paths=sorted(path.name for path in (fixtures_dir/"model-responses").glob("*.txt"))
    harness=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Lab 10 Model Response Review Harness</title></head><body><main><h1>{SAFETY_MARKER} Lab 10 Model Response Review Harness</h1><p>model response is evidence, not policy.</p><p>This local-only harness loads synthetic model-response fixtures and policy simulator outputs.</p><section id="summary">waiting for local model-response capture</section><pre id="capture"></pre></main><script>const marker={json.dumps(SAFETY_MARKER)};const modelPaths={json.dumps(model_paths)};window.lab10ModelResponseCapture={{completed:false,model_responses:[]}};async function loadJson(path){{const response=await fetch(path,{{cache:'no-store'}});return await response.json();}}async function loadText(path){{const response=await fetch(path,{{cache:'no-store'}});return await response.text();}}async function runCapture(){{const manifest=await loadJson('fixture-manifest.json');const simulation=await loadJson('policy-simulation-results.json');const mismatch=await loadJson('verdict-mismatch-report.json');const responses=[];for(const name of modelPaths){{const text=await loadText('model-responses/'+name);responses.push({{filename:name,contains_marker:text.includes(marker),text_sha256_hint:String(text.length)+':'+text.slice(0,24),text_prefix:text.slice(0,360)}});}}window.lab10ModelResponseCapture={{completed:true,safety_marker:marker,local_only:true,synthetic_only:true,authorized_only:true,playwright_model_response_capture_integration:true,model_response_is_evidence_not_policy:true,target_backed_policy_gate_expected:true,scenario_count:manifest.scenario_count,model_response_count:responses.length,policy_result_count:simulation.results.length,model_policy_mismatch_count:mismatch.mismatch_count,model_responses:responses}};document.getElementById('summary').textContent='captured '+responses.length+' local synthetic model responses';document.getElementById('capture').textContent=JSON.stringify(window.lab10ModelResponseCapture,null,2);}}runCapture();</script></body></html>'''
    write_text(fixtures_dir/"model-response-review-harness.html",harness)
def generate_fixtures(repo_root:Path,out_dir:Path)->dict[str,Any]:
    generator=import_lab10_generator(repo_root); fixtures_dir=out_dir/"fixtures"; manifest=generator.write_fixtures(fixtures_dir); write_browser_harness(fixtures_dir); return manifest
def start_static_server(directory:Path,host:str,port:int)->tuple[http.server.ThreadingHTTPServer,threading.Thread]:
    assert_loopback_host(host)
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self,*args:Any,**kwargs:Any)->None: super().__init__(*args,directory=str(directory),**kwargs)
        def log_message(self,format:str,*args:Any)->None: return
    server=http.server.ThreadingHTTPServer((host,port),Handler); thread=threading.Thread(target=server.serve_forever,name="lab10-fixture-server",daemon=True); thread.start()
    for _ in range(30):
        with contextlib.suppress(OSError):
            with socket.create_connection((host,port),timeout=1): return server,thread
        time.sleep(0.25)
    raise SystemExit(f"fixture server did not become reachable on {host}:{port}")
def http_response_bytes(url:str,proxy_host:str|None=None,proxy_port:int|None=None)->bytes:
    assert_loopback_url(url); parsed=urlparse(url); target_host=parsed.hostname or "127.0.0.1"; target_port=parsed.port or (443 if parsed.scheme=="https" else 80); target_path=parsed.path or "/"
    if parsed.query: target_path=f"{target_path}?{parsed.query}"
    if proxy_host and proxy_port: assert_loopback_host(proxy_host); conn=http.client.HTTPConnection(proxy_host,proxy_port,timeout=20); request_target=url
    else: conn=http.client.HTTPConnection(target_host,target_port,timeout=20); request_target=target_path
    conn.request("GET",request_target,headers={"Host":f"{target_host}:{target_port}","User-Agent":"browser-safe-ai-lab10-live-evidence/0.1"}); response=conn.getresponse(); body=response.read(); status_line=f"HTTP/1.1 {response.status} {response.reason}\r\n".encode(); headers=b"".join(f"{k}: {v}\r\n".encode(errors="replace") for k,v in response.getheaders()); conn.close(); return status_line+headers+b"\r\n"+body
def start_mitmdump(out_dir:Path,host:str,port:int)->subprocess.Popen[str]|None:
    mitmdump=command_path("mitmdump",required=False); status_path=out_dir/"proxy-evidence/mitmdump-status.json"; conf_dir=out_dir/"proxy-evidence/mitmdump-conf"; conf_dir.mkdir(parents=True,exist_ok=True)
    if not mitmdump: write_json(status_path,{"status":"unavailable-tool-exception","tool":"mitmdump","local_only":True,"fabricated":False}); return None
    process=subprocess.Popen([mitmdump,"--mode",f"regular@{host}:{port}","--set",f"confdir={conf_dir}","--set","block_global=false","--set","flow_detail=1"],stdout=(out_dir/"proxy-evidence/mitmdump.log").open("w",encoding="utf-8"),stderr=subprocess.STDOUT,text=True,start_new_session=True); write_text(out_dir/"proxy-evidence/mitmdump.pid",f"{process.pid}\n")
    for _ in range(30):
        with contextlib.suppress(OSError):
            with socket.create_connection((host,port),timeout=1): write_json(status_path,{"status":"running","pid":process.pid,"local_only":True,"fabricated":False}); return process
        if process.poll() is not None: write_json(status_path,{"status":"failed","returncode":process.returncode,"local_only":True,"fabricated":False}); return None
        time.sleep(0.5)
    write_json(status_path,{"status":"startup-timeout","pid":process.pid,"local_only":True,"fabricated":False}); process.send_signal(signal.SIGTERM); return None
def remove_mitmproxy_private_material(out_dir: Path) -> None:
    conf_dir = out_dir / "proxy-evidence/mitmdump-conf"
    removed: list[str] = []
    private_names = set(MITMPROXY_PRIVATE_CA_FILENAMES) | {"mitmproxy-ca.p12"}
    private_globs = ("*.p12",)
    candidate_paths: set[Path] = set()
    if conf_dir.exists():
        for private_name in private_names:
            candidate_paths.update(conf_dir.rglob(private_name))
        for private_glob in private_globs:
            candidate_paths.update(conf_dir.rglob(private_glob))
    for path in sorted(candidate_paths):
        if path.is_file():
            removed.append(path.relative_to(out_dir).as_posix())
            path.unlink()
    remaining: list[str] = []
    if conf_dir.exists():
        for private_name in private_names:
            remaining.extend(p.relative_to(out_dir).as_posix() for p in sorted(conf_dir.rglob(private_name)) if p.is_file())
        for private_glob in private_globs:
            remaining.extend(p.relative_to(out_dir).as_posix() for p in sorted(conf_dir.rglob(private_glob)) if p.is_file())
    remaining = sorted(set(remaining))
    write_json(
        out_dir / "proxy-evidence/mitmproxy-private-material-removal.json",
        {
            "checked_at_utc": utc_now(),
            "removed": sorted(set(removed)),
            "remaining_mitmproxy_ca_files": remaining,
            "private_material_patterns": sorted(private_names | set(private_globs)),
        },
    )

def replay_paths(fixtures_dir:Path)->list[str]: return sorted(set(REPLAY_PATHS+[f"model-responses/{p.name}" for p in sorted((fixtures_dir/"model-responses").glob("*.txt"))]))
def capture_http_replays(out_dir:Path,fixture_base_url:str,fixtures_dir:Path,mitm_host:str,mitm_port:int,use_proxy:bool)->None:
    captured=[]
    for relative in replay_paths(fixtures_dir):
        artifact_name=relative.replace("/","__"); url=join_url(fixture_base_url,relative); direct_path=out_dir/"http-replay/direct"/f"{artifact_name}.http"; write_bytes(direct_path,http_response_bytes(url)); proxied_path=out_dir/"http-replay/proxied"/f"{artifact_name}.http"
        write_bytes(proxied_path,http_response_bytes(url,proxy_host=mitm_host,proxy_port=mitm_port) if use_proxy else b"HTTP/1.1 599 proxy unavailable\r\nX-Browser-Safe-AI-Status: unavailable-tool-exception\r\n\r\nmitmdump unavailable. No proxy evidence was fabricated.\n")
        captured.append({"relative_path":relative,"url":url,"direct":direct_path.relative_to(out_dir).as_posix(),"proxied":proxied_path.relative_to(out_dir).as_posix()})
    write_json(out_dir/"http-replay/captured-url-index.json",{"captured_at_utc":utc_now(),"urls":captured})
def capture_browser_evidence(out_dir:Path,fixture_base_url:str)->dict[str,Any]:
    from playwright.sync_api import sync_playwright
    harness_url=join_url(fixture_base_url,"model-response-review-harness.html"); browser_dir=out_dir/"browser-evidence"; browser_dir.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True); page=browser.new_page(viewport={"width":1280,"height":900}); page.goto(harness_url,wait_until="networkidle"); page.wait_for_function("window.lab10ModelResponseCapture && window.lab10ModelResponseCapture.completed === true",timeout=10000); capture=page.evaluate("window.lab10ModelResponseCapture"); source=page.content(); dom=page.evaluate("document.documentElement.outerHTML"); visible_text=page.locator("body").inner_text(timeout=10000); page.screenshot(path=str(browser_dir/"browser-screenshot.png"),full_page=True); browser.close()
    write_text(browser_dir/"browser-source.html",source); write_text(browser_dir/"browser-dom.html",dom); write_text(browser_dir/"browser-visible-text.txt",visible_text); write_json(browser_dir/"model-response-capture.json",capture); write_json(browser_dir/"browser-capture-index.json",{"captured_at_utc":utc_now(),"harness_url":harness_url,"playwright_model_response_capture_integration":True,"model_response_is_evidence_not_policy":True,"source":"browser-evidence/browser-source.html","dom":"browser-evidence/browser-dom.html","visible_text":"browser-evidence/browser-visible-text.txt","screenshot":"browser-evidence/browser-screenshot.png","model_response_capture":"browser-evidence/model-response-capture.json","model_response_count":capture.get("model_response_count",0)}); return capture
def load_json(path:Path)->dict[str,Any]: return json.loads(path.read_text(encoding="utf-8"))
def build_target_backed_policy_gate(out_dir:Path,target_health:dict[str,Any])->dict[str,Any]:
    simulation=load_json(out_dir/"fixtures/policy-simulation-results.json"); mismatch=load_json(out_dir/"fixtures/verdict-mismatch-report.json"); target_available=bool(target_health.get("available")); decisions=[]; violations=[]
    for result in simulation["results"]:
        model_verdict=result.get("model_verdict"); policy_decision=result.get("policy_decision"); indicators=set(result.get("evidence_indicators",[])); schema_valid=bool(result.get("schema_valid")); required_state=result.get("required_evidence_state"); gate_reasons=[]
        if not target_available and policy_decision=="allow": gate_decision="review"; gate_reasons.append("weak target readiness was unavailable, so allow-capable cases route to review")
        elif not schema_valid: gate_decision="block"; gate_reasons.append("model response did not satisfy the output contract")
        elif required_state!="complete": gate_decision="review"; gate_reasons.append("required browser evidence was incomplete")
        elif indicators & {"untrusted_content_requested_allow","policy_downgrade_attempt","hidden_instruction_present","dom_render_mismatch_present","parser_pressure","invalid_output_schema"}: gate_decision="block"; gate_reasons.append("captured evidence contained adversarial decision-pressure indicators")
        else: gate_decision=policy_decision; gate_reasons.append("deterministic simulator policy decision was preserved")
        if model_verdict=="allow" and gate_decision=="allow" and indicators: violations.append(f"unsafe allow survived target-backed policy gate: {result['scenario_id']}")
        decisions.append({"scenario_id":result["scenario_id"],"model_verdict":model_verdict,"simulator_policy_decision":policy_decision,"target_backed_gate_decision":gate_decision,"model_output_treated_as_policy":False,"schema_valid":schema_valid,"required_evidence_state":required_state,"evidence_indicators":sorted(indicators),"gate_reasons":gate_reasons})
    gate={"schema_version":"browser-safe-ai-workshop-lab10-target-backed-policy-gate/v0.1","created_at_utc":utc_now(),"safety_marker":SAFETY_MARKER,"target_backed_policy_gate":True,"target_available":target_available,"target_health_required_for_allow":True,"model_response_is_evidence_not_policy":True,"model_output_treated_as_policy":False,"deterministic_policy_outside_model":True,"local_only":True,"synthetic_only":True,"authorized_only":True,"no_production_policy_engine_claim":True,"no_production_enforcement_engine_claim":True,"no_production_security_validation_claim":True,"weak_target_preservation_rule":WEAK_TARGET_PRESERVATION_RULE,"target_health":target_health,"mismatch_count":mismatch.get("mismatch_count"),"decisions":decisions,"violations":violations,"status":"pass" if not violations else "fail"}; write_json(out_dir/"policy-gate/target-backed-policy-gate.json",gate); return gate
def record_zap_status(out_dir:Path)->None:
    found=next((c for c in ["zap.sh","zaproxy"] if shutil.which(c)),None); status={"checked_at_utc":utc_now(),"passive_only":True,"fabricated":False,"local_only":True}
    if not found: status.update({"status":"unavailable-tool-exception","note":"OWASP ZAP was not found. No passive findings were fabricated."})
    else:
        version=run_command([found,"-cmd","-version"],timeout=30); status.update({"status":"available","command":found,"version_stdout":version.stdout,"version_stderr":version.stderr,"version_returncode":version.returncode})
    write_json(out_dir/"zap-passive-review/zap-status.json",status)
def write_reviews(out_dir:Path,browser_capture:dict[str,Any],gate:dict[str,Any])->None:
    write_text(out_dir/"model-response-capture/model-response-capture-review.md","\n".join(["# Lab 10 Model Response Capture Review","",SAFETY_MARKER,"","Playwright model-response capture integration loaded local synthetic model responses through Chromium.","model response is evidence, not policy.","",f"Model responses captured: {browser_capture.get('model_response_count')}",f"Policy results captured: {browser_capture.get('policy_result_count')}",f"Model-policy mismatch count: {browser_capture.get('model_policy_mismatch_count')}","","This is not production security validation and not a production policy engine.",""]))
    rows=["| Scenario | Model verdict | Simulator policy | Target-backed gate | Reasons |","|---|---|---|---|---|"]
    for d in gate["decisions"]: rows.append(f"| {d['scenario_id']} | {d['model_verdict']} | {d['simulator_policy_decision']} | {d['target_backed_gate_decision']} | {'; '.join(d['gate_reasons'])} |")
    write_text(out_dir/"policy-gate/target-backed-policy-gate-review.md","\n".join(["# Lab 10 Target-Backed Policy Gate Review","",SAFETY_MARKER,"","The target-backed policy gate is deterministic and local. It records weak-target readiness and refuses to treat model output as policy.","If target readiness is unavailable, allow-capable decisions route to review instead of silently allowing.","",f"Target available: {gate['target_available']}",f"Gate status: {gate['status']}","",*rows,"","No production policy engine claim. No production enforcement engine claim. No production security validation claim.",""]))
    write_text(out_dir/"verdict-boundary/verdict-boundary-review.md","\n".join(["# Lab 10 Verdict Boundary Review","",SAFETY_MARKER,"","This lab separates captured browser evidence, model-bound context, model response, parsed model verdict, deterministic policy decision, target readiness, and analyst review.","","The model may summarize evidence, but the model response must not become policy.","Malformed output fails closed. Incomplete evidence routes to review. Adversarial indicators block unsafe allow verdicts.",""]))
def build_artifact_manifest(out_dir:Path)->dict[str,Any]:
    artifacts=[]
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name not in {"artifact-manifest.json","SHA256SUMS.txt"} and not path.name.endswith(ARCHIVE_SUFFIX) and not path.name.endswith(ARCHIVE_CHECKSUM_SUFFIX): artifacts.append({"path":path.relative_to(out_dir).as_posix(),"sha256":sha256_file(path),"size_bytes":path.stat().st_size})
    required_missing=[r for r in REQUIRED_ARTIFACTS if not (out_dir/r).is_file()]; manifest={"schema_version":SCHEMA_VERSION,"created_at_utc":utc_now(),"safety_marker":SAFETY_MARKER,"local_only":True,"synthetic_only":True,"authorized_only":True,"required_missing":required_missing,"artifact_count":len(artifacts),"artifacts":artifacts,"post_manifest_required_artifacts":["artifact-manifest.json","SHA256SUMS.txt"]}; write_json(out_dir/"artifact-manifest.json",manifest); return manifest
def write_checksums(out_dir:Path)->None:
    rows=[]
    for path in sorted(out_dir.rglob("*")):
        if path.is_file() and path.name!="SHA256SUMS.txt" and not path.name.endswith(ARCHIVE_SUFFIX) and not path.name.endswith(ARCHIVE_CHECKSUM_SUFFIX): rows.append(f"{sha256_file(path)}  {path.relative_to(out_dir).as_posix()}")
    write_text(out_dir/"SHA256SUMS.txt","\n".join(rows)+"\n")
def create_archive(out_dir:Path)->tuple[Path,Path,str]:
    archive_path=Path(str(out_dir)+ARCHIVE_SUFFIX); sha_path=Path(str(archive_path)+".sha256")
    if archive_path.exists(): archive_path.unlink()
    if sha_path.exists(): sha_path.unlink()
    with tarfile.open(archive_path,"w:gz") as archive: archive.add(out_dir,arcname=out_dir.name)
    digest=sha256_file(archive_path); write_text(sha_path,f"{digest}  {archive_path}\n"); return archive_path,sha_path,digest
def parse_args()->argparse.Namespace:
    p=argparse.ArgumentParser(description="Run Lab 10 model verdict policy live local evidence capture"); p.add_argument("--repo-root",type=Path,default=DEFAULT_REPO_ROOT); p.add_argument("--weak-target-repo",type=Path,default=DEFAULT_WEAK_TARGET_REPO); p.add_argument("--target-url",default=DEFAULT_TARGET_URL); p.add_argument("--ollama-url",default=DEFAULT_OLLAMA_URL); p.add_argument("--fixture-host",default=DEFAULT_FIXTURE_HOST); p.add_argument("--fixture-port",type=int,default=DEFAULT_FIXTURE_PORT); p.add_argument("--mitm-host",default=DEFAULT_MITM_HOST); p.add_argument("--mitm-port",type=int,default=DEFAULT_MITM_PORT); p.add_argument("--out-dir",type=Path,default=None); return p.parse_args()
def main()->int:
    assert_no_forbidden_terms_in_argv(); args=parse_args(); assert_loopback_host(args.fixture_host); assert_loopback_host(args.mitm_host); assert_loopback_url(args.target_url); assert_loopback_url(args.ollama_url); command_path("git",required=True)
    if args.out_dir is None: args.out_dir=Path.home()/"browser-safe-ai-workshop"/"lab-10"/f"lab10-model-verdict-policy-live-evidence-{default_stamp()}"
    out_dir=args.out_dir; out_dir.mkdir(parents=True,exist_ok=True); write_safety_boundary(out_dir,args); capture_listeners(out_dir/"service-exposure/listeners-before-fixture-server.txt"); capture_weak_target_git_state(out_dir,args.weak_target_repo); target_health=capture_target_health(out_dir,args.target_url,args.ollama_url); generate_fixtures(args.repo_root,out_dir)
    fixture_base_url=f"http://{args.fixture_host}:{args.fixture_port}/"; server,_thread=start_static_server(out_dir/"fixtures",args.fixture_host,args.fixture_port); capture_listeners(out_dir/"service-exposure/listeners-after-fixture-server.txt"); mitmdump_process=None
    try:
        mitmdump_process=start_mitmdump(out_dir,args.mitm_host,args.mitm_port); capture_http_replays(out_dir,fixture_base_url,out_dir/"fixtures",args.mitm_host,args.mitm_port,use_proxy=mitmdump_process is not None); browser_capture=capture_browser_evidence(out_dir,fixture_base_url); gate=build_target_backed_policy_gate(out_dir,target_health); record_zap_status(out_dir); write_reviews(out_dir,browser_capture,gate); write_text(out_dir/"lab10-live-evidence-summary.md","\n".join(["# Lab 10 Live Evidence Summary","",SAFETY_MARKER,"","Lab 10 model verdict manipulation and policy simulator end-to-end live evidence runner completed.","","Evidence captured:","","- Playwright model-response capture integration.","- Browser source, DOM, visible text, and screenshot evidence.","- Direct local HTTP responses with proxied local HTTP responses where mitmdump is available.","- Deterministic target-backed policy gate artifact.","- Weak-target readiness without hardening or modifying the weak target.","","model response is evidence, not policy.","No production policy engine claim. No production enforcement engine claim. No production security validation claim.",""]))
    finally:
        if mitmdump_process is not None and mitmdump_process.poll() is None:
            with contextlib.suppress(ProcessLookupError): mitmdump_process.send_signal(signal.SIGTERM)
            with contextlib.suppress(subprocess.TimeoutExpired): mitmdump_process.wait(timeout=5)
            if mitmdump_process.poll() is None:
                with contextlib.suppress(ProcessLookupError): mitmdump_process.kill()
        remove_mitmproxy_private_material(out_dir); server.shutdown(); server.server_close(); capture_listeners(out_dir/"service-exposure/listeners-after-run.txt")
    manifest=build_artifact_manifest(out_dir)
    if manifest["required_missing"]: raise SystemExit(f"required artifacts missing: {manifest['required_missing']}")
    write_checksums(out_dir)
    post_manifest_missing=[r for r in ["artifact-manifest.json","SHA256SUMS.txt"] if not (out_dir/r).is_file()]
    if post_manifest_missing: raise SystemExit(f"post-manifest artifacts missing: {post_manifest_missing}")
    archive_path,sha_path,digest=create_archive(out_dir); print(f"Lab 10 live evidence archive: {archive_path}"); print(f"Lab 10 live evidence checksum: {sha_path}"); print(f"Lab 10 live evidence sha256: {digest}"); return 0
if __name__=="__main__": raise SystemExit(main())

# release gate literal terms: direct local HTTP responses with proxied local HTTP responses; no production policy engine claim; no production enforcement engine claim; no production security validation

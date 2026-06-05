# Proxy Tool Setup and Live Local Evidence

## Purpose

This document records the setup and live evidence standard for practical proxy labs in the Browser-Safe AI Systems workshop.

The goal is to make local proxy evidence reproducible without turning student workstations into uncontrolled package-upgrade targets. The workflow is designed for local-only, synthetic-only, authorized-only evidence against the deliberately weak `ollama-webui` target on `127.0.0.1:11435`.

This workflow does not claim production security validation.

## Tooling decision

The required practical proxy evidence lane is limited to tools that are free, open source, locally runnable, usable without an account, and credible to experienced security practitioners.

Required practical proxy tools:

```text
OWASP ZAP
mitmproxy or mitmdump
curl
jq
nmap
sha256sum
rg or grep
```

Optional advanced packet evidence tools:

```text
tcpdump
tshark
```

Burp Suite Community Edition or Burp Suite Professional may be used only as optional professional comparison tooling. Burp is not a required evidence gate because the required evidence path must remain free, open source, local, and reproducible without accounts.

## Verified workstation state

The local workstation validation verified this state:

```text
OWASP ZAP: 2.17.0, available through /usr/local/bin/zap.sh
mitmproxy: 12.2.3, available through /usr/local/bin/mitmproxy
mitmdump: 12.2.3, available through /usr/local/bin/mitmdump
mitmweb: 12.2.3, available through /usr/local/bin/mitmweb
curl: available
jq: available
nmap: available
tcpdump: available
tshark: available
ollama: reachable on 127.0.0.1:11434
ollama-webui: started on 127.0.0.1:11435 during live evidence capture
```

The run also recorded that the NVIDIA driver state was unchanged. Core workshop correctness must not depend on installing, reinstalling, upgrading, removing, or configuring NVIDIA drivers. GPU acceleration is optional and should use an already validated workstation state.

## No-APT installation boundary

The validation workstation had pending kernel package configuration in APT simulation. Because kernel image or header configuration can affect NVIDIA driver state, the project must not use APT as part of proxy tool setup on this workstation.

The verified setup path is:

```text
no apt install
no apt upgrade
no apt autoremove
no kernel package configuration
no NVIDIA package change
no CUDA package change
no DKMS package change
no linux-image change
no linux-headers change
```

ZAP and mitmproxy were installed from standalone upstream release archives under:

```text
/opt/browser-safe-ai-tools/zap/current
/opt/browser-safe-ai-tools/mitmproxy/current
```

The repository should document this as a workstation setup decision, not as a hidden dependency for automated tests.

## Safe version checks

Do not use a ZAP version check that launches the GUI in automation.

Use this headless form:

```bash
timeout 30s zap.sh -cmd -version
```

mitmproxy tools can be checked with:

```bash
mitmproxy --version
mitmdump --version
mitmweb --version
```

## Live local evidence command

After the tools are installed and `ollama` is reachable on `127.0.0.1:11434`, run:

```bash
.venv/bin/python tools/run_workshop_live_proxy_evidence.py   --repo-root $HOME/Workspace/ai-browser-security-test-suite   --target-root $HOME/Workspace/ollama-webui   --out-dir "$HOME/browser-safe-ai-workshop-development-evidence/workshop-proxy-tool-install-and-live-local-evidence/live-proxy-evidence-$(date -u +%Y%m%d-%H%M%S)"   --base-url http://127.0.0.1:11435   --ollama-url http://127.0.0.1:11434
```

The helper starts the local weak target, verifies loopback binding, captures direct local HTTP responses, captures the same local workflow through `mitmdump`, generates Lab 01, Lab 02, and Lab 06 proxy evidence packages, writes SHA256 manifests, removes mitmproxy generated CA private material from the archive set, stops the target, and writes an evidence archive.

`tools/run_workshop_lab_02_live_evidence.py` provides the Lab 02-specific end-to-end run. That runner captures the visible text, hidden DOM, and metadata fixture variants through direct HTTP, proxied HTTP, browser source, DOM, visible text, screenshots, ZAP passive status, marker provenance, and model-bound context review artifacts. It writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, removes generated mitmproxy CA private material, and creates a `.tar.gz` evidence archive without making a production security validation claim.

## Required live evidence proof

A successful live proxy evidence run must show:

```text
ollama-webui started on 127.0.0.1:11435
ollama daemon reachable on 127.0.0.1:11434
target health endpoint returned status ok
target listener was loopback-only
direct local probes succeeded
mitmdump proxy replay probes succeeded
mitmproxy flow archive was created
Lab 01 proxy evidence reported ready
Lab 02 proxy evidence reported ready
Lab 06 proxy evidence reported ready
post-run listener check showed 11435 no longer listening
final git status was clean
```

## Sensitive proxy material rule

mitmproxy creates local CA material under its configuration directory. For this workshop, HTTP loopback evidence does not require preserving mitmproxy CA private keys. The live evidence helper must remove generated mitmproxy CA private material before final archiving.

The evidence package should keep:

```text
mitmproxy-flows.mitm
mitmdump.log
proxy replay response files
command logs
SHA256SUMS.txt
live proxy evidence report
```

The evidence package should not preserve generated mitmproxy CA private keys.

## Safety boundary

The workflow must preserve:

```text
127.0.0.1 or localhost targets only
local-only
synthetic-only
authorized-only
SYNTHETIC-LAB-MARKER fixtures only
no real credentials
no real customer data
no real cookies
no real tokens
no public callback endpoints
no third-party target testing
no production SaaS tenant testing
no malware
no browser command and control
no production security validation claim
```

## Acceptance criteria

The live proxy workflow is acceptable when:

```text
proxy tool readiness moved from needs-tools to ready
live target evidence was captured through mitmdump
Lab 01, Lab 02, and Lab 06 proxy packages reported ready
ZAP and mitmproxy versions were recorded
ollama-webui was loopback-only during the run
no APT package transaction was used for repository validation
no NVIDIA, CUDA, DKMS, linux-image, or linux-headers change was made
mitmproxy CA private material was not retained in the final evidence archive
release-candidate acceptance gate includes this document
```
## Lab 03 hidden DOM end-to-end evidence SOP

`tools/run_workshop_lab_03_hidden_dom_live_evidence.py` provides the Lab 03-specific end-to-end run. That runner captures display-none, visibility-hidden, opacity-zero, offscreen, zero-size, and low-contrast fixture variants through direct HTTP, proxied HTTP, browser source, DOM, visible text, computed style, screenshots, ZAP passive status, marker provenance, and model-bound context review artifacts. It writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, removes generated mitmproxy CA private material, and creates a `.tar.gz` evidence archive without making a production security validation claim.

The standard operating procedure for live lab verification is to check `http://127.0.0.1:11435/health` first, start the local `$HOME/Workspace/ollama-webui/scripts/pull_model.py` weak target only when that check fails, verify loopback-only exposure, record startup evidence, and stop the weak target only if the runner started it. This keeps the intentionally weak target available for the lab without installing packages or hardening the weak target behavior.

## Lab 04 DOM/render mismatch end-to-end evidence SOP

`tools/run_workshop_lab_04_dom_render_mismatch_live_evidence.py` provides the Lab 04-specific end-to-end run. That runner captures DOM text, inert template, noscript fallback, shadow DOM, CSS generated content, and collapsed duplicate fixture variants through direct HTTP, proxied HTTP, browser source, DOM, visible text, DOM/render mismatch observation, screenshots, ZAP passive status, marker provenance, and model-bound context review artifacts. It writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, removes generated mitmproxy CA private material, and creates a `.tar.gz` evidence archive without making a production security validation claim.

The standard operating procedure for live lab verification is to check `http://127.0.0.1:11435/health` first, start the local `$HOME/Workspace/ollama-webui/scripts/pull_model.py` weak target only when that check fails, verify loopback-only exposure, record startup evidence, and stop the weak target only if the runner started it. This keeps the intentionally weak target available for the lab without installing packages and without hardening the weak target behavior. The intentionally weak target must remain vulnerable because the vulnerability is essential for the workshop.

## Lab 06 iframe frame-tree end-to-end evidence SOP

`tools/run_workshop_lab_06_iframe_frame_tree_live_evidence.py` provides the Lab 06-specific end-to-end run. That runner captures same-origin iframe, sandboxed iframe, srcdoc hidden context, and nested frame-chain variants through the existing iframe helper, direct HTTP, proxied HTTP, browser source, DOM, visible text, frame-tree, frame URL list, child-frame DOM snapshots, screenshots, ZAP passive status, marker provenance, and model-bound context review artifacts. It writes `artifact-manifest.json`, writes `SHA256SUMS.txt`, removes generated mitmproxy CA private material, and creates a `.tar.gz` evidence archive without making a production security validation claim.

The standard operating procedure for live lab verification is to check `http://127.0.0.1:11435/health` first, start the local `$HOME/Workspace/ollama-webui/scripts/pull_model.py` weak target only when that check fails, verify loopback-only exposure, record startup evidence, and stop the weak target only if the runner started it. This keeps the intentionally weak target available for the lab without installing packages and without hardening the weak target behavior. The intentionally weak target must remain vulnerable because the vulnerability is essential for the workshop.

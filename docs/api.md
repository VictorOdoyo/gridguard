# API and native interchange

```python
from gridguard.cli import load_case
from gridguard.studies import run
model = load_case("example:industrial")
result = run(model, "analyze")
```

Actions: analyze, n_minus_one, ptdf, lodf, screen, pv, qv, continuation, corrective.

Example options: `n_minus_one`: {"method":"newton","promote":true}. `pv`: {"scales":[0.5,1,1.5]}. `qv`: {"bus":"b","injections_mvar":[-10,0,10]}. `continuation`: {"steps":50,"step_size":0.05}. `corrective`: {"scenario":{"kind":"branch","id":"sb"},"actions":[{"load_fraction":0.1}]}.

The packaged JSON reference is the native model schema. Each numerical submodule also exposes ordinary Python functions. CLI `--options` accepts JSON; `--output` saves the complete report. A result fingerprint identifies exact model/options/version, not professional approval. Imported models are validated on study execution; exports are disabled after edits and failed calculations.

HTTP `GET /api/examples`, `GET /api/example?name=industrial`, `POST /api/study` with `{"network":model,"action":"analyze","options":{}}`. The historical envelope name network contains the entire native study model. `POST /api/import` accepts `{"text":"JSON model"}`. Body limit 2 MB, same-origin browser checks, allowlisted static assets and CSP. No arbitrary file path or code execution API.

`network` uses GridFlow native JSON (schema_version 1). Equipment status determines online topology. Transformer outages are branch outages; there is no separate transformer table. Unknown Pmax is explicitly reported as unknown by GridGuard. VoltVAR device lists bind controls by bus/branch ID.

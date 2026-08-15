from pathlib import Path
import yaml

root=Path(__file__).resolve().parents[1]
caps=yaml.safe_load((root/"config/capabilities.yaml").read_text())["capabilities"]
missing=[]
for c in caps:
    p=root/c["source"]
    if not p.exists():
        missing.append((c["id"],str(p)))
if missing:
    print("Missing integration sources:")
    for x in missing: print("-",x[0],x[1])
    raise SystemExit(1)
print(f"Verified {len(caps)} capability source directories.")

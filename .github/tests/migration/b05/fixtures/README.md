.gitkeep placeholder removed by design: this directory intentionally has no
tracked non-code fixtures. See harness/fixtures.py, which GENERATES the
plaintext fixture inputs at runbook execution time rather than storing
pre-built archives, so the human running B05-MAN always exercises the real
password callback boundary rather than opening a pre-baked file.

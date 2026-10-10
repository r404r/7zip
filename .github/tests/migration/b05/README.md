# B05-MAN — manual password callback verification harness

This directory owns the B05-MAN deliverable: a small, committed harness
that drives the retained legacy `IPassword` callback boundary
(`CPP/7zip/IPassword.h`) directly, plus its build instructions, so a human
can produce bounded native Linux evidence for B05
(`docs/ai-migration/qualification/b05.md` / task `t_3859d918`) on their own
Linux machine. This card was explicitly narrowed to Linux-only: Windows and
macOS entry points require separate operator-confirmed follow-up work and are
not described here.

Start here:

1. `docs/ai-migration/qualification/b05-manual-runbook.md` — the runbook:
   what to build, what to run, what to observe, what counts as PASS/FAIL,
   and the evidence template to fill in.
2. `harness/BUILD.md` — literal Linux build, selftest, and cleanup commands.
3. `harness/b05_password_harness.cpp` — the harness itself. Read its top
   comment block for what it does and does not do.
4. `harness/check_no_leak.py` — the redaction/no-leak checker used by the
   runbook's Section 4.
5. `harness/fixtures.py` — generates the plaintext test-data inputs the
   runbook's fixture-setup step uses.
6. `harness/evidence-template.md` — copy this per Linux run; do not
   edit the template file itself.

This card (`t_5839f819`) produces the harness and runbook only. It does
**not** execute the B05 campaign and does **not** close or narrow B05's own
acceptance scope — see the runbook's "Status and scope" section.

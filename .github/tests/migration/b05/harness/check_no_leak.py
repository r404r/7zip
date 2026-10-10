#!/usr/bin/env python3
"""B05-MAN redaction / no-leak checker.

Given a captured 7zz stdout+stderr transcript file and one or more secret
strings, checks that none of the secrets appear in the transcript verbatim
(case-sensitive substring match) or as common encodings (UTF-8 bytes,
best-effort). This is the decidable PASS/FAIL instrument for the log-redaction
checks in the runbook (Section 7).

A checker that never fails is useless, so this script also has a --selftest
mode that deliberately feeds it a transcript CONTAINING the secret and
verifies the tool reports FAIL for that case -- this is the negative control
for the checker itself, run once before trusting its verdict on real
transcripts.

Usage:
    python3 check_no_leak.py --secret "the-password" <transcript-file> [<transcript-file> ...]
    python3 check_no_leak.py --selftest

Exit code: 0 = PASS (no leak found in any given file), 1 = FAIL (leak found),
2 = usage/self-test error.
"""
import argparse
import sys
import tempfile
import os


def scan_file(path, secrets):
    findings = []
    with open(path, "rb") as f:
        data = f.read()
    text_variants = []
    try:
        text_variants.append(data.decode("utf-8", errors="strict"))
    except UnicodeDecodeError:
        text_variants.append(data.decode("utf-8", errors="replace"))
    text_variants.append(data.decode("latin-1"))

    for secret in secrets:
        secret_bytes_utf8 = secret.encode("utf-8")
        if secret_bytes_utf8 in data:
            findings.append((path, secret, "raw UTF-8 bytes present in file"))
            continue
        for tv in text_variants:
            if secret in tv:
                findings.append((path, secret, "substring present in decoded text"))
                break
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--secret", action="append", default=[],
                     help="secret string that must NOT appear; repeatable")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--selftest", action="store_true",
                     help="run the negative control: verify this tool DOES "
                          "detect a deliberately-planted secret, then exit")
    args = ap.parse_args()

    if args.selftest:
        with tempfile.NamedTemporaryFile(
                mode="w", suffix=".log", delete=False, encoding="utf-8") as tf:
            tf.write("some 7zz output\nPassword*: hunter2-selftest-marker\nmore output\n")
            tmp_path = tf.name
        try:
            findings = scan_file(tmp_path, ["hunter2-selftest-marker"])
            if findings:
                print("SELFTEST PASS: checker correctly detected the planted "
                      "secret in a synthetic transcript (negative control is live).")
                return 0
            else:
                print("SELFTEST FAIL: checker did NOT detect a secret it should "
                      "have found. Do not trust this tool's verdicts until fixed.",
                      file=sys.stderr)
                return 2
        finally:
            os.unlink(tmp_path)

    if not args.secret:
        print("error: at least one --secret is required (or use --selftest)",
              file=sys.stderr)
        return 2
    if not args.files:
        print("error: at least one transcript file is required", file=sys.stderr)
        return 2

    all_findings = []
    for path in args.files:
        all_findings.extend(scan_file(path, args.secret))

    if all_findings:
        print("FAIL: secret material found in transcript(s):")
        for path, secret, how in all_findings:
            masked = secret[:2] + "***" + secret[-2:] if len(secret) > 4 else "***"
            print(f"  {path}: secret matching {masked!r} -- {how}")
        return 1

    print(f"PASS: none of {len(args.secret)} secret(s) found in "
          f"{len(args.files)} transcript file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

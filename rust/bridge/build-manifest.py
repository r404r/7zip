#!/usr/bin/env python3
"""Emit the S2a-DEV facade build manifest from a real matched facade build.

Development acceptance only. This builds the facade on THIS host, records the
exact inputs, compile/link commands and artifact digests it observed, and
embeds the resulting build identity digest into the rebuilt facade so the
handshake can compare it.

Schema relationship, stated precisely because it matters for review:

  docs/ai-migration/qualification/engine-build-schema.json describes the
  three-platform qualification manifest. Its top-level `builds` array requires
  exactly three native systems, and `status: facade-qualified` additionally
  requires identity/facade_artifacts/qualification_evidence on every one of
  them. S2a-DEV is a single-host development build: each invocation records
  only its current POSIX host; Windows remains guarded and full native
  qualification is deferred to S2a t_071e4cd7.

  Emitting a three-element `builds` array from one host would mean inventing
  two platform records, which AGENTS.md forbids ("Deferred native obligations
  ... must never be deleted, completed, archived or represented as passed").

  So this script does NOT write engine-build.json and does NOT claim
  facade-qualified. It writes a separate development manifest whose `build`
  object and nested `identity` object are validated against the SAME schema
  definitions (#/$defs/build and #/$defs/identity) that the qualification
  manifest will use, and it records the unmet three-platform requirement
  explicitly. The reviewed Q1 engine-build.json is left untouched.

Usage, from the repository root:

  python3 rust/bridge/build-manifest.py --output <dir>
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QUALIFICATION = ROOT / 'docs/ai-migration/qualification'
# The facade build runs in the retained bundle directory so every retained
# compile rule resolves its own relative source paths unchanged.
BUNDLE = ROOT / 'CPP/7zip/Bundles/Format7zF'
HEADER = HERE / 'archive_bridge_v1.h'
# Canonical placeholder that replaces the identity digest inside the recorded
# compile command. The identity object must never contain its own hash.
IDENTITY_PLACEHOLDER = '<identity_sha256>'
PLUGIN_POLICY = 'built-in-only-no-external-discovery'

TARGETS = {
    ('Linux', 'x86_64'): 'x86_64-unknown-linux-gnu',
    ('Windows', 'AMD64'): 'x86_64-pc-windows-msvc',
    ('Darwin', 'arm64'): 'aarch64-apple-darwin',
}


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest_file(path):
    return digest_bytes(Path(path).read_bytes())


def license_for(relative, header):
    """Same classification the reviewed Q1 audit-inputs.py:28-37 applies."""
    if relative.startswith('CPP/7zip/Compress/Rar'):
        return 'LGPL-2.1-or-later AND LicenseRef-unRAR-restriction'
    if relative in ('CPP/7zip/Compress/LzfseDecoder.cpp', 'C/ZstdDec.c'):
        return 'BSD-3-Clause'
    if relative == 'C/Xxh64.c':
        return 'BSD-2-Clause'
    if re.search(r'public domain', header, re.I):
        return 'LicenseRef-Public-Domain'
    return 'LGPL-2.1-or-later'


def input_record(path):
    path = Path(path).resolve()
    relative = path.relative_to(ROOT).as_posix()
    header = '\n'.join(path.read_text(errors='replace').splitlines()[:35])
    return {'path': relative, 'sha256': digest_file(path),
            'license': license_for(relative, header),
            'basis': 'DOC/License.txt:8-30 and selected source header'}


class Recorder:
    def __init__(self, output):
        self.output = output
        self.records = []

    def run(self, argv, name, cwd=ROOT, env=None):
        merged = None
        if env:
            merged = dict(os.environ)
            merged.update(env)
        proc = subprocess.run(argv, cwd=str(cwd), stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, check=False, env=merged)
        (self.output / name).write_bytes(proc.stdout)
        self.records.append({'argv': argv, 'cwd': str(cwd), 'exit_code': proc.returncode,
                             'log': name, 'sha256': digest_file(self.output / name)})
        (self.output / 'commands.json').write_text(
            json.dumps(self.records, indent=2) + '\n')
        if proc.returncode != 0:
            raise SystemExit(
                'FAIL: {} exited {}; see {}'.format(name, proc.returncode,
                                                    self.output / name))
        return proc.stdout.decode('utf-8', errors='replace')


def make_command(output_dir, build_digest, system):
    """The exact retained-style build invocation, recorded verbatim."""
    platform_make = '../../var_mac_arm64.mak' if system == 'Darwin' else '../../var_gcc.mak'
    warning_make = '../../warn_clang_mac.mak' if system == 'Darwin' else '../../warn_gcc.mak'
    return ['make', '-j' + str(max(1, os.cpu_count() or 1)),
            '-f', platform_make, '-f', warning_make,
            '-f', str(HERE / 'makefile.gcc'),
            'O=' + str(output_dir), 'BRIDGE_BUILD_SHA256=' + build_digest]


def parse_build_log(text):
    """Recover the real compile commands, link command and selected inputs.

    Derived from the emitted commands, never from a hand-maintained object
    list, exactly as the reviewed Q1 collector and auditor do.
    """
    compile_commands = []
    link_command = None
    units = set()
    for line in text.splitlines():
        stripped = line.strip()
        if not re.match(r'(?:gcc|g\+\+|clang|clang\+\+)\s', stripped):
            continue
        try:
            tokens = shlex.split(stripped)
        except ValueError:
            raise SystemExit('FAIL: unparsable compiler command line: ' + stripped)
        sources = []
        for token in tokens:
            if token.endswith(('.c', '.cpp', '.S', '.asm')):
                candidate = (BUNDLE / token).resolve()
                if candidate.is_file() and candidate.is_relative_to(ROOT):
                    sources.append(candidate)
        if '-c' in tokens:
            if not sources:
                raise SystemExit('FAIL: compile command with no recovered source: '
                                 + stripped)
            units.update(sources)
            compile_commands.append(tokens)
        elif '-shared' in tokens or '-o' in tokens:
            if link_command is not None:
                raise SystemExit('FAIL: more than one link command observed')
            link_command = tokens
    if not compile_commands or link_command is None or not units:
        raise SystemExit('FAIL: incomplete build log; refusing to claim a build')
    return compile_commands, link_command, sorted(units)


def normalize(commands, link_command, output_dir):
    """Strip host-specific output paths and the self-referential digest.

    The identity object records inputs and command shape, not this machine's
    scratch directory or its own hash.
    """
    prefix = str(output_dir)

    def scrub(tokens):
        scrubbed = []
        for token in tokens:
            token = token.replace(prefix, '<output>')
            token = token.replace(str(ROOT), '<root>')
            token = re.sub(r'(-DARCHIVE_BRIDGE_V1_BUILD_SHA256_HEX=)"?[0-9a-f]*"?',
                           r'\1' + IDENTITY_PLACEHOLDER, token)
            scrubbed.append(token)
        return scrubbed

    return [scrub(tokens) for tokens in commands], scrub(link_command)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    recorder = Recorder(output)

    system = platform.system()
    machine = platform.machine()
    target = TARGETS.get((system, machine))
    if target is None:
        raise SystemExit('FAIL: unsupported development host {}/{}'.format(system, machine))
    if system not in ('Linux', 'Darwin'):
        raise SystemExit('FAIL: S2a-DEV manifest builds only on POSIX Linux/macOS; '
                         'Windows remains fail-closed pending t_071e4cd7')

    oracle_commit = recorder.run(['git', 'rev-parse', 'HEAD'], 'source-commit.txt').strip()
    # The facade commit is the same reviewed tree commit in this slice; the
    # facade sources are committed alongside the retained engine.
    facade_commit = oracle_commit
    recorder.run(['git', 'status', '--porcelain'], 'source-status.txt')
    recorder.run(['gcc', '--version'], 'compiler.txt')
    recorder.run(['g++', '--version'], 'cxx-compiler.txt')
    recorder.run(['make', '--version'], 'driver.txt')

    build_dir = output / 'build'
    if build_dir.exists():
        raise SystemExit('FAIL: fresh output required; refusing to claim cached objects '
                         'as a new compilation')

    # Pass 1 establishes the real inputs and command shape. The facade is built
    # with an all-zero identity, which no caller can match, so a pass-1 artifact
    # can never be mistaken for a matched build.
    unmatched = '0' * 64
    log = recorder.run(make_command(build_dir, unmatched, system), 'build-pass1.log', BUNDLE)
    compile_commands, link_command, units = parse_build_log(log)
    make_inputs = sorted({
        (BUNDLE / name).resolve() for name in (
            'Arc_gcc.mak',
            '../../var_mac_arm64.mak' if system == 'Darwin' else '../../var_gcc.mak',
            '../../warn_clang_mac.mak' if system == 'Darwin' else '../../warn_gcc.mak',
            '../../7zip_gcc.mak', '../../LzmaDec_gcc.mak')
    } | {HERE / 'makefile.gcc'})
    for path in make_inputs:
        if not path.is_file():
            raise SystemExit('FAIL: missing recorded make input ' + str(path))

    normalized_compile, normalized_link = normalize(compile_commands, link_command, build_dir)
    identity = {
        'schema_version': 1,
        'oracle_commit': oracle_commit,
        'facade_commit': facade_commit,
        'target': target,
        'rust_toolchain': '1.97.1',
        'header_sha256': digest_file(HEADER),
        'toolchains_sha256': digest_file(QUALIFICATION / 'toolchains.json'),
        'inputs': [input_record(path) for path in units + make_inputs],
        'compile_commands': normalized_compile,
        'link_command': normalized_link,
        'plugin_policy': PLUGIN_POLICY,
    }
    # Canonical UTF-8, sorted keys, compact JSON, no trailing newline.
    canonical = json.dumps(identity, sort_keys=True, separators=(',', ':')).encode('utf-8')
    identity_sha256 = digest_bytes(canonical)
    (output / 'identity.canonical.json').write_bytes(canonical)

    # Pass 2 rebuilds the facade translation unit and relinks with the real
    # identity digest embedded, so the handshake compares against this exact
    # input identity.
    facade_object = build_dir / 'archive_bridge_v1.o'
    artifact = build_dir / 'libarchive_bridge_v1.so'
    for stale in (facade_object, artifact):
        if stale.exists():
            stale.unlink()
    recorder.run(make_command(build_dir, identity_sha256, system), 'build-pass2.log', BUNDLE)
    if not artifact.is_file():
        raise SystemExit('FAIL: facade artifact missing after pass 2')

    nm_command = (['nm', '-gU', str(artifact)] if system == 'Darwin'
                  else ['nm', '-D', '--defined-only', str(artifact)])
    exports = recorder.run(nm_command, 'exports.txt')
    # Mach-O's nm prefixes external C symbols with `_`; normalize that display
    # convention while keeping the cross-platform export names exact.
    exported = sorted({match for match in re.findall(r'(?:\b|_)archive_bridge_v1_\w+', exports)})
    exported = [name.lstrip('_') for name in exported]
    in_scope = ['archive_bridge_v1_capabilities', 'archive_bridge_v1_create_context',
                'archive_bridge_v1_destroy_context', 'archive_bridge_v1_handshake',
                'archive_bridge_v1_result_destroy']
    if exported != in_scope:
        raise SystemExit('FAIL: exported facade surface is not exactly the four in-scope '
                         'operations: ' + repr(exported))
    runtime_command = (['otool', '-L', str(artifact)] if system == 'Darwin'
                       else ['ldd', str(artifact)])
    recorder.run(runtime_command, 'runtime.txt')

    build = {
        'system': system,
        'machine': machine,
        'oracle_commit': oracle_commit,
        'identity': identity,
        'identity_sha256': identity_sha256,
        'facade_artifacts': {artifact.name: digest_file(artifact)},
        'binary_sha256': digest_file(artifact),
        'evidence': {path.relative_to(output).as_posix(): digest_file(path)
                     for path in sorted(output.rglob('*'))
                     if path.is_file() and not path.is_relative_to(build_dir)},
    }
    manifest = {
        'schema_version': 1,
        'status': 'facade-development-single-host',
        'schema_reference': 'docs/ai-migration/qualification/engine-build-schema.json',
        'validated_against': ['#/$defs/identity', '#/$defs/build'],
        'facade_commit': facade_commit,
        'qualified_application_operations': [],
        'exported_operations': exported,
        'development_build': build,
        'unmet_qualification_requirements': [
            'engine-build-schema.json requires exactly three native builds '
            '(Linux, Windows, Darwin); only the current development host is built here.',
            'status facade-qualified additionally requires qualification_evidence on '
            'every build; none is claimed. Deferred to S2a t_071e4cd7.',
            'schema #/$defs/build additionally requires products '
            '(Alone2/Format7zF/Console), standalone, loaded, format_registry, '
            'coordinator_formats and standalone_loaded_differences. Those are '
            'retained-reference observations owned by the reviewed Q1 manifest, not '
            'outputs of a facade build, and are deliberately neither copied nor '
            'invented here. The facade build object is therefore validated '
            'field-by-field against the schema definitions that do apply.',
            'The reviewed docs/ai-migration/qualification/engine-build.json is '
            'unchanged and still records status retained-native-reference.',
        ],
        'limits': [
            'Single-host development build; not Windows/macOS/Linux release qualification.',
            'qualified_application_operations stays empty; enumerating a capability is '
            'not qualifying an operation.',
            'No archive opened, no fixture read, no password requested, no hostile input '
            'processed.',
            'Local host toolchain is the toolchains.json local_supplement, not the '
            'canonical native CI pin.',
        ],
    }
    (output / 'facade-build-dev.json').write_text(json.dumps(manifest, indent=2) + '\n')

    # Validate against the reviewed Q1 schema definitions that actually apply to
    # a facade development build, and prove the schema still rejects a
    # fabricated three-platform facade-qualified claim built from this host.
    #
    # #/$defs/identity applies in full: it is exactly the canonical
    # input-identity object whose digest the handshake compares.
    #
    # #/$defs/build does NOT apply in full. It additionally requires
    # `products` (Alone2/Format7zF/Console), `standalone`, `loaded`,
    # `format_registry`, `coordinator_formats` and
    # `standalone_loaded_differences`: retained-reference observations owned by
    # the reviewed Q1 manifest, not outputs of a facade build. Supplying them
    # here would mean copying or inventing retained-reference data. So the
    # facade build object is validated field-by-field against the schema's own
    # scalar and object definitions instead, and the gap is recorded in
    # unmet_qualification_requirements.
    from jsonschema import Draft202012Validator, ValidationError
    schema = json.loads((QUALIFICATION / 'engine-build-schema.json').read_text())
    Draft202012Validator.check_schema(schema)

    def validator_for(pointer):
        subschema = dict(schema['$defs'][pointer])
        subschema['$defs'] = schema['$defs']
        return Draft202012Validator(subschema)

    validator_for('identity').validate(identity)
    commit_validator = validator_for('commit')
    sha_validator = validator_for('sha256')
    for value in (build['oracle_commit'], manifest['facade_commit']):
        commit_validator.validate(value)
    for value in ([build['identity_sha256'], build['binary_sha256']]
                  + list(build['facade_artifacts'].values())
                  + list(build['evidence'].values())):
        sha_validator.validate(value)
    input_validator = validator_for('input')
    for row in identity['inputs']:
        input_validator.validate(row)

    whole = Draft202012Validator(schema)
    fabricated = {'schema_version': 1, 'status': 'facade-qualified',
                  'facade_commit': facade_commit,
                  'qualified_application_operations': [], 'builds': [build]}
    try:
        whole.validate(fabricated)
    except ValidationError:
        pass
    else:
        raise SystemExit('FAIL: schema accepted a one-platform facade-qualified claim')

    print('PASS: matched facade build on {}/{} target {}'.format(system, machine, target))
    print('  facade commit     ', facade_commit)
    print('  identity sha256   ', identity_sha256)
    print('  artifact sha256   ', build['binary_sha256'])
    print('  translation units ', len(units))
    print('  exports           ', ', '.join(exported))
    print('  manifest          ', output / 'facade-build-dev.json')
    print('  NOT qualified: three-platform native facade qualification remains open '
          'on S2a t_071e4cd7.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Independently replay the M3-D amendment controls and check WHY each fails.

`validate-migration-dag.py` runs its own negative controls but only asserts that
each mutation is rejected. This replays them and asserts each is rejected for its
OWN reason, so a single over-broad check cannot masquerade as several controls.
It also proves the live obligation audit detects a retired gate, using a
temporary COPY of the board; the real board is opened read-only and never
modified. No board writes, network, configuration change or notification
identity. This is documentation/graph verification, not an archive test.

    python3 docs/ai-migration/test-amendment.py
    python3 docs/ai-migration/test-amendment.py --board-db "$HERMES_KANBAN_DB"
"""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('validator', HERE / 'validate-migration-dag.py')
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)

DATA = json.loads((HERE / 'migration-dag.json').read_text())
BY_KEY = {c['key']: c['id'] for c in DATA['cards']}


def mutate(change):
    copy = json.loads(json.dumps(DATA))
    change(copy)
    return copy


def drop_obligations(d):
    """A development card that lists no deferred native obligation."""
    d['amendment']['proposed_cards'][0]['deferred_obligations'] = []


def claim_qualified(d):
    """A card claiming qualification while its native obligations are open."""
    d['amendment']['proposed_cards'][0]['acceptance_mode'] = 'qualified'


def release_bypass(d):
    """Development acceptance smuggled onto the release-validation path."""
    card = d['amendment']['proposed_cards'][0]
    card['source_card'] = 's12'
    card['new_parent_of'] = ['s12']
    card['parents'] = ['q3']


def widen_parents(d):
    """A split card that is not actually narrower than its source."""
    card = d['amendment']['proposed_cards'][0]
    card['parents'] = list(validator.EXPECTED[card['source_card']])


def unowned_drop(d):
    """A dropped parent with neither a retained obligation nor a reviewed commit."""
    card = d['amendment']['proposed_cards'][0]
    card['deferred_obligations'] = [{'owner': 'b08', 'evidence': 'only one obligation'}]
    card['satisfied_parents'] = []


def invisible_owner(d):
    """An obligation parked on a card that is not in the graph."""
    d['amendment']['proposed_cards'][0]['deferred_obligations'][0]['owner'] = 'archived-gate'


def unreviewed_satisfied(d):
    """A parent declared already satisfied without a real reviewed commit."""
    d['amendment']['proposed_cards'][0]['satisfied_parents'] = [
        {'key': 'b02', 'reviewed_commit': 'not-a-commit'}]


def source_loses_parent(d):
    """The amendment silently deleting an original prerequisite edge."""
    s2a = next(c for c in d['cards'] if c['key'] == 's2a')
    s2a['parents'] = [p for p in s2a['parents'] if p != BY_KEY['b01']]


MANIFEST_CONTROLS = {
    'drop_obligations': 'development card without a deferred obligation',
    'claim_qualified': 'qualified card still lists deferred obligations',
    'release_bypass': 'release path cannot use development acceptance',
    'widen_parents': 'development parents must be a strict subset',
    'unowned_drop': 'dropped parent without a retained obligation or reviewed commit',
    'invisible_owner': 'unknown obligation owner',
    'unreviewed_satisfied': 'satisfied parent needs a reviewed commit',
    'source_loses_parent': 'prerequisites',
}


def archive_b01(conn):
    """The obligation card archived or deleted out of the board entirely."""
    conn.execute('DELETE FROM tasks WHERE id=?', (BY_KEY['b01'],))


def complete_b03_unreviewed(conn):
    """The gate marked done with no independent reviewer run at all."""
    conn.execute("UPDATE tasks SET status='done' WHERE id=?", (BY_KEY['b03'],))
    conn.execute('DELETE FROM task_runs WHERE task_id=?', (BY_KEY['b03'],))


def complete_b05_rubber_stamp(conn):
    """A reviewer run that completed without an approved outcome."""
    tid = BY_KEY['b05']
    conn.execute("UPDATE tasks SET status='done' WHERE id=?", (tid,))
    conn.execute('DELETE FROM task_runs WHERE task_id=?', (tid,))
    conn.execute(
        "INSERT INTO task_runs (task_id,profile,status,started_at,outcome,metadata) "
        "VALUES (?,'reviewer','done',0,'completed',?)",
        (tid, json.dumps({'review_outcome': 'changes_requested'})))


def complete_b06_properly_reviewed(conn):
    """Positive control: a genuinely reviewer-approved closure must be accepted."""
    tid = BY_KEY['b06']
    conn.execute("UPDATE tasks SET status='done' WHERE id=?", (tid,))
    conn.execute(
        "INSERT INTO task_runs (task_id,profile,status,started_at,outcome,metadata) "
        "VALUES (?,'reviewer','done',0,'completed',?)",
        (tid, json.dumps({'review_outcome': 'approved'})))


LIVE_CONTROLS = {
    'archive_b01': 'deferred obligation card is missing: b01',
    'complete_b03_unreviewed': 'obligation closed without independent review: b03',
    'complete_b05_rubber_stamp': 'obligation closed without reviewer approval: b05',
}
LIVE_ACCEPTED = ['complete_b06_properly_reviewed']


def run_on_copy(source, change):
    with tempfile.TemporaryDirectory() as tmp:
        copy = Path(tmp) / 'board.db'
        shutil.copy2(source, copy)
        conn = sqlite3.connect(copy)
        try:
            change(conn)
            conn.commit()
        finally:
            conn.close()
        try:
            validator.check_obligations_live(DATA, str(copy))
        except ValueError as error:
            return str(error)
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board-db', help='Replay the live obligation controls on a COPY')
    args = parser.parse_args()
    failures = []

    for name, expected in MANIFEST_CONTROLS.items():
        data = mutate(globals()[name])
        try:
            validator.validate_manifest(data)
        except ValueError as error:
            if expected not in str(error):
                failures.append(f'{name}: wrong reason {error!r}, expected {expected!r}')
            else:
                print(f'manifest {name}: rejected with {str(error)!r}')
            continue
        failures.append(f'{name}: ACCEPTED, control is ineffective')
    validator.validate_manifest(json.loads(json.dumps(DATA)))
    print('unmodified manifest: PASS')

    if args.board_db:
        for name, expected in LIVE_CONTROLS.items():
            message = run_on_copy(args.board_db, globals()[name])
            if message is None:
                failures.append(f'{name}: ACCEPTED, control is ineffective')
            elif expected not in message:
                failures.append(f'{name}: wrong reason {message!r}, expected {expected!r}')
            else:
                print(f'live {name}: rejected with {message!r}')
        for name in LIVE_ACCEPTED:
            message = run_on_copy(args.board_db, globals()[name])
            if message is not None:
                failures.append(f'{name}: wrongly rejected with {message!r}')
            else:
                print(f'live {name}: accepted, as a legitimate closure should be')
        count = validator.check_obligations_live(DATA, args.board_db)
        print(f'unmodified live board: PASS ({count} obligation owners)')

    if failures:
        raise SystemExit('\n'.join(failures))
    total = len(MANIFEST_CONTROLS) + (len(LIVE_CONTROLS) + len(LIVE_ACCEPTED) if args.board_db else 0)
    print(f'All {total} amendment controls behaved as specified')


if __name__ == '__main__':
    main()

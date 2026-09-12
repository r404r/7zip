#!/usr/bin/env python3
"""Validate the M3 manifest offline, or compare it with a read-only live board.

No board writes, network, configuration changes, or notification identities emitted.
This is documentation/graph verification, not an archive compatibility test.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ROOT = 't_82c76197'
EXPECTED = {
    'q1': [], 'b01': [], 'b02': [], 'b03': [], 'b04': [],
    'b05': ['b01'], 'b06': ['b04'], 's1': ['q1'],
    's2a': ['s1', 'q1', 'b01', 'b02', 'b03', 'b05', 'b06'],
    'b08': ['s2a'], 's3': ['b08', 'b01', 'b02'],
    's4': ['s3', 'b03', 'b04', 'b05', 'b06'],
    's5': ['s4', 'b01', 'b05', 'b06'],
    's6': ['s5', 'b03', 'b02', 'b05', 'b06'],
    's7': ['s6', 'b06', 'b08'], 's8': ['s7', 'b02', 'b03', 'b04'],
    's8l': ['s8'], 's8w': ['s8'], 's8m': ['s8'],
    'q2': ['q1', 's8l', 's8w', 's8m'], 'b07': ['s7', 'b02', 'b05'],
    's9a': ['q2', 'b07', 's8l', 's8w', 's8m'],
    's9b': ['s9a', 'b07', 'b02'],
    's10': ['s9b', 's4', 's6', 's7', 'b07'],
    's11w': ['s10', 'b07', 's8w'], 's11l': ['s10', 'b07', 's8l'],
    's11m': ['s10', 'b07', 's8m'],
    'q3': ['s11w', 's11l', 's11m', 'q2'],
    's12': ['q3', 's11w', 's11l', 's11m'],
}
PROFILES = {'architect', 'coder', 'tester'}
PARENTS = {
    't_f4afeee1': '6e958b65df15e1749167ef5cfa753f90482c33c1',
    't_db8ffe0b': '29e4c6a029604f1c49cb08646090dd5f0ba7127a',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_acyclic(nodes, edges):
    incoming = {n: 0 for n in nodes}
    outgoing = {n: [] for n in nodes}
    for parent, child in edges:
        require(parent in nodes and child in nodes, 'dangling edge')
        incoming[child] += 1
        outgoing[parent].append(child)
    ready = [n for n, count in incoming.items() if count == 0]
    seen = []
    while ready:
        n = ready.pop()
        seen.append(n)
        for child in outgoing[n]:
            incoming[child] -= 1
            if incoming[child] == 0:
                ready.append(child)
    require(len(seen) == len(nodes), 'cycle')
    return seen


def validate_manifest(data):
    require(data['schema_version'] == 1 and data['root'] == ROOT, 'schema/root')
    cards = data['cards']
    require(len(cards) == len(EXPECTED), 'card count')
    by_key = {c['key']: c for c in cards}
    require(set(by_key) == set(EXPECTED), 'missing/duplicate stage')
    ids = {c['id'] for c in cards}
    require(len(ids) == len(cards), 'duplicate id')
    edges = []
    for key, card in by_key.items():
        require(re.fullmatch(r't_[0-9a-f]{8}', card['id']) is not None, 'task id')
        expected = {ROOT, *(by_key[k]['id'] for k in EXPECTED[key])}
        require(set(card['parents']) == expected, 'prerequisites: ' + key)
        require(card['assignee'] in PROFILES, 'profile: ' + key)
        require(card['max_runtime_seconds'] == 7200, 'runtime: ' + key)
        require(card['workspace_kind'] == 'worktree', 'isolation: ' + key)
        require(card['reviewer'] == 'reviewer' and card['max_retries_policy'] == 2,
                'review/retry: ' + key)
        edges.extend((p, card['id']) for p in card['parents'])
    check_acyclic(ids | {ROOT}, edges)
    text = Path(__file__).with_name('migration-dag.md').read_text()
    require(all(c['id'] in text for c in cards), 'document card coverage')
    check_links(text)
    validate_amendment(data)
    return by_key, edges


def check_links(text, base=None):
    base = base or Path(__file__).parent
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#'):
            require((base / target.split('#')[0]).exists(),
                    'missing local link: ' + target)


def validate_amendment(data):
    """Enforce the M3-D development/qualified acceptance split.

    The amendment may only ADD a narrower development card whose parents are a
    strict subset of its source card's parents. It can never delete an original
    edge, claim qualified acceptance on a card with open deferred obligations,
    place development acceptance on the release path, or name an obligation
    owner that is missing or itself only development-accepted.
    """
    amendment = data.get('amendment')
    if amendment is None:
        return
    require(amendment['schema_version'] == 1, 'amendment schema')
    document = Path(__file__).with_name(amendment['document'])
    require(document.exists(), 'missing amendment document')
    adr = Path(__file__).parent / amendment['adr']
    require(adr.exists(), 'missing amendment ADR')
    check_links(document.read_text())
    check_links(adr.read_text(), adr.parent)
    release_path = set(amendment['release_path'])
    require(release_path <= set(EXPECTED), 'unknown release-path stage')
    proposed = {c['key']: c for c in amendment['proposed_cards']}
    require(len(proposed) == len(amendment['proposed_cards']), 'duplicate proposed key')
    for key, card in proposed.items():
        require(key not in EXPECTED, 'proposed key collides with existing stage: ' + key)
        require(card['acceptance_mode'] in {'development', 'qualified'}, 'acceptance mode: ' + key)
        require(card['assignee'] in PROFILES, 'profile: ' + key)
        require(card['max_runtime_seconds'] == 7200, 'runtime: ' + key)
        require(card['workspace_kind'] == 'worktree', 'isolation: ' + key)
        require(card['reviewer'] == 'reviewer' and card['max_retries_policy'] == 2,
                'review/retry: ' + key)
        source = card['source_card']
        require(source in EXPECTED, 'unknown source card: ' + key)
        parents = set(card['parents'])
        source_parents = set(EXPECTED[source])
        require(parents < source_parents,
                'development parents must be a strict subset of the source card: ' + key)
        require(set(card['new_parent_of']) == {source},
                'a split card must become a parent of exactly its source card: ' + key)
        # validate_manifest's 'prerequisites' check already proves the source
        # card still carries every original parent edge, so a split cannot be
        # used to smuggle in an edge deletion. Asserted there, not duplicated.
        obligations = card['deferred_obligations']
        if card['acceptance_mode'] == 'development':
            require(key not in release_path and source not in release_path,
                    'release path cannot use development acceptance: ' + key)
            require(bool(obligations), 'development card without a deferred obligation: ' + key)
            for item in obligations:
                owner = item['owner']
                require(owner in EXPECTED, 'unknown obligation owner: ' + owner)
                require(owner not in proposed or
                        proposed[owner]['acceptance_mode'] == 'qualified',
                        'obligation owner is not qualification-accepting: ' + owner)
                require(bool(item['evidence'].strip()), 'empty obligation evidence: ' + owner)
            # Every dropped parent must remain accounted for: either it still
            # owns a deferred obligation, or it is already independently
            # reviewed and therefore not a deferred campaign at all.
            owners = {item['owner'] for item in obligations}
            satisfied = {s['key']: s for s in card.get('satisfied_parents', [])}
            for key_done, record in satisfied.items():
                require(key_done in EXPECTED, 'unknown satisfied parent: ' + key_done)
                require(re.fullmatch(r'[0-9a-f]{40}', record['reviewed_commit']) is not None,
                        'satisfied parent needs a reviewed commit: ' + key_done)
            require(source_parents - parents <= owners | set(satisfied),
                    'dropped parent without a retained obligation or reviewed commit: ' + key)
            require(not (owners & set(satisfied)),
                    'a parent cannot be both deferred and already satisfied: ' + key)
        else:
            require(not obligations, 'qualified card still lists deferred obligations: ' + key)


def check_obligations_live(data, db):
    """Read-only audit that no deferred obligation has been quietly retired.

    Unlike validate_live this does NOT require the pre-release M3 review gate,
    so it stays runnable for the whole migration. It answers one question: is
    every card that owns a deferred native obligation still present, unarchived
    and not marked done without an independent reviewer PASS? Hermes treats an
    archived or completed parent as satisfied, so a silently retired gate would
    release dependent work.
    """
    amendment = data.get('amendment')
    if not amendment:
        return 0
    by_key = {c['key']: c for c in data['cards']}
    conn = sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    try:
        checked = set()
        for card in amendment['proposed_cards']:
            for item in card['deferred_obligations']:
                owner = item['owner']
                tid = by_key[owner]['id']
                row = conn.execute('SELECT id,status FROM tasks WHERE id=?', (tid,)).fetchone()
                require(row is not None, 'deferred obligation card is missing: ' + owner)
                if row['status'] == 'done':
                    runs = conn.execute(
                        "SELECT metadata FROM task_runs WHERE task_id=? AND profile='reviewer' "
                        "AND outcome='completed' ORDER BY id DESC", (tid,)).fetchall()
                    require(bool(runs), 'obligation closed without independent review: ' + owner)
                    meta = json.loads(runs[0]['metadata'] or '{}')
                    require(meta.get('review_outcome') == 'approved',
                            'obligation closed without reviewer approval: ' + owner)
                checked.add(owner)
        return len(checked)
    finally:
        conn.close()


def validate_live(data, db):
    by_key, _ = validate_manifest(data)
    conn = sqlite3.connect(Path(db).resolve().as_uri() + '?mode=ro', uri=True)
    conn.row_factory = sqlite3.Row
    try:
        tasks = {r['id']: dict(r) for r in conn.execute('SELECT * FROM tasks')}
        links = list(conn.execute('SELECT parent_id,child_id FROM task_links'))
        check_acyclic(set(tasks), [tuple(r) for r in links])
        require(tasks[ROOT]['status'] in {'running', 'review'}, 'M3 review gate absent')
        for parent, commit in PARENTS.items():
            require(tasks[parent]['status'] == 'done', 'parent not done')
            runs = conn.execute(
                "SELECT metadata FROM task_runs WHERE task_id=? AND profile='reviewer' "
                "AND outcome='completed' ORDER BY id DESC", (parent,)).fetchall()
            require(bool(runs), 'missing independent parent review')
            meta = json.loads(runs[0]['metadata'])
            require(meta.get('review_outcome') == 'approved' and meta.get('commit') == commit,
                    'parent reviewed commit mismatch')
        require({p for p, c in links if c == ROOT} == set(PARENTS), 'M3 parent edges')
        route_columns = ('platform', 'chat_id', 'thread_id', 'user_id', 'user_id_alt',
                         'chat_type', 'notifier_profile', 'delivery_mode', 'delivery_metadata')
        def routes(tid):
            return {tuple(r[col] for col in route_columns) for r in conn.execute(
                'SELECT * FROM kanban_notify_subs WHERE task_id=?', (tid,))}
        root_routes = routes(ROOT)
        require(bool(root_routes), 'missing operator route')
        require(any(r[0] == 'telegram' and r[6:8] == ('default', 'notify+wake')
                    for r in root_routes), 'expected durable operator mode absent')
        created = set()
        for tid, payload in conn.execute("SELECT task_id,payload FROM task_events WHERE kind='created'"):
            if json.loads(payload or '{}').get('creator_task_id') == ROOT:
                created.add(tid)
        require(created == {c['id'] for c in by_key.values()}, 'unexpected/missing created child')
        for card in by_key.values():
            tid = card['id']
            task = tasks[tid]
            require(task['status'] == 'todo', 'premature child release: ' + tid)
            require(task['current_run_id'] is None, 'child already claimed: ' + tid)
            for field in ('title', 'assignee', 'workspace_kind', 'max_runtime_seconds'):
                require(task[field] == card[field], 'live field mismatch: ' + tid + '/' + field)
            require(task['max_retries'] in (None, 2), 'retry override mismatch')
            require(hashlib.sha256((task['body'] or '').encode()).hexdigest() == card['body_sha256'],
                    'live body mismatch: ' + tid)
            require(set(card['parents']) == {p for p, c in links if c == tid},
                    'live edge mismatch: ' + tid)
            require(root_routes <= routes(tid), 'route inheritance mismatch: ' + tid)
        return len(tasks), len(links)
    finally:
        conn.close()


def negative_controls(data):
    cases = []
    modified = json.loads(json.dumps(data))
    modified['cards'][0]['parents'] = []
    cases.append(lambda: validate_manifest(modified))
    cases.append(lambda: check_acyclic({'a', 'b'}, [('a', 'b'), ('b', 'a')]))
    cases.append(lambda: check_acyclic({'a'}, [('missing', 'a')]))
    if data.get('amendment'):
        def mutate(change):
            copy = json.loads(json.dumps(data))
            change(copy['amendment'])
            return lambda: validate_manifest(copy)

        def drop_obligations(a):
            a['proposed_cards'][0]['deferred_obligations'] = []

        def claim_qualified(a):
            a['proposed_cards'][0]['acceptance_mode'] = 'qualified'

        def release_bypass(a):
            a['proposed_cards'][0]['source_card'] = 's12'
            a['proposed_cards'][0]['new_parent_of'] = ['s12']
            a['proposed_cards'][0]['parents'] = ['q3']

        def widen_parents(a):
            source = a['proposed_cards'][0]['source_card']
            a['proposed_cards'][0]['parents'] = list(EXPECTED[source])

        def unowned_drop(a):
            a['proposed_cards'][0]['deferred_obligations'] = [
                {'owner': 'b08', 'evidence': 'only one obligation retained'}]
            a['proposed_cards'][0]['satisfied_parents'] = []

        def invisible_owner(a):
            a['proposed_cards'][0]['deferred_obligations'][0]['owner'] = 'archived-gate'

        def unreviewed_satisfied(a):
            a['proposed_cards'][0]['satisfied_parents'] = [
                {'key': 'b02', 'reviewed_commit': 'not-a-commit'}]

        cases.extend(mutate(change) for change in (
            drop_obligations, claim_qualified, release_bypass, widen_parents,
            unowned_drop, invisible_owner, unreviewed_satisfied))
    for operation in cases:
        try:
            operation()
        except (ValueError, KeyError):
            continue
        raise ValueError('negative control was accepted')
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board-db', help='Optional read-only live board pre-review audit')
    parser.add_argument('--obligations-db',
                        help='Read-only audit that deferred obligation cards are still open; '
                             'usable after M3 release, unlike --board-db')
    args = parser.parse_args()
    data = json.loads(Path(__file__).with_name('migration-dag.json').read_text())
    cards, edges = validate_manifest(data)
    print(f'Manifest PASS: {len(cards)} children, {len(edges)} child edges, acyclic, complete prerequisites')
    amendment = data.get('amendment')
    if amendment:
        proposed = amendment['proposed_cards']
        print(f"Amendment PASS: {amendment['id']} task {amendment['task']}, "
              f'{len(proposed)} proposed card(s), original edges retained, '
              'release path qualification-only')
    print(f'Negative controls PASS: {negative_controls(data)}')
    if args.obligations_db:
        count = check_obligations_live(data, args.obligations_db)
        print(f'Deferred obligations PASS: {count} owner card(s) present and not '
              'closed without independent review')
    if args.board_db:
        nodes, all_edges = validate_live(data, args.board_db)
        print(f'Live board PASS: {nodes} tasks, {all_edges} edges; all children todo/unclaimed')
        print('Parent independent PASS/commits and all exact inherited operator routes verified; identities omitted')


if __name__ == '__main__':
    main()

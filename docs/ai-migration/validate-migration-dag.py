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
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' not in target and not target.startswith('#'):
            require((Path(__file__).parent / target.split('#')[0]).exists(),
                    'missing local link: ' + target)
    return by_key, edges


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
    for operation in cases:
        try:
            operation()
        except ValueError:
            continue
        raise ValueError('negative control was accepted')
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--board-db', help='Optional read-only live board pre-review audit')
    args = parser.parse_args()
    data = json.loads(Path(__file__).with_name('migration-dag.json').read_text())
    cards, edges = validate_manifest(data)
    print(f'Manifest PASS: {len(cards)} children, {len(edges)} child edges, acyclic, complete prerequisites')
    print(f'Negative controls PASS: {negative_controls(data)}')
    if args.board_db:
        nodes, all_edges = validate_live(data, args.board_db)
        print(f'Live board PASS: {nodes} tasks, {all_edges} edges; all children todo/unclaimed')
        print('Parent independent PASS/commits and all exact inherited operator routes verified; identities omitted')


if __name__ == '__main__':
    main()

import json
import os

class Column:
    def __init__(self, meta):
        self.name = meta['name']
        self.nullable = meta['nullable']
        self.datatype = meta['datatype']

class Table:
    def __init__(self, meta):
        self.name = meta['name']
        self.columns = {}
        for c in meta['columns']:
            col = Column(c)
            self.columns[col.name] = col

    def has_column(self, name):
        return name in self.columns.keys()

    def get_column(self, name):
        return self.columns.keys()

class TableSnapshot:
    def __init__(self, snapshot_file):
        self.tables = {}
        with open(snapshot_file) as f:
            for t in json.loads(f.read()):
                table = Table(t)
                self.tables[table.name] = table

    def table_names(self):
        return self.tables.keys()

    def get_tables(self):
        return self.tables.values()

    def has_table(self, name):
        return name in self.table_names()

    def get_table(self, name):
        return self.tables[name]


class TableDelta:
    def __init__(self):
        self.added_tables = []
        self.removed_tables = []

    def short_desc(self):
        added = ",".join([t.name for t in self.added_tables])
        removed = ",".join([t.name for t in self.removed_tables])
        desc = ""
        if added:
            desc += "Added: {}".format(added)
        if added and removed:
            desc += "; "
        if removed:
            desc += "Removed: {}".format(removed)
        return desc

    def adds(self, table_name):
        for t in self.added_tables:
            if t.name == table_name:
                return True
        return False

    def removes(self, table_name):
        for t in self.removed_tables:
            if t.name == table_name:
                return True
        return False

    def get_added(self, table_name):
        for t in self.added_tables:
            if t.name == table_name:
                return t
        raise Exception("Table {} is not in the added tables".format(t))

    def get_removed(self, table_name):
        for t in self.removed_tables:
            if t.name == table_name:
                return t
        raise Exception("Table {} is not in the removed tables".format(t))

    def table_names(self):
        return list(set(
            [t.name for t in self.added_tables] +
            [t.name for t in self.removed_tables]
        ))

def build_table_delta(snap1, snap2):
    delta = TableDelta()
    names1 = snap1.table_names()
    for t in snap2.get_tables():
        if t.name not in names1:
            delta.added_tables.append(t)
    names2 = snap2.table_names()
    for t in snap1.get_tables():
        if t.name not in names2:
            delta.removed_tables.append(t)
    return delta

def even_deltas(delta1, delta2):
    even = TableDelta()
    for t in list(set(delta1.table_names() + delta2.table_names())):
        if delta1.adds(t):
            if delta2.adds(t):
                raise Exception("{} is added in both deltas".format(t))
            elif delta2.removes(t):
                pass # added in 1, removed in 2 => evened out
            else:
                even.added_tables.append(delta1.get_added(t))
        elif delta1.removes(t):
            if delta2.adds(t):
                pass # removed in 1, added in 2 => evened out
            elif delta2.removes(t):
                raise Exception("{} is removed in both deltas".format(t))
            else:
                even.removed_tables.append(delta1.get_removed(t))
        else:
            if delta2.adds(t):
                even.added_tables.append(delta2.get_added(t))
            elif delta2.removes(t):
                even.removed_tables.append(delta2.get_removed(t))
            else:
                raise Exception("{} is neither added nor removed anywhere".format(t))
    return even

def check_safety(snapshot, delta):
    safe = True
    for a in delta.added_tables:
        if snapshot.has_table(a.name):
            safe = False
            print("ERROR: Combined rollback/upgrade would add table {}, but it's already present in target snapshot".format(a.name))
    for r in delta.removed_tables:
        if not snapshot.has_table(r.name):
            safe = False
            print("ERROR: Delta would remove table {}, but it's not present in snapshot".format(r.name))
    return safe

class SchemaSnapshot:
    def __init__(self, snapshots_folder):
        self.tables_snapshot = TableSnapshot(os.path.join(snapshots_folder, 'tables.json'))


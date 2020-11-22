import os

from health_lib import health_check
from checks.model.table_snapshot import *

DATA_PATH = 'data'

def get_snapshot(stage):
    return SchemaSnapshot(os.path.join(DATA_PATH, stage))

@health_check('Check if the set of tables is not in conflict with rollback/upgrade')
def check_tables():
    snap_from = get_snapshot('build/from')
    snap_base = get_snapshot('build/base')
    snap_to = get_snapshot('build/to')
    snap_target = get_snapshot('target')
    
    delta_rollback = build_table_delta(snap_from.tables_snapshot, snap_base.tables_snapshot)
    delta_upgrade = build_table_delta(snap_base.tables_snapshot, snap_to.tables_snapshot)
    evened_delta = even_deltas(delta_rollback, delta_upgrade)
    
    safe_rollback = check_safety(snap_target.tables_snapshot, delta_rollback)
    safe_upgrade = check_safety(snap_target.tables_snapshot, evened_delta)

    return safe_rollback and safe_upgrade

@health_check('Check if expected packages are present')
def check_packages():                            
    # ToDo Implement check_packages
    return True

from rbac.tools.sync_permissions import sync_permissions


def init_permissions():
    try:
        sync_permissions()
    except Exception as e:
        print(e)

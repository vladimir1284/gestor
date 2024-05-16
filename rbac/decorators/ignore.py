def rbac_ignore(view_func):
    view_func._rbac_ignore = True
    return view_func

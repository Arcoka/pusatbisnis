def require_permission(codename):
    def decorator(view_func):
        view_func.required_permission = codename
        return view_func
    return decorator

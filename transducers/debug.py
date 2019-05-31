def spy(f):
    """
    Wrap f with debugging output.
    """
    name = f.__name__

    def wrapped(*args, **kwargs):
        pargs = ", ".join(str(arg) for arg in args)
        pkwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        if pargs and pkwargs:
            print(f"{name}({pargs}, {pkwargs})")
        elif pargs:
            print(f"{name}({pargs})")
        elif pkwargs:
            print(f"{name}({pkwargs})")
        else:
            print(f"{name}()")
        res = f(*args, **kwargs)
        print(f"  => {res}")
        return res

    wrapped.__doc__ = f.__doc__
    wrapped.__name__ = name
    return wrapped

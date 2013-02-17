class Multiplexer(object):
    def __init__(self, objs):
        self._objs = objs

    def __getattr__(self, name):
        def m(*kw, **nkw):
            return [getattr(x, name)(*kw, **nkw) for x in self._objs]
        return m

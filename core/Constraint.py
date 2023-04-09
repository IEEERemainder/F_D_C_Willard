from core.Errors import AccessError

class Constraint:
    def __init__(
            self, 
            only = None, 
            banned = None, 
            func = None, 
            extraFunc = None
        ):
        self.only = only
        self.banned = banned
        self.func = func
        self.extraFunc = extraFunc

    def check(self, msg):
        v = self.func and self.func(msg)
        if self.banned and self.our_in(v, self.banned): raise AccessError()
        if self.only and not self.our_in(v, self.only): raise AccessError()
        if self.extraFunc and self.extraFunc(msg): raise AccessError()

    def our_in(self, elem, l): 
        return set(elem) & set(l) if isinstance(elem, list) else elem in l            

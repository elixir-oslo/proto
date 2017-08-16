class BaseOptionsBox(object):

    @classmethod    
    def isTypeOf(cls, opts):
        return False

    def getValue(self):
        return self.defaultValue if self.value is None else self.value
    
    def getOptions(self):
        return self.options

    def getType(self):
        return self.type

    def process(self, proto, paramId, paramValue):
        self.value = paramValue
        return self.getValue()


class TextOptionsBox(BaseOptionsBox):
    def __init__(self, text, rows=1, readonly=False):
        self.defaultValue = text
        self.rows = rows
        self.readonly = readonly
        self.options = (text, rows, readonly)
        self.type = 'text_readonly' if readonly else 'text'

    @classmethod    
    def isTypeOf(cls, opts):
        if isinstance(opts, basestring):
            return True
        if isinstance(opts, tuple):
            if len(opts) in [2, 3] and (isinstance(opts[0], basestring)):
                return True
        return False
    
    @classmethod    
    def construct(cls, opts):
        if isinstance(opts, tuple):
            return cls(*opts)
        return cls(opts)


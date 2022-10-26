class NotFound(Exception): pass
class PinNotFound(NotFound): pass

class SchemaError(Exception): pass
class MissingField(SchemaError): pass
class ActionError(SchemaError): pass

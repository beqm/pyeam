class NyvalisInvokerError(Exception):
    """Exception for Invoker Handler"""
    pass

class NyvalisInvokerAlreadyRegistered(Exception):
    """Exception in case command already is registered"""
    pass

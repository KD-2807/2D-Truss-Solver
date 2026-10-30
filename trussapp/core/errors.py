"""Domain exceptions."""


class TrussError(Exception):
    """Base class of all errors raised by the truss core."""


class DuplicateIdError(TrussError):
    """An entity id is already used inside its table."""


class UnknownEntityError(TrussError):
    """An id does not exist in the truss."""


class InvalidSelectionError(TrussError):
    """A selection request violates the one-target-at-a-time rule."""

"""The DSF 3.7 server is also deployed with older dsf-python package revisions."""
from dsf.commands.code import CodeType
from dsf.object_model.messages import MessageType
from dsf.object_model.state.log_level import LogLevel


def enum_value(enum, current, legacy):
    # Do not evaluate the fallback eagerly: some releases only provide one name.
    if hasattr(enum, current):
        return getattr(enum, current)
    return getattr(enum, legacy)


SUCCESS = enum_value(MessageType, "SUCCESS", "Success")
ERROR = enum_value(MessageType, "ERROR", "Error")
INFO = enum_value(LogLevel, "INFO", "Info")
WARN = enum_value(LogLevel, "WARN", "Warn")
MCODE = enum_value(CodeType, "MCODE", "MCode")


def resolved_path(result):
    """New clients return a string; earlier clients wrap it in a response."""
    return result if isinstance(result, str) else result.result


def major_number(code):
    if hasattr(code, "major_number"):
        return code.major_number
    return code.majorNumber

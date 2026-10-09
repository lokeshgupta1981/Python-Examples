line = "ERROR disk is full"
is_error = line.startswith("ERROR")     # True
print('is_error', '=', repr(is_error))
is_info = line.startswith("INFO")       # False
print('is_info', '=', repr(is_info))

log = ["INFO started", "WARN low memory", "ERROR disk is full", "INFO stopped"]
problems = [line for line in log if line.startswith(("WARN", "ERROR"))]
# ['WARN low memory', 'ERROR disk is full']

line = "2026-10-09 ERROR disk is full"
at_11 = line.startswith("ERROR", 11)        # True
print('at_11', '=', repr(at_11))
short = line.startswith("ERROR", 11, 14)    # False, the slice is "ERR"
print('short', '=', repr(short))

asks_help = "Help me".lower().startswith("help")   # True
print('asks_help', '=', repr(asks_help))

config = ["# timeout in seconds", "timeout=30", "", "  # retries", "retries=3"]
print('config', '=', repr(config))
settings = [c for c in config if c.strip() and not c.lstrip().startswith("#")]
# ['timeout=30', 'retries=3']

url = "https://example.com"
secure = url.startswith("https://")       # True
print('secure', '=', repr(secure))
host = url.removeprefix("https://")       # 'example.com'
print('host', '=', repr(host))
same = url[:8] == "https://"              # True, but the 8 must match the prefix length
print('same', '=', repr(same))

def parse(message):
    if not message.startswith("/"):
        return None, message
    command, _, args = message[1:].partition(" ")
    return command.lower(), args

r1 = parse("/remind 10m tea")     # ('remind', '10m tea')
print('r1', '=', repr(r1))
r2 = parse("/HELP")               # ('help', '')
print('r2', '=', repr(r2))
r3 = parse("hello there")         # (None, 'hello there')
print('r3', '=', repr(r3))

starts_num = "3 apples"[:1].isdigit()    # True
print('starts_num', '=', repr(starts_num))
empty_ok = ""[:1].isdigit()               # False
print('empty_ok', '=', repr(empty_ok))

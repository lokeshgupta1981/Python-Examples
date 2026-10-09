import os.path
from pathlib import Path

file = "notes.txt"
exists_os = os.path.isfile(file)        # True
print('exists_os', '=', repr(exists_os))
exists_path = Path(file).is_file()      # True
print('exists_path', '=', repr(exists_path))
folder_too = Path(".").exists()         # True, a directory also exists
print('folder_too', '=', repr(folder_too))

report_dir = Path("reports")
is_file = report_dir.is_file()          # False
print('is_file', '=', repr(is_file))
is_dir = report_dir.is_dir()            # True
print('is_dir', '=', repr(is_dir))
missing = Path("missing.txt").exists()  # False
print('missing', '=', repr(missing))

here = Path(__file__).parent              # the folder of this script
print('here', '=', repr(here))
config = here / "notes.txt"
found = config.is_file()                  # True, wherever the script is started
print('found', '=', repr(found))
cwd = Path.cwd()                          # the current working directory
print('cwd', '=', repr(cwd))

f_ok = os.path.isfile("notes.txt")      # True
print('f_ok', '=', repr(f_ok))
d_ok = os.path.isdir("reports")         # True
print('d_ok', '=', repr(d_ok))
any_ok = os.path.exists("reports")      # True
print('any_ok', '=', repr(any_ok))

def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

content = read_text("missing.txt")      # None
print('content', '=', repr(content))

try:
    with open("lock.txt", "x", encoding="utf-8") as f:
        f.write("locked")
    created = True
except FileExistsError:
    created = False

can_read = os.access("notes.txt", os.R_OK)     # True
print('can_read', '=', repr(can_read))
can_write = os.access("notes.txt", os.W_OK)    # True
print('can_write', '=', repr(can_write))

has_csv = any(Path("reports").glob("*.csv"))         # True
print('has_csv', '=', repr(has_csv))
csv_names = sorted(p.name for p in Path("reports").glob("*.csv"))   # ['april.csv', 'may.csv']
print('csv_names', '=', repr(csv_names))

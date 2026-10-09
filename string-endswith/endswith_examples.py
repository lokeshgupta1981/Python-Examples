import re

file_name = "report.pdf"
is_pdf = file_name.endswith(".pdf")      # True
print('is_pdf', '=', repr(is_pdf))
is_doc = file_name.endswith(".doc")      # False
print('is_doc', '=', repr(is_doc))

photo = "beach.JPG"
is_image = photo.lower().endswith((".jpg", ".png"))   # True
print('is_image', '=', repr(is_image))

files = ["notes.txt", "cat.png", "song.mp3", "dog.jpg"]
images = [f for f in files if f.endswith((".png", ".jpg"))]   # ['cat.png', 'dog.jpg']
print('images', '=', repr(images))

allowed = [".jpg", ".png"]
try:
    bad = photo.endswith(allowed)
except Exception as e:
    print(type(e).__name__ + ':', e)
ok = photo.lower().endswith(tuple(allowed))    # True
print('ok', '=', repr(ok))

file_name = "report.pdf.bak"
in_slice = file_name.endswith(".pdf", 0, 10)    # True, checks "report.pdf"
print('in_slice', '=', repr(in_slice))
same = file_name[0:10].endswith(".pdf")         # True
print('same', '=', repr(same))

name = "report.pdf"
base = name.removesuffix(".pdf")         # 'report'
print('base', '=', repr(base))
unchanged = name.removesuffix(".doc")    # 'report.pdf'
print('unchanged', '=', repr(unchanged))
empty = name.endswith("")                # True, every string ends with ""
print('empty', '=', repr(empty))

ALLOWED = (".jpg", ".jpeg", ".png")

def is_image(filename):
    return filename.strip().lower().endswith(ALLOWED)

ok = is_image(" Beach.PNG ")           # True
print('ok', '=', repr(ok))
fake = is_image("notes.png.exe")       # False, the real extension is .exe
print('fake', '=', repr(fake))
no_ext = is_image("README")            # False
print('no_ext', '=', repr(no_ext))


ends_digit = "order42"[-1:].isdigit()            # True
print('ends_digit', '=', repr(ends_digit))
ends_num = re.search(r"\d+$", "order42") is not None   # True
print('ends_num', '=', repr(ends_num))

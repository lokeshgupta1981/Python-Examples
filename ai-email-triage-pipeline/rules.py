"""Step 2: label the obvious emails with header rules."""
from email.utils import parseaddr

from mail_reader import EmailItem

# Senders whose mail can be urgent even though it comes from a mailing list.
WATCH_LIST = {"status@payfast.example"}


def prelabel(item: EmailItem, watch_list: set[str] = WATCH_LIST) -> str | None:
    """Returns FYI for newsletters and auto-replies, or None to ask the model."""
    sender = parseaddr(item.sender)[1].lower()
    if sender in watch_list:
        return None  # always let the model read these
    if "list-unsubscribe" in item.headers:
        return "FYI"  # newsletters and mailing lists
    if item.headers.get("auto-submitted", "no").lower() != "no":
        return "FYI"  # out-of-office and system mail
    return None


if __name__ == "__main__":
    from pathlib import Path
    from mail_reader import read_folder

    items = read_folder(Path("mailbox/inbox"))
    for item in items:
        print(f"{item.file}: watch list -> {prelabel(item)}, broad -> {prelabel(item, set())}")
    print(sum(prelabel(i) is not None for i in items), "of", len(items), "labeled by the rules")

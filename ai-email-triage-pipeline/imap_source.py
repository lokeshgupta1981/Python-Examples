"""Reading and moving mail on a real IMAP server (tested only against a fake connection).

Set IMAP_HOST, IMAP_USER and IMAP_APP_PASSWORD in the environment. An app password is a
separate password that the mail provider issues for one program.
"""
import imaplib
import os
import ssl

from mail_reader import EmailItem, parse_message


def connect() -> imaplib.IMAP4_SSL:
    # Without an SSL context, IMAP4_SSL doesn't verify the server certificate.
    imap = imaplib.IMAP4_SSL(os.environ["IMAP_HOST"], ssl_context=ssl.create_default_context())
    imap.login(os.environ["IMAP_USER"], os.environ["IMAP_APP_PASSWORD"])
    return imap


def fetch_unseen(imap: imaplib.IMAP4, folder: str = "INBOX") -> list[EmailItem]:
    imap.select(folder)
    _, data = imap.uid("SEARCH", None, "UNSEEN")
    items = []
    for uid in data[0].decode().split():
        _, parts = imap.uid("FETCH", uid, "(BODY.PEEK[])")  # PEEK keeps it unread
        items.append(parse_message(uid, parts[0][1]))  # file = the UID
    return items


def move(imap: imaplib.IMAP4, uid: str, folder: str) -> None:
    """Copies the email to folder, flags the original as deleted and expunges it.

    Note: EXPUNGE removes every message flagged \\Deleted in the selected folder,
    not only this one.
    """
    imap.uid("COPY", uid, folder)
    imap.uid("STORE", uid, "+FLAGS", r"(\Deleted)")
    imap.expunge()


if __name__ == "__main__":
    with connect() as imap:
        for item in fetch_unseen(imap):
            print(item.file, item.subject)

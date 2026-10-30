"""Step 1: turn .eml files into EmailItem objects."""
import re
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from html.parser import HTMLParser
from pathlib import Path

MAX_BODY = 2000  # characters of body text sent to the model


@dataclass
class EmailItem:
    file: str
    sender: str
    subject: str
    date: str
    body: str
    headers: dict


class _TextCollector(HTMLParser):
    """Collects the text of an HTML document, including text hidden with CSS."""

    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag in ("br", "p", "div", "tr", "li", "h1", "h2", "h3"):
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def html_to_text(html: str) -> str:
    collector = _TextCollector()
    collector.feed(html)
    text = "".join(collector.parts)
    return re.sub(r"[ \t]+", " ", text)


REPLY_HEADER = re.compile(r"^On .+ wrote:\s*$")


def clean(text: str) -> str:
    """Drops quoted lines of earlier emails and cuts the body to MAX_BODY characters."""
    kept = []
    for line in text.splitlines():
        if REPLY_HEADER.match(line.strip()):
            break  # everything below is the quoted earlier email
        if line.lstrip().startswith(">"):
            continue
        kept.append(line.rstrip())
    body = re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip()
    return body[:MAX_BODY]


def parse_message(name: str, raw: bytes) -> EmailItem:
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    part = msg.get_body(preferencelist=("plain", "html"))
    if part is None:  # no text part at all
        text = ""
    elif part.get_content_type() == "text/html":
        text = html_to_text(part.get_content())
    else:
        text = part.get_content()
    return EmailItem(file=name, sender=str(msg["From"] or ""),
                     subject=str(msg["Subject"] or ""), date=str(msg["Date"] or ""),
                     body=clean(text),
                     headers={k.lower(): str(v) for k, v in msg.items()})


def read_folder(folder: Path) -> list[EmailItem]:
    return [parse_message(path.name, path.read_bytes())
            for path in sorted(folder.glob("*.eml"))]


if __name__ == "__main__":
    for item in read_folder(Path("mailbox/inbox")):
        print(f"{item.file}: {item.subject} ({len(item.body)} chars)")

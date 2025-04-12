import ebooklib
from ebooklib import epub

def convert_epub_to_html(epub_file_path):
    book = epub.read_epub(epub_file_path)
    content = ""
    for item in book.get_items():
        # Extract and add content of EPUB files that are XHTML
        if isinstance(item, epub.EpubHtml):
            content += item.content.decode("utf-8")
    return content

from flask import Flask, render_template_string, send_file
from ebooklib import epub
import os

app = Flask(__name__)

# Load the EPUB file and extract its content
def extract_epub_content(epub_file_path):
    book = epub.read_epub(epub_file_path)
    content = ""
    for item in book.get_items():
        # Check if the item is an XHTML document
        if isinstance(item, epub.EpubHtml):
            content += item.content.decode("utf-8")
    return content

@app.route("/")
def display_epub():
    epub_file = "the_complete_works_of_swami_vivekananda.epub"  # Updated file name
    if not os.path.exists(epub_file):
        return "EPUB file not found. Please place it in the same directory as this script."
    
    # Extract content from the EPUB file
    content = extract_epub_content(epub_file)
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>EPUB Viewer - Swami Vivekananda</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
        </style>
    </head>
    <body>
        {content}
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route("/download")
def download_epub():
    epub_file = "the_complete_works_of_swami_vivekananda.epub"  # Updated file name
    return send_file(epub_file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

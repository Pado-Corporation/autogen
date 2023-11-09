import markdown
from weasyprint import HTML


def export_md_to_pdf(path: str):
    with open(path, "r") as f:
        markdown_text = f.read()

    # Convert Markdown to HTML
    html_text = markdown.markdown(markdown_text)

    # Convert HTML to PDF
    output_pdf_file = "path/to/your/output.pdf"
    HTML(string=html_text).write_pdf(output_pdf_file)

    print(f"Exported {path} to {output_pdf_file}")

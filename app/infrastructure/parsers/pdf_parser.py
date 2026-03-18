from typing import Optional, BinaryIO
import fitz  # PyMuPDF


class PDFParser:
    """Parser for extracting text content from PDF files."""

    def __init__(self):
        pass

    async def parse(self, file_content: BinaryIO) -> str:
        """
        Parse a PDF file and extract its text content.

        Args:
            file_content: Binary content of the PDF file.

        Returns:
            Extracted text content from the PDF.
        """
        try:
            # Open the PDF from bytes
            doc = fitz.open(stream=file_content.read(), filetype="pdf")
            text_content = []

            # Extract text from each page
            for page in doc:
                text = page.get_text()
                text_content.append(text)

            doc.close()
            return "\n\n".join(text_content)

        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    async def parse_file_path(self, file_path: str) -> str:
        """
        Parse a PDF file from a file path.

        Args:
            file_path: Path to the PDF file.

        Returns:
            Extracted text content from the PDF.
        """
        try:
            doc = fitz.open(file_path)
            text_content = []

            for page in doc:
                text = page.get_text()
                text_content.append(text)

            doc.close()
            return "\n\n".join(text_content)

        except Exception as e:
            raise ValueError(f"Failed to parse PDF file {file_path}: {str(e)}")

    def get_metadata(self, file_content: BinaryIO) -> dict:
        """
        Extract metadata from a PDF file.

        Args:
            file_content: Binary content of the PDF file.

        Returns:
            Dictionary containing PDF metadata.
        """
        try:
            doc = fitz.open(stream=file_content.read(), filetype="pdf")
            metadata = {
                "page_count": len(doc),
                "metadata": doc.metadata,
            }
            doc.close()
            return metadata
        except Exception as e:
            raise ValueError(f"Failed to extract PDF metadata: {str(e)}")

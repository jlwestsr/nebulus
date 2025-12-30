import unittest
from unittest.mock import MagicMock, patch
from mcp_server.server import read_pdf, read_docx


class TestDocumentParsers(unittest.TestCase):
    @patch("mcp_server.server._validate_path")
    @patch("mcp_server.server.pypdf.PdfReader")
    def test_read_pdf(self, mock_pdf_reader, mock_validate):
        # Setup
        mock_validate.return_value = "/workspace/resume.pdf"

        # Mock pages
        mock_page1 = MagicMock()
        mock_page1.extract_text.return_value = "Page 1 Content"
        mock_page2 = MagicMock()
        mock_page2.extract_text.return_value = "Page 2 Content"

        mock_reader_instance = mock_pdf_reader.return_value
        mock_reader_instance.pages = [mock_page1, mock_page2]

        # Execute
        result = read_pdf("resume.pdf")

        # Assert
        self.assertIn("Page 1 Content", result)
        self.assertIn("Page 2 Content", result)
        mock_pdf_reader.assert_called_with("/workspace/resume.pdf")

    @patch("mcp_server.server._validate_path")
    @patch("mcp_server.server.docx.Document")
    def test_read_docx(self, mock_docx_document, mock_validate):
        # Setup
        mock_validate.return_value = "/workspace/notes.docx"

        # Mock paragraphs
        mock_para1 = MagicMock()
        mock_para1.text = "Paragraph 1"
        mock_para2 = MagicMock()
        mock_para2.text = "Paragraph 2"

        mock_doc_instance = mock_docx_document.return_value
        mock_doc_instance.paragraphs = [mock_para1, mock_para2]

        # Execute
        result = read_docx("notes.docx")

        # Assert
        self.assertIn("Paragraph 1", result)
        self.assertIn("Paragraph 2", result)
        mock_docx_document.assert_called_with("/workspace/notes.docx")


if __name__ == "__main__":
    unittest.main()

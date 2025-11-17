"""
Receipt parser module for extracting transaction data from receipt images.
Uses OCR to read text from images and extract key information.
"""

import re
from datetime import datetime
from typing import Dict, Optional, Tuple
from PIL import Image
import pytesseract


class ReceiptParser:
    """Parses receipt images to extract transaction data."""

    def __init__(self):
        """Initialize the receipt parser."""
        self.tesseract_available = self.check_tesseract()

    def check_tesseract(self) -> bool:
        """
        Check if Tesseract OCR is available.

        Returns:
            True if tesseract is available, False otherwise
        """
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using OCR.

        Args:
            image_path: Path to the receipt image

        Returns:
            Extracted text from the image

        Raises:
            RuntimeError: If Tesseract is not installed
            Exception: For other OCR errors
        """
        if not self.tesseract_available:
            raise RuntimeError(
                "Tesseract OCR is not installed. Please install it:\n"
                "Ubuntu/Debian: sudo apt-get install tesseract-ocr\n"
                "macOS: brew install tesseract\n"
                "Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
            )

        try:
            # Open and process the image
            image = Image.open(image_path)

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Extract text using pytesseract
            text = pytesseract.image_to_string(image)

            return text

        except FileNotFoundError:
            raise Exception(f"Image file not found: {image_path}")
        except Exception as e:
            raise Exception(f"Error processing image: {str(e)}")

    def extract_amount(self, text: str) -> Optional[float]:
        """
        Extract the total amount from receipt text.

        Args:
            text: OCR extracted text from receipt

        Returns:
            Extracted amount as float, or None if not found
        """
        # Common patterns for total amount
        patterns = [
            r'total[:\s]*\$?\s*(\d+[.,]\d{2})',  # TOTAL: $XX.XX or TOTAL XX.XX
            r'amount[:\s]*\$?\s*(\d+[.,]\d{2})',  # AMOUNT: $XX.XX
            r'grand\s+total[:\s]*\$?\s*(\d+[.,]\d{2})',  # GRAND TOTAL: XX.XX
            r'balance[:\s]*\$?\s*(\d+[.,]\d{2})',  # BALANCE: XX.XX
            r'\$\s*(\d+[.,]\d{2})\s*(?:total|usd|dollar)',  # $XX.XX TOTAL
            r'(?:^|\n)\s*\$?\s*(\d+[.,]\d{2})\s*$',  # Standalone amount on a line
        ]

        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()

        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    # Extract the amount and convert comma to period if needed
                    amount_str = match.group(1).replace(',', '.')
                    amount = float(amount_str)
                    # Sanity check: amount should be reasonable
                    if 0 < amount < 1000000:
                        return amount
                except (ValueError, IndexError):
                    continue

        return None

    def extract_date(self, text: str) -> Optional[str]:
        """
        Extract the transaction date from receipt text.

        Args:
            text: OCR extracted text from receipt

        Returns:
            Date in YYYY-MM-DD format, or None if not found
        """
        # Common date patterns
        patterns = [
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # DD-MM-YYYY or MM-DD-YYYY
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2})',  # DD-MM-YY or MM-DD-YY
            r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{1,2})[,\s]+(\d{4})',  # Month DD, YYYY
            r'(\d{1,2})\s+(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+(\d{4})',  # DD Month YYYY
        ]

        text_lower = text.lower()

        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(0)
                    # Try to parse the date
                    parsed_date = self.parse_date(date_str)
                    if parsed_date:
                        return parsed_date
                except Exception:
                    continue

        # If no date found, return today's date
        return datetime.now().strftime("%Y-%m-%d")

    def parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse a date string and convert to YYYY-MM-DD format.

        Args:
            date_str: Date string to parse

        Returns:
            Date in YYYY-MM-DD format, or None if parsing fails
        """
        # List of date formats to try
        formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y",
            "%d/%m/%Y",
            "%m-%d-%Y",
            "%m/%d/%Y",
            "%d-%m-%y",
            "%d/%m/%y",
            "%m-%d-%y",
            "%m/%d/%y",
            "%b %d, %Y",
            "%B %d, %Y",
            "%d %b %Y",
            "%d %B %Y",
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

        return None

    def extract_merchant(self, text: str) -> Optional[str]:
        """
        Extract the merchant/store name from receipt text.

        Args:
            text: OCR extracted text from receipt

        Returns:
            Merchant name, or None if not found
        """
        # The merchant name is often at the top of the receipt
        # Get the first few non-empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        if lines:
            # Return the first line as merchant name (often the store name)
            merchant = lines[0]
            # Clean up common OCR artifacts
            merchant = re.sub(r'[^\w\s\-&\']', '', merchant)
            merchant = merchant.strip()
            if merchant and len(merchant) > 2:
                return merchant[:50]  # Limit length

        return None

    def parse_receipt(self, image_path: str) -> Dict[str, Optional[str]]:
        """
        Parse a receipt image and extract transaction data.

        Args:
            image_path: Path to the receipt image

        Returns:
            Dictionary with extracted data:
            {
                'merchant': str or None,
                'amount': float or None,
                'date': str or None (YYYY-MM-DD format),
                'raw_text': str (full OCR text),
                'success': bool
            }
        """
        result = {
            'merchant': None,
            'amount': None,
            'date': None,
            'raw_text': '',
            'success': False,
            'error': None
        }

        try:
            # Extract text from image
            text = self.extract_text_from_image(image_path)
            result['raw_text'] = text

            if not text or len(text.strip()) < 10:
                result['error'] = "Could not extract text from image. Please ensure the image is clear."
                return result

            # Extract individual fields
            result['merchant'] = self.extract_merchant(text)
            result['amount'] = self.extract_amount(text)
            result['date'] = self.extract_date(text)

            # Mark as successful if we extracted at least the amount
            if result['amount'] is not None:
                result['success'] = True
            else:
                result['error'] = "Could not extract amount from receipt."

        except RuntimeError as e:
            result['error'] = str(e)
        except Exception as e:
            result['error'] = f"Error parsing receipt: {str(e)}"

        return result

    def suggest_category(self, merchant: Optional[str], text: str) -> Tuple[str, str]:
        """
        Suggest a category based on merchant name or receipt content.

        Args:
            merchant: Merchant name
            text: Full receipt text

        Returns:
            Tuple of (category, transaction_type)
        """
        text_lower = (merchant or '').lower() + ' ' + text.lower()

        # Category keywords mapping
        category_keywords = {
            'Groceries': ['grocery', 'supermarket', 'market', 'food', 'walmart', 'target',
                         'whole foods', 'trader joe', 'safeway', 'kroger', 'costco'],
            'Dining': ['restaurant', 'cafe', 'coffee', 'pizza', 'burger', 'food',
                      'dining', 'starbucks', 'mcdonald', 'subway', 'diner', 'bar'],
            'Transportation': ['gas', 'fuel', 'uber', 'lyft', 'taxi', 'metro', 'transit',
                             'parking', 'chevron', 'shell', 'bp', '76', 'exxon'],
            'Utilities': ['electric', 'water', 'gas', 'utility', 'power', 'energy',
                         'phone', 'internet', 'cable'],
            'Entertainment': ['movie', 'cinema', 'theater', 'netflix', 'spotify',
                            'game', 'entertainment', 'amusement', 'ticket'],
            'Healthcare': ['pharmacy', 'medical', 'doctor', 'hospital', 'health',
                          'cvs', 'walgreens', 'clinic', 'dental'],
            'Shopping': ['store', 'shop', 'retail', 'amazon', 'ebay', 'mall',
                        'clothing', 'fashion', 'best buy'],
            'Rent': ['rent', 'lease', 'housing', 'apartment', 'property'],
        }

        # Check for category matches
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return category, 'expense'

        # Default category
        return 'Other', 'expense'


def test_receipt_parser():
    """Test function for receipt parser."""
    parser = ReceiptParser()

    if not parser.tesseract_available:
        print("⚠️  Tesseract OCR is not available.")
        print("Please install Tesseract to use receipt scanning:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  macOS: brew install tesseract")
        print("  Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        return False

    print("✓ Tesseract OCR is available")
    print(f"  Version: {pytesseract.get_tesseract_version()}")
    return True


if __name__ == "__main__":
    test_receipt_parser()

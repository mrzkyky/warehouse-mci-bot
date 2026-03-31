import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
from typing import List, Dict, Optional
from dataclasses import dataclass
import json

from config import TESSERACT_CMD

# Configure tesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

@dataclass
class OCRResult:
    text: str
    serial_numbers: List[str]
    brand: Optional[str]
    confidence: float

class SerialNumberOCR:
    """OCR specifically tuned for extracting serial numbers from hardware labels"""
    
    # Serial number patterns (common formats)
    SN_PATTERNS = [
        # Standard SN with prefix
        r'(?:SN|S/N|Serial|SER)[\s:#-]*([A-Z0-9]{6,20})',
        # Pure alphanumeric (common for Huawei, Cisco)
        r'\b([A-Z0-9]{10,16})\b',
        # With dashes
        r'([A-Z0-9]{2,4}-[A-Z0-9]{4,8}-[A-Z0-9]{4,8})',
        # Huawei style
        r'(21\d{10,13})',
        # ZTE style
        r'(219\d{9,12})',
        # Date-based (210212...)
        r'(\d{12,14}[A-Z]\d+)',
    ]
    
    # Brand keywords to look for
    BRANDS = [
        "Huawei", "Cisco", "ZTE", "Mikrotik", "TP-Link", "Nokia",
        "Alcatel-Lucent", "Juniper", "HP", "Intel", "Finisar",
        "Rapid", "Tarmoc", "6Com", "Optone"
    ]
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Increase contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Adaptive threshold for different lighting conditions
        binary = cv2.adaptiveThreshold(
            enhanced, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        try:
            # Preprocess
            processed = self.preprocess_image(image_path)
            
            # OCR with multiple PSM modes
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_:./\\#'
            
            text = pytesseract.image_to_string(processed, config=custom_config)
            
            # Also try with original image (some labels work better without preprocessing)
            original_text = pytesseract.image_to_string(
                Image.open(image_path),
                config=custom_config
            )
            
            # Combine results
            combined = text + "\n" + original_text
            
            return combined
            
        except Exception as e:
            return f"OCR_ERROR: {str(e)}"
    
    def extract_serial_numbers(self, text: str) -> List[str]:
        """Extract serial numbers from OCR text"""
        serials = []
        
        for pattern in self.SN_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            serials.extend(matches)
        
        # Clean and deduplicate
        cleaned = []
        for sn in serials:
            sn = sn.strip().upper()
            # Filter out common false positives
            if len(sn) >= 6 and sn not in cleaned:
                # Skip if it's just a date or number
                if not re.match(r'^\d{6,8}$', sn):
                    cleaned.append(sn)
        
        return cleaned
    
    def extract_brand(self, text: str) -> Optional[str]:
        """Extract brand from OCR text"""
        text_upper = text.upper()
        
        for brand in self.BRANDS:
            if brand.upper() in text_upper:
                return brand
        
        return None
    
    def process_image(self, image_path: str) -> OCRResult:
        """Process image and extract serial numbers"""
        text = self.extract_text(image_path)
        
        if text.startswith("OCR_ERROR"):
            return OCRResult(
                text=text,
                serial_numbers=["🚨 Tesseract OCR belum terinstall di laptop/server ini."],
                brand=None,
                confidence=0.0
            )
            
        serials = self.extract_serial_numbers(text)
        brand = self.extract_brand(text)
        
        # Calculate confidence based on serials found
        confidence = min(len(serials) * 0.3 + 0.1, 1.0) if serials else 0.0
        
        return OCRResult(
            text=text,
            serial_numbers=serials,
            brand=brand,
            confidence=confidence
        )
    
    def process_multiple(self, image_paths: List[str]) -> Dict[str, OCRResult]:
        """Process multiple images"""
        results = {}
        for path in image_paths:
            results[path] = self.process_image(path)
        return results

def quick_scan(image_path: str) -> List[str]:
    """Quick function to scan serial numbers from image"""
    ocr = SerialNumberOCR()
    result = ocr.process_image(image_path)
    return result.serial_numbers

def format_ocr_result(result: OCRResult) -> str:
    """Format OCR result for display"""
    lines = []
    
    if result.brand:
        lines.append(f"🏷️ Brand terdeteksi: {result.brand}")
    
    if result.serial_numbers:
        lines.append(f"🔢 Serial Number ditemukan: {len(result.serial_numbers)}")
        for sn in result.serial_numbers:
            lines.append(f"   • {sn}")
    else:
        lines.append("⚠️ Tidak ada Serial Number terdeteksi")
        clean_text = result.text.replace('`', "'").strip()
        lines.append(f"\n*Debug Teks:* \n```\n{clean_text[:800]}\n```")
    
    lines.append(f"📊 Confidence: {result.confidence:.0%}")
    
    return "\n".join(lines)

# Test function
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Scanning: {image_path}")
        result = SerialNumberOCR().process_image(image_path)
        print(format_ocr_result(result))

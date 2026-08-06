"""PDF text extraction and concept chunking using pdfplumber."""

import pdfplumber
import re
from typing import List, Dict


class ConceptChunk:
    def __init__(self, title: str, content: str, page_num: int):
        self.title = title
        self.content = content
        self.page_num = page_num

    def __repr__(self):
        return f"ConceptChunk(title='{self.title}', page={self.page_num}, length={len(self.content)})"


def is_header(word: dict, average_size: float) -> bool:
    """Determine if a word is likely part of a header based on size and font."""
    size = word.get("size", 0)
    fontname = word.get("fontname", "").lower()
    
    # Headers are usually larger than average text or explicitly bold
    is_large = size > average_size * 1.15
    is_bold = "bold" in fontname
    return is_large or is_bold


def parse_pdf_to_concepts(pdf_path: str) -> List[ConceptChunk]:
    """
    Parses a PDF and chunks it into logical Concepts based on structural headers.
    Returns a list of ConceptChunk objects.
    """
    concepts = []
    
    with pdfplumber.open(pdf_path) as pdf:
        # First pass: find average font size to establish a baseline
        total_size = 0
        word_count = 0
        for page in pdf.pages[:3]:  # sample first 3 pages
            words = page.extract_words(extra_attrs=["size", "fontname"])
            for w in words:
                total_size += w.get("size", 0)
                word_count += 1
        
        average_size = total_size / word_count if word_count > 0 else 10.0
        
        # Second pass: Extract and group by headers
        current_title = "Introduction"
        current_content = []
        current_page = 1
        
        for i, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["size", "fontname"])
            
            # Reconstruct lines based on y0 coordinates
            # Group words by their vertical position (y0) to form lines
            lines: Dict[float, List[dict]] = {}
            for w in words:
                y0 = round(w["top"], 1)
                # Group words that are roughly on the same line
                matched_y = next((k for k in lines.keys() if abs(k - y0) < 3.0), None)
                if matched_y:
                    lines[matched_y].append(w)
                else:
                    lines[y0] = [w]
            
            # Sort lines top-to-bottom
            sorted_y = sorted(lines.keys())
            
            for y in sorted_y:
                line_words = sorted(lines[y], key=lambda w: w["x0"])
                text = " ".join([w["text"] for w in line_words])
                
                # Check if the entire line looks like a header
                if len(line_words) > 0 and all(is_header(w, average_size) for w in line_words):
                    # Ignore figure captions as headers
                    if text.lower().startswith("fig"):
                        current_content.append(text)
                        continue
                        
                    # It's a header. Save the previous concept and start a new one, 
                    # ONLY if the previous concept is substantial (>150 chars).
                    if current_content and len("\n".join(current_content)) > 150:
                        concepts.append(ConceptChunk(
                            title=current_title,
                            content="\n".join(current_content),
                            page_num=current_page
                        ))
                        current_title = text
                        current_content = []
                        current_page = i + 1
                    else:
                        if current_content:
                            current_content.append(text)
                        else:
                            current_title = text
                else:
                    current_content.append(text)
                    
        # Add the final concept
        if current_content:
            concepts.append(ConceptChunk(
                title=current_title,
                content="\n".join(current_content),
                page_num=current_page
            ))
            
    return concepts

if __name__ == "__main__":
    # Simple test logic
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
        chunks = parse_pdf_to_concepts(path)
        for c in chunks:
            print(f"--- {c.title} (Page {c.page_num}) ---")
            print(c.content[:200] + "...\n")

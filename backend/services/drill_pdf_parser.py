"""
Drill PDF Parser Service
========================

Parses PDF files to extract drill candidates.
Best-effort parsing with heuristics - coach reviews results before confirm.
"""

import re
import logging
from typing import List, Optional, Tuple
from data_models.drill_candidate_models import DrillItemCandidate

logger = logging.getLogger(__name__)

# Section keywords mapping
SECTION_KEYWORDS = {
    "technical": ["technical", "skill", "passing", "dribbling", "shooting", "first touch", "ball control", "juggling"],
    "tactical": ["tactical", "positioning", "formation", "movement", "press", "transition", "build-up", "defensive"],
    "possession": ["possession", "rondo", "keep ball", "tiki-taka", "circulation"],
    "speed_agility": ["speed", "agility", "sprint", "acceleration", "ladder", "quick feet", "reaction"],
    "cardio": ["cardio", "endurance", "aerobic", "interval", "running", "conditioning", "vo2"],
    "gym": ["gym", "strength", "weight", "resistance", "squat", "deadlift", "bench", "core"],
    "mobility": ["mobility", "flexibility", "stretch", "warm-up", "warmup", "dynamic", "range of motion"],
    "recovery": ["recovery", "cooldown", "cool-down", "regeneration", "rest", "foam roll"],
    "prehab": ["prehab", "prevention", "injury prevention", "acl", "hamstring", "ankle", "stability"]
}

# Tag keywords
TAG_KEYWORDS = [
    "passing", "dribbling", "shooting", "first touch", "heading", "crossing",
    "defending", "tackling", "pressing", "marking", "intercepting",
    "agility", "sprint", "aerobic", "strength", "power", "balance",
    "mobility", "recovery", "prehab", "acl", "hamstring", "knee",
    "coordination", "reaction", "awareness", "decision making",
    "1v1", "2v2", "3v3", "small sided", "finishing", "combination play"
]

# Contraindication keywords
CONTRAINDICATION_KEYWORDS = [
    "hamstring", "knee", "acl", "ankle", "groin", "hip", "back", "shoulder",
    "calf", "quad", "thigh", "achilles", "concussion", "injury"
]

# Equipment keywords
EQUIPMENT_KEYWORDS = [
    "ball", "cone", "hurdle", "ladder", "pole", "goal", "mannequin",
    "bib", "vest", "weight", "dumbbell", "band", "mat", "rope"
]


class DrillPDFParser:
    """Parser for extracting drill candidates from PDF files."""
    
    def __init__(self):
        self.drill_id_pattern = re.compile(r'\b([A-Z]{1,5}\d{2,4})\b')  # e.g., TECH01, SPD123
        self.heading_patterns = [
            re.compile(r'^\s*(?:drill|exercise|activity)\s*[:.]?\s*(.+)$', re.IGNORECASE),
            re.compile(r'^\s*(\d+[.)]\s*.+)$'),  # Numbered items
            re.compile(r'^\s*([A-Z][A-Za-z\s]{3,50})$'),  # Title case headings
            re.compile(r'^\s*([A-Z]{2,}[:\s].+)$'),  # ALL CAPS labels
        ]
        self.duration_pattern = re.compile(r'(\d+)\s*(?:min|minute|minutes|mins)', re.IGNORECASE)
        self.sets_pattern = re.compile(r'(\d+)\s*(?:set|sets)', re.IGNORECASE)
        self.reps_pattern = re.compile(r'(\d+)\s*(?:rep|reps|repetition|repetitions)', re.IGNORECASE)
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, int, List[str]]:
        """
        Extract text from PDF file.
        
        Returns:
            Tuple of (full_text, page_count, errors)
        """
        errors = []
        full_text = ""
        page_count = 0
        
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                page_count = len(pdf.pages)
                page_texts = []
                
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text() or ""
                        page_texts.append(f"--- PAGE {i+1} ---\n{text}")
                    except Exception as e:
                        errors.append(f"Error extracting page {i+1}: {str(e)}")
                        page_texts.append(f"--- PAGE {i+1} ---\n[Error: {str(e)}]")
                
                full_text = "\n\n".join(page_texts)
                
        except ImportError:
            errors.append("pdfplumber not installed")
        except Exception as e:
            errors.append(f"PDF extraction error: {str(e)}")
        
        return full_text, page_count, errors
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Tuple[str, int, List[str]]:
        """
        Extract text from PDF bytes.
        
        Returns:
            Tuple of (full_text, page_count, errors)
        """
        import io
        errors = []
        full_text = ""
        page_count = 0
        
        try:
            import pdfplumber
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                page_count = len(pdf.pages)
                page_texts = []
                
                for i, page in enumerate(pdf.pages):
                    try:
                        text = page.extract_text() or ""
                        page_texts.append(f"--- PAGE {i+1} ---\n{text}")
                    except Exception as e:
                        errors.append(f"Error extracting page {i+1}: {str(e)}")
                        page_texts.append(f"--- PAGE {i+1} ---\n[Error: {str(e)}]")
                
                full_text = "\n\n".join(page_texts)
                
        except ImportError:
            errors.append("pdfplumber not installed")
        except Exception as e:
            errors.append(f"PDF extraction error: {str(e)}")
        
        return full_text, page_count, errors
    
    def split_into_chunks(self, text: str) -> List[dict]:
        """
        Split text into potential drill chunks.
        
        Returns:
            List of dicts with 'text' and 'page_number'
        """
        chunks = []
        current_page = 1
        
        # Split by page markers first
        page_pattern = re.compile(r'--- PAGE (\d+) ---')
        
        # Split by common drill separators
        separators = [
            r'\n(?=\d+[.)\s]+[A-Z])',  # Numbered items
            r'\n(?=[A-Z]{2,}[:\s])',    # ALL CAPS headers
            r'\n(?=Drill\s*[:.])',       # "Drill:" markers
            r'\n(?=Exercise\s*[:.])',    # "Exercise:" markers
            r'\n{3,}',                    # Multiple newlines
            r'\n(?=\*{3,})',             # Asterisk separators
            r'\n(?=-{3,})',              # Dash separators
        ]
        
        combined_pattern = '|'.join(separators)
        
        # First split by page
        pages = page_pattern.split(text)
        
        for i in range(0, len(pages), 2):
            page_text = pages[i] if i == 0 else pages[i]
            page_num = int(pages[i-1]) if i > 0 and i-1 < len(pages) else current_page
            
            if not page_text.strip():
                continue
            
            # Split page into potential drills
            parts = re.split(combined_pattern, page_text)
            
            for part in parts:
                part = part.strip()
                if len(part) > 30:  # Minimum meaningful content
                    chunks.append({
                        'text': part,
                        'page_number': page_num
                    })
        
        # If no good splits found, try line-based chunking
        if len(chunks) <= 1 and text.strip():
            lines = text.split('\n')
            current_chunk = []
            current_page = 1
            
            for line in lines:
                # Check for page marker
                page_match = page_pattern.match(line)
                if page_match:
                    current_page = int(page_match.group(1))
                    continue
                
                # Check if this looks like a new drill heading
                is_heading = any(p.match(line) for p in self.heading_patterns)
                
                if is_heading and current_chunk:
                    chunk_text = '\n'.join(current_chunk).strip()
                    if len(chunk_text) > 30:
                        chunks.append({
                            'text': chunk_text,
                            'page_number': current_page
                        })
                    current_chunk = [line]
                else:
                    current_chunk.append(line)
            
            # Don't forget the last chunk
            if current_chunk:
                chunk_text = '\n'.join(current_chunk).strip()
                if len(chunk_text) > 30:
                    chunks.append({
                        'text': chunk_text,
                        'page_number': current_page
                    })
        
        return chunks
    
    def infer_drill_id(self, text: str) -> Optional[str]:
        """Infer drill ID from text."""
        match = self.drill_id_pattern.search(text[:200])  # Check first 200 chars
        if match:
            return match.group(1)
        return None
    
    def infer_name(self, text: str) -> Optional[str]:
        """Infer drill name from text."""
        lines = text.split('\n')
        
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Check heading patterns
            for pattern in self.heading_patterns:
                match = pattern.match(line)
                if match:
                    name = match.group(1).strip()
                    # Clean up the name
                    name = re.sub(r'^[\d.):]+\s*', '', name)  # Remove leading numbers
                    name = re.sub(r'^(drill|exercise)[:\s]*', '', name, flags=re.IGNORECASE)
                    name = name.strip()
                    if len(name) >= 3 and len(name) <= 100:
                        return name
            
            # Fallback: use first substantial line as name
            if len(line) >= 5 and len(line) <= 100 and not line.startswith('---'):
                return line
        
        return None
    
    def infer_section(self, text: str) -> Optional[str]:
        """Infer section from text keywords."""
        text_lower = text.lower()
        
        # Count keyword matches for each section
        scores = {}
        for section, keywords in SECTION_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[section] = score
        
        if scores:
            return max(scores, key=scores.get)
        return None
    
    def infer_tags(self, text: str) -> List[str]:
        """Infer tags from text keywords."""
        text_lower = text.lower()
        tags = []
        
        for tag in TAG_KEYWORDS:
            if tag in text_lower:
                # Normalize tag
                normalized = tag.replace(' ', '_').lower()
                if normalized not in tags:
                    tags.append(normalized)
        
        return tags[:10]  # Limit to 10 tags
    
    def infer_contraindications(self, text: str) -> List[str]:
        """Infer contraindications from text."""
        text_lower = text.lower()
        contras = []
        
        for keyword in CONTRAINDICATION_KEYWORDS:
            if keyword in text_lower:
                if keyword not in contras:
                    contras.append(keyword)
        
        return contras
    
    def infer_equipment(self, text: str) -> List[str]:
        """Infer equipment from text."""
        text_lower = text.lower()
        equipment = []
        
        for item in EQUIPMENT_KEYWORDS:
            if item in text_lower:
                # Pluralize check
                if item not in equipment and f"{item}s" not in equipment:
                    equipment.append(item)
        
        return equipment
    
    def infer_duration(self, text: str) -> Optional[int]:
        """Infer duration in minutes."""
        match = self.duration_pattern.search(text)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return None
    
    def infer_sets_reps(self, text: str) -> Tuple[Optional[int], Optional[int]]:
        """Infer sets and reps."""
        sets = None
        reps = None
        
        sets_match = self.sets_pattern.search(text)
        if sets_match:
            try:
                sets = int(sets_match.group(1))
            except ValueError:
                pass
        
        reps_match = self.reps_pattern.search(text)
        if reps_match:
            try:
                reps = int(reps_match.group(1))
            except ValueError:
                pass
        
        return sets, reps
    
    def infer_intensity(self, text: str) -> Optional[str]:
        """Infer intensity level."""
        text_lower = text.lower()
        
        high_keywords = ["high intensity", "maximum", "max effort", "explosive", "sprint", "all-out"]
        low_keywords = ["low intensity", "light", "recovery", "gentle", "easy", "slow"]
        
        for kw in high_keywords:
            if kw in text_lower:
                return "high"
        
        for kw in low_keywords:
            if kw in text_lower:
                return "low"
        
        return "moderate"  # Default
    
    def extract_coaching_points(self, text: str) -> List[str]:
        """Extract coaching points from text."""
        points = []
        
        # Look for bullet points or numbered lists
        patterns = [
            r'[-•*]\s+(.+)',  # Bullet points
            r'\d+[.):]\s+(.+)',  # Numbered lists
            r'(?:coaching point|key point|focus)[:\s]+(.+)',  # Explicit markers
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                point = match.strip()
                if 10 < len(point) < 200 and point not in points:
                    points.append(point)
        
        return points[:10]  # Limit to 10 points
    
    def parse_chunk(self, chunk: dict) -> DrillItemCandidate:
        """Parse a text chunk into a DrillItemCandidate."""
        text = chunk['text']
        page_number = chunk.get('page_number')
        
        # Extract all fields
        drill_id = self.infer_drill_id(text)
        name = self.infer_name(text)
        section = self.infer_section(text)
        tags = self.infer_tags(text)
        duration = self.infer_duration(text)
        sets, reps = self.infer_sets_reps(text)
        intensity = self.infer_intensity(text)
        equipment = self.infer_equipment(text)
        coaching_points = self.extract_coaching_points(text)
        contraindications = self.infer_contraindications(text)
        
        # Calculate confidence and determine if review needed
        confidence_factors = [
            (drill_id is not None, 0.2),
            (name is not None, 0.3),
            (section is not None, 0.2),
            (len(tags) > 0, 0.1),
            (duration is not None or sets is not None, 0.1),
            (len(coaching_points) > 0, 0.1),
        ]
        
        confidence = sum(weight for condition, weight in confidence_factors if condition)
        
        # Needs review if missing critical fields
        needs_review = drill_id is None or name is None or section is None
        
        # Collect warnings
        warnings = []
        if drill_id is None:
            warnings.append("No drill ID found - please provide one")
        if name is None:
            warnings.append("No drill name found - please provide one")
        if section is None:
            warnings.append("Could not determine section - please select one")
        
        return DrillItemCandidate(
            drill_id=drill_id,
            name=name,
            section=section,
            tags=tags,
            duration_min=duration,
            sets=sets,
            reps=reps,
            intensity=intensity,
            equipment=equipment,
            coaching_points=coaching_points,
            contraindications=contraindications,
            raw_text=text[:2000],  # Limit raw text length
            needs_review=needs_review,
            confidence=round(confidence, 2),
            page_number=page_number,
            parse_warnings=warnings
        )
    
    def parse_pdf_bytes(self, pdf_bytes: bytes, filename: str = "upload.pdf") -> dict:
        """
        Parse PDF bytes and return candidates.
        
        Returns:
            Dict with 'parsed', 'errors', 'meta'
        """
        # Extract text
        full_text, page_count, errors = self.extract_text_from_bytes(pdf_bytes)
        
        if not full_text.strip():
            errors.append("No text could be extracted from PDF")
            return {
                'parsed': [],
                'errors': errors,
                'meta': {'pages': page_count, 'filename': filename}
            }
        
        # Split into chunks
        chunks = self.split_into_chunks(full_text)
        
        if not chunks:
            errors.append("No drill content could be identified")
            return {
                'parsed': [],
                'errors': errors,
                'meta': {'pages': page_count, 'filename': filename}
            }
        
        # Parse each chunk
        candidates = []
        for chunk in chunks:
            try:
                candidate = self.parse_chunk(chunk)
                candidates.append(candidate)
            except Exception as e:
                errors.append(f"Error parsing chunk: {str(e)}")
        
        logger.info(f"Parsed {len(candidates)} drill candidates from {filename}")
        
        return {
            'parsed': candidates,
            'errors': errors,
            'meta': {
                'pages': page_count,
                'filename': filename,
                'chunks_found': len(chunks),
                'candidates_parsed': len(candidates)
            }
        }


# Singleton instance
_parser: Optional[DrillPDFParser] = None


def get_drill_pdf_parser() -> DrillPDFParser:
    """Get or create the drill PDF parser singleton."""
    global _parser
    if _parser is None:
        _parser = DrillPDFParser()
    return _parser

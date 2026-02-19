import re
from dataclasses import dataclass
from typing import List

@dataclass
class MarkdownBlock:
    content: str
    headings: List[str] # Document hierarchy at this block
    is_heading: bool

def parse_markdown_blocks(text: str) -> List[MarkdownBlock]:
    raw_blocks = re.split(r'\n\s*\n', text.strip())
    blocks = []
    current_headings = []
    
    for rb in raw_blocks:
        rb = rb.strip()
        if not rb:
            continue
            
        is_heading = False
        match = re.match(r'^(#{1,6})\s+(.*)', rb)
        if match:
            level = len(match.group(1))
            heading_text = match.group(2).strip()
            is_heading = True
            
            while current_headings and current_headings[-1][0] >= level:
                current_headings.pop()
            current_headings.append((level, heading_text))
            
        headings_str = [h[1] for h in current_headings]
        blocks.append(MarkdownBlock(content=rb, headings=headings_str, is_heading=is_heading))
        
    return blocks

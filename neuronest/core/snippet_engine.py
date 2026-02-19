from typing import List
from neuronest.utils.markdown_parser import parse_markdown_blocks, MarkdownBlock

def extract_smart_snippets(text: str, query: str, context_radius: int = 2) -> str:
    """
    Extracts relevant snippets preserving surround blocks and heading hierarchy.
    """
    blocks = parse_markdown_blocks(text)
    query_lower = query.lower()
    
    match_indices = []
    for i, block in enumerate(blocks):
        if query_lower in block.content.lower():
            match_indices.append(i)
            
    if not match_indices:
        return ""
        
    # Merge overlapping ranges
    ranges = []
    for idx in match_indices:
        start = max(0, idx - context_radius)
        end = min(len(blocks) - 1, idx + context_radius)
        
        if not ranges:
            ranges.append([start, end])
        else:
            last_range = ranges[-1]
            if start <= last_range[1] + 1:
                # Overlaps or contiguous, merge
                last_range[1] = max(last_range[1], end)
            else:
                ranges.append([start, end])
                
    # Format output
    output_parts = []
    last_end = -1
    
    for start, end in ranges:
        if start > last_end + 1:
            if last_end != -1:
                output_parts.append("\n...\n")
                
            if start < len(blocks) and blocks[start].headings and not blocks[start].is_heading:
                 parent_heading = blocks[start].headings[-1]
                 output_parts.append(f"> Context: {parent_heading}")
                 
        for i in range(start, end + 1):
            output_parts.append(blocks[i].content)
            
        last_end = end
        
    return "\n\n".join(output_parts)

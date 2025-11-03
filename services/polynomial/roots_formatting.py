from typing import List


def simplify_roots_text(roots_display: str) -> str:
    """Convert verbose multi-line roots_display into compact 'x1=..., x2=...' etc.
    Accepts blocks containing separators and analysis; returns only assignments.
    """
    if not roots_display:
        return ""
    lines = [l.strip() for l in roots_display.splitlines() if l.strip()]
    compact: List[str] = []
    for ln in lines:
        # Lines like 'x_1 = ...' or 'x1 = ...'
        if ln.lower().startswith('x_') or ln.lower().startswith('x'):
            # remove underscores in variable name x_1 -> x1
            parts = ln.split('=', 1)
            if len(parts) == 2:
                var = parts[0].replace('_', '').strip()
                val = parts[1].strip()
                compact.append(f"{var}={val}")
    return ', '.join(compact)

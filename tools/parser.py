def parse_tm(description: str) -> dict[str, str]:
    """Parse a Turing machine description into a transition dictionary."""
    
    blocks = description.split("_")
    states = [chr(ord("A") + i) for i in range(len(blocks))]
    transitions = dict()
    
    for state, block in zip(states, blocks):
        tokens = [block[i:i+3] for i in range(0, len(block), 3)]
        for symbol, token in enumerate(tokens):
            transitions[f"{state}{symbol}"] = token
    return transitions

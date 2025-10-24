from tools.parser import parse_tm
from collections import defaultdict

def simulate_tm(machine: str, stepc_lim: int) -> tuple[set[str], bool, int]:
    """Simulate a Turing machine for a given number of steps.
    
    Returns:
        tuple: (visited_configs, halted, step_count)
    """
    # Use defaultdict for automatic 0 initialization
    tape = defaultdict(int)
    transitions = parse_tm(machine)
    head_pos = 0
    state = 'A'
    visited_configs = set()
    
    for step in range(stepc_lim):
        # Get current symbol (defaultdict returns 0 if not present)
        current_symbol = tape[head_pos]
        transition_key = f"{state}{current_symbol}"
        
        # Check if transition exists
        if transition_key not in transitions:
            return visited_configs, True, step
        
        transition = transitions[transition_key]
        write_symbol, direction, next_state = transition
        
        # Check for halt
        if next_state in ('Z', '-'):
            return visited_configs, True, step
        
        # Build configuration string for visited set
        if direction == 'L':
            adjacent_symbol = tape[head_pos - 1]
            config = f"{state}{current_symbol}{adjacent_symbol}L"
        else:  # direction == 'R'
            adjacent_symbol = tape[head_pos + 1]
            config = f"{state}{current_symbol}{adjacent_symbol}R"
        
        # Add to visited if valid length
        if len(config) == 4:
            visited_configs.add(config)
        
        # Execute transition
        tape[head_pos] = int(write_symbol)
        
        if direction == 'L':
            head_pos -= 1
        else:  # direction == 'R'
            head_pos += 1
        
        state = next_state
    
    return visited_configs, False, stepc_lim
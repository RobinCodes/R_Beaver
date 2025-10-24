from collections import defaultdict

def simulate_branch(branch: list[str], machine: dict) -> bool:
    """Simulate a branch of configurations to check for contradictions.
    
    Args:
        branch: List of configs [config_n, config_n-1, ..., config_0] (latest to earliest)
        machine: Transition dictionary
    
    Returns:
        bool: True if contradiction found, False otherwise
    """
    if not branch:
        return False
    
    # Use defaultdict to avoid key checks
    tape = defaultdict(int)
    head_pos = 0
    
    for i, config in enumerate(branch):
        if len(config) < 2:
            continue
            
        state = config[0]
        current_symbol = int(config[1])
        direction = config[3] if len(config) > 3 else None
        
        # Check for contradiction at current position
        existing_symbol = tape.get(head_pos)
        if existing_symbol is not None and existing_symbol != current_symbol:
            return True  # Contradiction found
        
        # Special check for last config (earliest in time)
        if i == len(branch) - 1 and direction:
            if direction == 'L':
                left_symbol = tape.get(head_pos - 1)
                if left_symbol is not None and left_symbol != current_symbol:
                    return True
            elif direction == 'R':
                right_symbol = tape.get(head_pos + 1)
                if right_symbol is not None and right_symbol != current_symbol:
                    return True
        
        # Get transition and write symbol
        transition_key = f"{state}{current_symbol}"
        if transition_key not in machine:
            return True  # Invalid transition
        
        transition = machine[transition_key]
        
        # Check for halting transition (---, 1RZ, etc.)
        if transition[0] == '-' or transition[2] in ('Z', '-'):
            # Halting transition - don't try to write
            continue
        
        write_symbol = int(transition[0])
        tape[head_pos] = write_symbol
        
        # Move head
        if direction == 'L':
            head_pos -= 1
        elif direction == 'R':
            head_pos += 1
    
    return False
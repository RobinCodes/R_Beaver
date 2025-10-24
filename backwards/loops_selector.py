def loops_selector(loop: str, machine: dict, d: int, preconfigs: list[str]) -> str:
    """Run Phase 2 to determine if a loop is impossible to escape.
    
    Args:
        loop: Loop string in format "config1 -> config2 -> ..."
        machine: Transition dictionary
        d: Maximum depth
        preconfigs: List of configurations before the loop
    
    Returns:
        str: "NONHALT" if loop is impossible, "UNKNOWN" otherwise
    """
    from backwards.simulate_branch import simulate_branch
    
    # Phase 2 Step 1: Attempt to prove escaping the loop is impossible
    
    # Parse loop string into list of configs
    parts = [p.strip() for p in loop.split("->")]
    
    # Reverse to get branch format: config_n ... config_0
    # (config_0 being right before preconfigs)
    branch_format_loop = list(reversed(parts))
    
    # Combine loop with preconfigs
    branch = branch_format_loop + preconfigs
    
    print(f"Testing loop: {loop}")
    print(f"Branch to simulate: {branch}")
    
    # If simulation finds a contradiction, the loop is impossible
    if simulate_branch(branch, machine):
        print("  -> Loop is IMPOSSIBLE (contradiction found)")
        return "NONHALT"
    
    print("  -> Loop status UNKNOWN (no contradiction)")
    
    # Phase 2 Step 2: Verify that entering the loop is impossible
    # (Not implemented yet as per user request)
    
    return "UNKNOWN"
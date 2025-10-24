def loops_selector(loop: str, machine: dict, d: int, preconfigs: list[str], 
                   visited_configs: set = None) -> str:
    """Run Phase 2 to determine if a loop is impossible to escape or enter.
    
    Args:
        loop: Loop string in format "config1 -> config2 -> ..."
        machine: Transition dictionary
        d: Maximum depth for Phase 2 Step 2
        preconfigs: List of configurations before the loop (in execution order)
        visited_configs: Set of configurations visited during forward simulation
    
    Returns:
        str: "NONHALT" if loop is impossible, "UNKNOWN" otherwise
    """
    from backwards.simulate_branch import simulate_branch
    
    if visited_configs is None:
        visited_configs = set()
    
    # Phase 2 Step 1: Attempt to prove escaping the loop is impossible
    
    # Parse loop string into list of configs
    parts = [p.strip() for p in loop.split("->")]
    
    # Reverse to get branch format: config_n ... config_0
    # (config_0 being right before preconfigs)
    branch_format_loop = list(reversed(parts))
    
    # Combine loop with preconfigs
    branch = branch_format_loop + preconfigs
    
    print(f"\n=== Testing loop: {loop} ===")
    print(f"Step 1 - Testing if escaping leads to contradiction")
    print(f"Branch to simulate: {branch}")
    
    # If simulation finds a contradiction, the loop is impossible to escape
    if simulate_branch(branch, machine):
        print("  -> IMPOSSIBLE: Escaping loop leads to contradiction")
        return "NONHALT"
    
    print("  -> Cannot prove loop is inescapable")
    
    # Phase 2 Step 2: Verify that entering the loop is impossible
    print(f"\nStep 2 - Testing if entering the loop is possible")
    
    # Convert loop string to set for fast membership checking
    loop_configs = set(parts)
    
    # Find all configurations that can lead INTO the loop
    # These are children of loop configs that are NOT themselves in the loop
    entry_points = []
    
    for loop_config in parts:
        loop_state = loop_config[0]
        loop_symbol = loop_config[1]
        
        # Find all configurations that can transition to this loop config
        for pair, transition in machine.items():
            if transition[2] == loop_state:
                child = f"{pair}{loop_symbol}{transition[1]}"
                
                # Only consider if this child is NOT in the loop
                if child not in loop_configs:
                    entry_points.append(child)
    
    # Remove duplicates
    entry_points = list(set(entry_points))
    
    if not entry_points:
        print("  -> IMPOSSIBLE: No entry points into the loop")
        return "NONHALT"
    
    print(f"  -> Found {len(entry_points)} potential entry points")
    
    # Build branches backwards from entry points, checking for contradictions
    branches_at_depth = [[entry] for entry in entry_points]
    
    for depth in range(1, d + 1):
        print(f"  -> Depth {depth}: {len(branches_at_depth)} branches")
        
        # Check all current branches
        valid_branches = []
        found_initial_config = False
        
        for branch in branches_at_depth:
            # Check for contradiction
            if simulate_branch(branch[::-1], machine):
                continue
            
            # Check if branch reaches initial config
            if "A00R" in branch or "A00L" in branch:
                # Check if forward simulation visited configs not in this branch
                # If so, this branch doesn't represent actual execution path
                if visited_configs:
                    configs_not_in_branch = [c for c in visited_configs if c not in branch]
                    if configs_not_in_branch:
                        # Forward sim visited configs outside this branch, continue expansion
                        valid_branches.append(branch)
                        continue
                
                # This branch could represent actual execution path
                print(f"  -> UNKNOWN: Found valid entry path at depth {depth}")
                print(f"     Entry branch: {' -> '.join(branch)}")
                found_initial_config = True
                continue
            
            # This branch is valid so far
            valid_branches.append(branch)
        
        if found_initial_config:
            return "UNKNOWN"
        
        # If no valid branches remain, loop is impossible
        if not valid_branches:
            print(f"  -> IMPOSSIBLE: All entry branches contradict by depth {depth}")
            return "NONHALT"
        
        # Expand branches for next depth (if not at limit)
        if depth < d:
            new_branches = []
            
            for branch in valid_branches:
                last_config = branch[-1]
                parent_state = last_config[0]
                parent_symbol = last_config[1]
                
                # Find children of this parent
                for pair, transition in machine.items():
                    if transition[2] == parent_state:
                        child = f"{pair}{parent_symbol}{transition[1]}"
                        new_branches.append(branch + [child])
            
            branches_at_depth = new_branches
        else:
            branches_at_depth = valid_branches
    
    # Reached maximum depth without proving impossibility
    print(f"  -> UNKNOWN: Could not prove impossibility within depth limit {d}")
    print(f"     Remaining valid branches: {len(branches_at_depth)}")
    
    return "UNKNOWN"
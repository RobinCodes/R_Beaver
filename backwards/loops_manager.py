from backwards.detect_loops import detect_loop

def loops_manager(branches):
    """Process branches to extract loops and preconfigs.
    
    Returns:
        tuple: (remaining_branches, unique_loops, preconfigs_dict)
    """
    loops = []
    loop_configs = set()
    preconfigs = dict()
    
    # First pass: detect loops and collect preconfigs
    for branch in branches:
        has_loop, loop = detect_loop(branch)
        
        if has_loop:
            loop_str = ' -> '.join(loop)
            loops.append(loop_str)
            loop_configs.update(loop)  # Use update instead of loop
            
            # FIX: Find where the loop starts in the branch
            loop_start_idx = None
            loop_len = len(loop)
            
            # Search for where the loop sequence begins
            for i in range(len(branch) - loop_len + 1):
                if branch[i:i + loop_len] == loop:
                    loop_start_idx = i
                    break
            
            # Everything before the loop is preconfigs
            # Reverse because branches grow from halt outward (opposite of execution order)
            if loop_start_idx is not None:
                preconfigs[loop_str] = branch[:loop_start_idx][::-1]
            else:
                preconfigs[loop_str] = []
    
    # Second pass: filter branches that don't contain loop configs
    new_branches = [
        branch for branch in branches 
        if not any(config in loop_configs for config in branch)
    ]
    
    # Deduplicate loops (convert to set then back to list)
    loops = list(set(loops))
    
    # Filter out longer loops that are extensions of shorter ones
    loops_sorted = sorted(loops, key=len)
    loops_filtered = []
    for p in loops_sorted:
        if not any(p.startswith(short + ' ->') for short in loops_filtered):
            loops_filtered.append(p)

    return new_branches, loops_filtered, preconfigs
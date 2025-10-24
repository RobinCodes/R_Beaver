def loops_selector(loop: str, machine:dict, d, preconfigs: list[str]) -> str:
    """Run Phase 2, 3 and 4 (if needed and requested), then return NONHALT or UNKNOWN
    """
    from backwards.simulate_branch import simulate_branch

    # Phase 2 Step 1: attempt to prove escaping the loop is impossible
    
    parts = [p.strip() for p in loop.split("->")]
    branch_format_loop = list(reversed(parts)) # this is the loop in format config_n ... config_0 (config 0 being right before preconfigs)
        
    branch = branch_format_loop + preconfigs
    
    print(branch)
        
    if simulate_branch(branch, machine):
        return "NONHALT"
    
    # if we did not return, proceed to Step 2: verify that entering the loop is impossible
        
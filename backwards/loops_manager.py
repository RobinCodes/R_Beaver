from backwards.detect_loops import detect_loop

def loops_manager(branches):
    loops = []
    new_branches = []
    loop_configs = set()
    preconfigs = dict()
    for branch in branches:
        has_loop, loop = detect_loop(branch)

        if has_loop: # we detect a loop
            loops.append(' -> '.join(loop))
            for config in loop:
                loop_configs.add(config)
            # for collecting the "preconfig" part of the branch:
            result = []
            for item in reversed(branch):
                if item in loop:
                    break
                result.insert(0, item) # fill up backwards because backwards with backwards is forwards, so order is preserved
            preconfigs[' -> '.join(loop)] = result # preconfigs in the branch
        else:
            # filter out complexes
            if any(config in loop_configs for config in branch):
                continue
            new_branches.append(branch)

    # Second filtering pass
    new_branches_2 = []
    for branch in new_branches:
        if not any(config in loop_configs for config in branch):
            new_branches_2.append(branch)

    branches = new_branches_2
    loops[:] = list(set(loops))  # deduplicate in-place
    #filter longer loops that begin with shorter ones (will be managed later)
    paths_sorted = sorted(loops, key=len)
    loops_filtered = []
    for p in paths_sorted:
        if not any(p.startswith(short + ' ->') for short in loops_filtered):
            loops_filtered.append(p)
    
    print(preconfigs)
    return branches, loops_filtered, preconfigs

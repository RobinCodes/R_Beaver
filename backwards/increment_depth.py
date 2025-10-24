from pathlib import Path
from backwards.simulate_branch import simulate_branch

def incr_graph(d, machine, graph, branches, unparsed_machine: str, 
               history=False, visited_configs: set = None) -> tuple[list[list[str]], dict[int, list[str]], int]:
    """Increment the depth of the backwards search graph.
    
    Returns:
        tuple: (branches, graph, status_code)
               status_code: 0 = normal, 1 = stepc limit reached
    """
    if visited_configs is None:
        visited_configs = set()
    
    if history:
        with open(f"{Path(__file__).parent}/individual/{unparsed_machine}_results/history.txt", "a") as f:
            f.write(f"Depth {d}:\n")
            for b in branches:
                f.write(f"{' -> '.join(b)}\n")
            f.write("\n")
    
    parents = graph[d - 1]
    children = set()  # Use set for automatic deduplication
    new_branches = []
    
    # Build parent_to_branches mapping once
    parent_to_branches = {}
    for branch_idx, branch in enumerate(branches):
        if branch:
            last_config = branch[-1]
            if last_config not in parent_to_branches:
                parent_to_branches[last_config] = []
            parent_to_branches[last_config].append(branch_idx)
    
    for parent in parents:
        parent_state = parent[0]
        parent_symbol = parent[1]
        
        # Find all children of this parent
        parent_children = []
        for pair, transition in machine.items():
            if transition[2] == parent_state:  # Next state matches parent state
                child = f"{pair}{parent_symbol}{transition[1]}"
                children.add(child)
                parent_children.append(child)
        
        # Handle branching
        if parent in parent_to_branches:
            # Parent has existing branches
            for branch_idx in parent_to_branches[parent]:
                parent_branch = branches[branch_idx]
                for child in parent_children:
                    new_branches.append(parent_branch + [child])
        else:
            # First level or new parent
            for child in parent_children:
                if d == 1:
                    new_branches.append([parent, child])
    
    # Remove contradicting branches - do this in one pass
    valid_branches = []
    branch_tuples = set()  # For deduplication
    
    for branch in new_branches:
        # Skip if contradicts
        if simulate_branch(branch[::-1], machine):
            continue
        
        # Deduplicate
        branch_tuple = tuple(branch)
        if branch_tuple in branch_tuples:
            continue
        
        branch_tuples.add(branch_tuple)
        valid_branches.append(branch)
    
    branches = valid_branches
    graph[d] = list(children)
    
    # Check for stepc limit issue
    if visited_configs:
        for branch in branches:
            if "A00R" in branch or "A00L" in branch:
                # Check if all visited configs are in this branch
                if all(vconfig in branch for vconfig in visited_configs):
                    return branches, graph, 1
    
    return branches, graph, 0
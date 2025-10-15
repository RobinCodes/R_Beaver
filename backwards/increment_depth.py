from pathlib import Path
from backwards.simulate_branch import simulate_branch

def incr_graph(d, machine, graph, branches, unparsed_machine: str, history=False, visited_configs: set = set()) -> tuple[list[list[str]], dict[int, list[str]]]:
    """Increment the depth of the backwards search graph (and branches)."""

    if history:
        with open(f"{Path(__file__).parent}/individual/{unparsed_machine}_results/history.txt", "a") as f:
            f.write(f"Depth {d}:\n")
            for b in branches:
                f.write(f"{' -> '.join(b)}\n")
            f.write("\n")
    
    parents = graph[d-1]
    children = list()
    new_branches = list() 
    
    for parent in parents:
        parent_children = []
        
        for pair, transition in machine.items():
            if transition[2] == parent[0]:
                child = f"{pair}{parent[1]}{transition[1]}"
                children.append(child)
                parent_children.append(child)
        
        #handling branching
        parent_branches = [i for i, branch in enumerate(branches) if branch and branch[-1] == parent]
        
        if parent_branches:
            for branch_idx in parent_branches:
                for child in parent_children:
                    new_branches.append(branches[branch_idx] + [child])
        else:
            for child in parent_children:
                if d == 1:
                    new_branches.append([parent, child])
    
    branches = [branch for branch in new_branches if not simulate_branch(branch[::-1], machine)] # remove contradicting branches
    branches = [list(t) for t in set(tuple(branch) for branch in branches)] # deduplicate branches
    graph[d] = children
    
    counterex = 0

    for branch in branches:
        counterex = 0
        if "A00R" in branch or "A00L" in branch:
            for vconfig in visited_configs:
                if vconfig not in branch:
                    counterex += 1
            
            if counterex == 0:
                return branches, graph, 1
            
    return branches, graph, 0
   
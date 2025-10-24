import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from tools.parser import parse_tm
from tools.simulate_tm import simulate_tm
from increment_depth import incr_graph
from loops_manager import loops_manager
from backwards.loops_selector import loops_selector

def manager(machine: str, phases: int, stepc_lim: int, history: bool, DEPTH: int) -> str:
    """Main manager for backwards reasoning on a Turing machine.
    
    Args:
        machine: Machine description string
        phases: Number of phases to run (1 or 2)
        stepc_lim: Step count limit for forward simulation
        history: Whether to write history files
        DEPTH: Maximum depth for backwards search
    
    Returns:
        str: Result status (HALT, NONHALT, or UNKNOWN with reason)
    """
    parsed_machine = parse_tm(machine)
    graph = {}
    branches = []
    
    # Run forward simulation
    visited_configs, halted, step_count = simulate_tm(machine, stepc_lim)
    
    # Setup history file if needed
    if history:
        base_dir = Path(__file__).parent / "individual" / f"{machine}_results"
        file_path = base_dir / "history.txt"
        base_dir.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w") as f:
            blocks = machine.split("_")
            num_states = len(blocks)
            num_symbols = len(blocks[0]) // 3
            max_configs = num_states * (num_symbols ** 2) - num_symbols + 1
            
            f.write(f"Machine: {machine}\n")
            f.write(f"States: {num_states}, Symbols: {num_symbols}\n")
            f.write(f"Max configurations: {max_configs}\n")
            f.write(f"Max depth for Phase 2: {max_configs + 1}\n\n")
    
    # Check if machine halted
    if halted:
        if history:
            with open(file_path, "a") as f:
                f.write(f"HALT (at step {step_count + 1})\n")
        return "HALT"
    
    # Find initial halting transition
    try:
        halt_config = next(k for k, v in parsed_machine.items() 
                          if v in ("---", "1RZ", "0RZ", "1LZ", "0LZ"))
        graph[0] = [halt_config]
    except StopIteration:
        if history:
            with open(file_path, "a") as f:
                f.write("NONHALT - NO HALTING TRANSITION\n")
        return "NONHALT"
    
    # Phase 1: Build backwards tree
    depth_reached = 0
    for d in range(1, DEPTH + 1):
        branches, graph, status = incr_graph(
            d, parsed_machine, graph, branches, machine, history, visited_configs
        )
        
        if status == 1:
            if history:
                with open(file_path, "a") as f:
                    f.write("UNKNOWN - STEPC LIMIT - PROBABLE HALTER\n")
            return "UNKNOWN - STEPC LIMIT"
        
        depth_reached = d
        
        # Check if tree is finite
        remaining_branches, _, _ = loops_manager(branches)
        if not remaining_branches:
            break
    
    # Analyze loops
    remaining_branches, loops, preconfigs = loops_manager(branches)
    
    if history:
        with open(file_path, "a") as f:
            f.write(f"Phase 1 completed at depth {depth_reached}\n")
            if loops:
                f.write(f"Found {len(loops)} loops:\n")
                for loop in loops:
                    f.write(f"  {loop}\n")
            else:
                f.write("No loops found\n")
            f.write("\n")
    
    # Check if tree is finite (no loops, no remaining branches)
    if not loops and not remaining_branches:
        if history:
            with open(file_path, "a") as f:
                f.write("NONHALT - FINITE TREE\n")
        return "NONHALT"
    
    # Phase 2: Analyze loops
    if phases > 1 and not remaining_branches:
        if history:
            with open(file_path, "a") as f:
                f.write(f"\n=== Phase 2 ===\n")
                f.write(f"Reached Phase 2 at depth {depth_reached}\n")
                f.write(f"Total loops: {len(loops)}\n")
                if loops:
                    max_loop = max(loops, key=lambda s: len(s.split(" -> ")))
                    max_loop_len = len(max_loop.split(" -> "))
                    f.write(f"Longest loop: {max_loop_len} configurations\n\n")
        
        undecided_loops = []
        
        for loop in loops:
            status = loops_selector(loop, parsed_machine, DEPTH, preconfigs[loop], visited_configs)
            
            if status == "UNKNOWN":
                undecided_loops.append(loop)
            elif status == "NONHALT":
                if history:
                    with open(file_path, "a") as f:
                        f.write(f"Impossible loop: {loop}\n")
        
        if not undecided_loops:
            if history:
                with open(file_path, "a") as f:
                    f.write("\nNONHALT - ALL LOOPS IMPOSSIBLE\n")
            return "NONHALT"
        else:
            if history:
                with open(file_path, "a") as f:
                    f.write(f"\nUNKNOWN - {len(undecided_loops)} UNRESOLVED LOOPS:\n")
                    for loop in undecided_loops:
                        f.write(f"  {loop}\n")
            return "UNKNOWN - UNDECIDED LOOPS"
    else:
        # Didn't reach Phase 2 or Phase 2 not requested
        if history:
            with open(file_path, "a") as f:
                if phases == 1:
                    f.write("Phase 2 not requested\n")
                else:
                    f.write("UNKNOWN - PHASE 2 NOT REACHED (infinite tree)\n")
        
        return "UNKNOWN - INFINITE TREE NO PHASE 2"
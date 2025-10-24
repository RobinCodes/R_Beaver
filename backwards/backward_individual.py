import sys
from pathlib import Path

#add the project root (parent of 'scripts/') to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from tools.parser import parse_tm
from tools.simulate_tm import simulate_tm
from increment_depth import incr_graph
from loops_manager import loops_manager
from backwards.loops_selector import loops_selector

def manager(machine: str, phases: int, stepc_lim: int, history: bool, DEPTH: int) -> str:
    parsed_machine = parse_tm(machine)
    graph = dict()
    branches = list()
    sim_tm_data = simulate_tm(machine, stepc_lim)
    visited_configs = sim_tm_data[0]
    
    if history:
        base_dir = Path(__file__).parent / "individual" / f"{machine}_results"
        file_path = base_dir / "history.txt"
        base_dir.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w") as f:
            blocks = machine.split("_")
            states = [chr(ord("A") + i) for i in range(len(blocks))]
            num_states = len(states)
            num_symbols = len(blocks[0]) // 3
            f.write(f"The machine has {num_states} states and {num_symbols} symbols.\n")
            f.write(f"The maximum number of configurations is {num_states * (num_symbols**2) - num_symbols + 1}\n")
            f.write(f"The maximum depth needed for reaching Phase 2 (or deciding the machine) is {(num_states * (num_symbols**2) - num_symbols + 1) + 1}\n")

    if sim_tm_data[1]:
        if history:
            with open(file_path, "a") as f:
                f.write("HALT\n")
            
        return "HALT"

    try:
        graph[0] = [next(k for k, v in parsed_machine.items() if v in ("---", "1RZ"))]
    except StopIteration:
        if history:
            with open(file_path, "a") as f:
                f.write("NONHALT - NO HALTING TRANSITION\n")
        return "NONHALT" # no halting transition
    
    for d in range(1, DEPTH+1):
        incremented_data = incr_graph(d, parsed_machine, graph, branches, machine, history, visited_configs)
        graph = incremented_data[1]
        branches = incremented_data[0]
        if incremented_data[2] == 1:
            if history:
                with open(file_path, "a") as f:
                    f.write("UNKNOWN - STEPC LIMIT - PROBABLE HALTER\n")
            return "UNKNOWN - STEPC LIMIT"
        if loops_manager(branches)[0] == []:
            break

    loops = loops_manager(branches)[1]
    preconfigs = loops_manager(branches)[2]

    if history:
        with open(f"{Path(__file__).parent}/individual/{machine}_results/history.txt", "a") as f:
            f.write(f"Phase 1 results: {d}:\n")
            if loops:
                for l in loops:
                    f.write(f"{l}\n")

            else:
                if loops_manager(branches)[0] == []:
                    f.write("NONHALT - FINITE")
            f.write("\n")

    if loops == [] and loops_manager(branches)[0] == []:
        return "NONHALT"
    
    if phases > 1 and loops_manager(branches)[0] == []:
        if history:
            with open(f"{Path(__file__).parent}/individual/{machine}_results/history.txt", "a") as f:
                f.write(f"Reached Phase 2 at depth {str(len(branches[0]))}\n")
                f.write(f"There are a total of {len(loops)} loops.\n")
                f.write(f"The longest loop is {len(max(loops, key=lambda s: len(s.split(" -> ")), default=None).split(" -> "))} configurations long.\n")

        remaining_loops = []
        
        for j, loop in enumerate(loops): 
            status = loops_selector(loop, parsed_machine, DEPTH, preconfigs[loop]) # important: status is for loop status, not machine status.
            if status == "UNKNOWN":
                remaining_loops.append(loop)
            elif status == "NONHALT":
                if history:
                    with open(file_path, "a") as f:
                        f.write(f"Impossible loop: - {loop}\n")

        if remaining_loops == []:
            if history:
                with open(file_path, "a") as f:
                    f.write("NONHALT\n")
            return "NONHALT"
        else:
            if history:
                with open(file_path, "a") as f:
                    f.write(f"UNKNOWN - {len(remaining_loops)} LOOPS NOT RESOLVED:\n")
                    for loop in remaining_loops:
                        f.write(f"Unknown loop: - {loop}\n")
            return "UNKNOWN - UNDECIDED LOOPS"
        
    else:
        if history:
            if phases == 2:
                with open(f"{Path(__file__).parent}/individual/{machine}_results/history.txt", "a") as f:
                    f.write(f"UNKNOWN - PHASE 2 NOT REACHED\n")
                    f.write("\n")
            else:
                with open(f"{Path(__file__).parent}/individual/{machine}_results/history.txt", "a") as f:
                    f.write(f"UNKNOWN - INFINITE TREE NO PHASE 2\n")
                    f.write("\n")

        return "UNKNOWN - INFINITE TREE NO PHASE 2"


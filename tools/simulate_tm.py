from tools.parser import parse_tm

def simulate_tm(machine: str, stepc_lim: int) -> tuple[set[str], bool, int]:
    """Simulate a Turing machine for a given number of steps.
    Return the set of visited configurations, whether it halted, and the step count"""
    
    tape = dict()
    transitions = parse_tm(machine)
    head_pos = 0
    visited_configs = set()
    for i in range(1, stepc_lim + 1):
        if i == 1:
            tape[0] = transitions["A0"][0]
            if transitions["A0"][1] == "L":
                head_pos -= 1
            elif transitions["A0"][1] == "R":
                head_pos += 1
            next_state = transitions["A0"][2]
            config = "A00".join(transitions["A0"][1])
            if len(config) == 4:
                visited_configs.add(config)
            continue
        
        if next_state == "Z" or next_state == "-":
            return visited_configs, True, i-1
    
        if head_pos < 0:
                head_pos = 0
                temp = dict()
                for i in range(len(tape)):
                    temp[i+1] = tape[i]
                    
                tape = temp

        transition = f"{next_state}{tape[head_pos] if head_pos in tape else 0}"
        
        dir = transitions[transition][1]
        
        if dir == "L":
            symb_to_l = tape[head_pos - 1] if head_pos - 1 in tape else "0"
            config = f"{next_state}{tape[head_pos] if head_pos in tape else 0}{symb_to_l}L"
        elif dir == "R":
            symb_to_r = tape[head_pos + 1] if head_pos + 1 in tape else "0"
            config = f"{next_state}{tape[head_pos] if head_pos in tape else 0}{symb_to_r}R"

        if config not in visited_configs:
            if len(config) == 4:
                visited_configs.add(config)
            
        tape[head_pos] = transitions[transition][0]
        
        if dir == "L":
            head_pos -= 1
        elif dir == "R":
            head_pos += 1
            
        next_state = transitions[transition][2]
            
    return visited_configs, False, i-1
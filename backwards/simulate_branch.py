def simulate_branch(branch: list[str], machine: dict) -> bool:
    """Simulate a branch of configurations to check for contradictions.
    Return True if a contradiction is found, otherwise False.
    expected branch format: [config_n, config_n-1, ..., config_0 = halt_config] (from latest to earliest)
    """
    
    tape = dict()
    head_pos = 0
            
    for i, config in enumerate(branch):
        #print(tape) for tape evolution
        
        # example config: A01R
        current_symbol = config[1]
        if len(config) > 2:
            direction = config[3]
        
        if head_pos in tape:
            if tape[head_pos] != current_symbol:
                return True #contradiction 
        else:
            if i == len(branch) - 1:
                if direction == 'L':
                    if tape.get(head_pos - 1) not in (None, current_symbol):
                        return True
                elif direction == 'R':
                    if tape.get(head_pos + 1) not in (None, current_symbol):
                        return True


        tape[head_pos] = machine.get(f"{config[0]}{config[1]}")[0] 

        if direction == 'L':
            head_pos -= 1
        elif direction == 'R':
            head_pos += 1
            
        if head_pos < 0:
            head_pos = 0
            temp = dict()
            for i in range(len(tape)):
                temp[i+1] = tape[i]
                
            tape = temp
                      
    return False

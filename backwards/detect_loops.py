def detect_loop(branch):
    visited = list()
    for i, config in enumerate(branch):
        if config in visited:
            loop_start_index = visited.index(config)
            loop = visited[loop_start_index:]
            return True, loop
        visited.append(config)
    return False, [] 
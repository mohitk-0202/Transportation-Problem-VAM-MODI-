import numpy as np

def get_user_input():
    print("=== Transportation Problem Setup ===")
    num_sources = int(input("Enter the number of sources: "))
    num_dests = int(input("Enter the number of destinations: "))

    print("\n--- Enter Supply for each Source ---")
    supply = []
    for i in range(num_sources):
        supply.append(float(input(f"Capacity of Source S{i+1}: ")))
        
    print("\n--- Enter Demand for each Destination ---")
    demand = []
    for j in range(num_dests):
        demand.append(float(input(f"Requirement of Destination D{j+1}: ")))

    print("\n--- Enter Transportation Costs (C_ij) ---")
    costs = []
    for i in range(num_sources):
        row = []
        for j in range(num_dests):
            row.append(float(input(f"Cost from S{i+1} to D{j+1}: ")))
        costs.append(row)

    return np.array(supply), np.array(demand), np.array(costs)

def balance_problem(supply, demand, costs):
    total_supply = np.sum(supply)
    total_demand = np.sum(demand)
    
    if total_supply > total_demand:
        diff = total_supply - total_demand
        demand = np.append(demand, diff)
        costs = np.hstack((costs, np.zeros((costs.shape[0], 1))))
        print(f"\n[!] Problem Unbalanced. Added Dummy Destination with demand {diff}.")
    elif total_demand > total_supply:
        diff = total_demand - total_supply
        supply = np.append(supply, diff)
        costs = np.vstack((costs, np.zeros((1, costs.shape[1]))))
        print(f"\n[!] Problem Unbalanced. Added Dummy Source with capacity {diff}.")
    else:
        print("\n[+] Problem is balanced.")
        
    return supply, demand, costs

def get_loop(alloc, start_r, start_c):
    rows, cols = alloc.shape
    valid = (alloc > 0).astype(bool)
    valid[start_r, start_c] = True
    
    # Prune rows/cols with only 1 allocated cell
    while True:
        pruned = False
        for r in range(rows):
            if np.sum(valid[r, :]) == 1:
                valid[r, :] = False
                pruned = True
        for c in range(cols):
            if np.sum(valid[:, c]) == 1:
                valid[:, c] = False
                pruned = True
        if not pruned:
            break
            
    # Sequence the remaining cells into a loop
    loop = [(start_r, start_c)]
    curr_r, curr_c = start_r, start_c
    is_row_search = True 
    
    while True:
        found = False
        if is_row_search:
            for c in range(cols):
                if c != curr_c and valid[curr_r, c]:
                    if (curr_r, c) not in loop:
                        loop.append((curr_r, c))
                        curr_c = c
                        is_row_search = False
                        found = True
                        break
                    elif (curr_r, c) == loop[0] and len(loop) > 3:
                        return loop
        else:
            for r in range(rows):
                if r != curr_r and valid[r, curr_c]:
                    if (r, curr_c) not in loop:
                        loop.append((r, curr_c))
                        curr_r = r
                        is_row_search = True
                        found = True
                        break
                    elif (r, curr_c) == loop[0] and len(loop) > 3:
                        return loop
        
        if not found:
            if len(loop) == 1:
                is_row_search = not is_row_search
            else:
                break
    return loop

def solve_transportation():
    supply, demand, costs = get_user_input()
    supply, demand, costs = balance_problem(supply, demand, costs)
    
    rows, cols = costs.shape
    allocation = np.zeros((rows, cols))
    
    # === PHASE 1: VAM (Initial Solution) ===
    s_temp, d_temp = supply.copy(), demand.copy()
    c_temp = costs.copy()
    
    while np.sum(s_temp) > 0 and np.sum(d_temp) > 0:
        row_pen = []
        for r in range(rows):
            valid_costs = c_temp[r, :][d_temp > 0]
            if s_temp[r] == 0 or len(valid_costs) == 0:
                row_pen.append(-1)
            elif len(valid_costs) == 1:
                row_pen.append(valid_costs[0])
            else:
                sorted_c = np.sort(valid_costs)
                row_pen.append(sorted_c[1] - sorted_c[0])
                
        col_pen = []
        for c in range(cols):
            valid_costs = c_temp[:, c][s_temp > 0]
            if d_temp[c] == 0 or len(valid_costs) == 0:
                col_pen.append(-1)
            elif len(valid_costs) == 1:
                col_pen.append(valid_costs[0])
            else:
                sorted_c = np.sort(valid_costs)
                col_pen.append(sorted_c[1] - sorted_c[0])
                
        if max(row_pen) >= max(col_pen):
            r = row_pen.index(max(row_pen))
            c = np.argmin(np.where(d_temp > 0, c_temp[r, :], np.inf))
        else:
            c = col_pen.index(max(col_pen))
            r = np.argmin(np.where(s_temp > 0, c_temp[:, c], np.inf))
            
        qty = min(s_temp[r], d_temp[c])
        allocation[r, c] = qty
        s_temp[r] -= qty
        d_temp[c] -= qty
        
        # Degeneracy fix: If both exhaust, leave a tiny trace to preserve basis
        if s_temp[r] == 0 and d_temp[c] == 0 and (np.sum(s_temp) > 0 or np.sum(d_temp) > 0):
            d_temp[c] = 1e-10 

    init_cost = np.sum(np.where(allocation < 1e-5, 0, allocation) * costs)
    print(f"\n[+] VAM Initial Cost: {init_cost}")

    # === PHASE 2: MODI & STEPPING STONE (Iterative Improvement) ===
    iteration = 1
    while True:
        u = np.full(rows, np.nan)
        v = np.full(cols, np.nan)
        u[0] = 0 
        
        while np.isnan(u).any() or np.isnan(v).any():
            progress = False
            for i in range(rows):
                for j in range(cols):
                    if allocation[i, j] > 0:
                        if not np.isnan(u[i]) and np.isnan(v[j]):
                            v[j] = costs[i, j] - u[i]
                            progress = True
                        elif not np.isnan(v[j]) and np.isnan(u[i]):
                            u[i] = costs[i, j] - v[j]
                            progress = True
            if not progress:
                if np.isnan(u).any(): u[np.where(np.isnan(u))[0][0]] = 0
                elif np.isnan(v).any(): v[np.where(np.isnan(v))[0][0]] = 0

        min_dij = 0
        enter_r, enter_c = -1, -1
        
        for i in range(rows):
            for j in range(cols):
                if allocation[i, j] == 0:
                    d_ij = costs[i, j] - (u[i] + v[j])
                    if d_ij < min_dij - 1e-7:
                        min_dij = d_ij
                        enter_r, enter_c = i, j

        if min_dij >= -1e-7:
            print(f"    -> Iteration {iteration}: No negative d_ij found. OPTIMAL!")
            break

        print(f"    -> Iteration {iteration}: Negative d_ij ({min_dij:.1f}) found. Shifting loop...")
        
        loop = get_loop(allocation, enter_r, enter_c)
        minus_cells = [loop[k] for k in range(1, len(loop), 2)]
        theta = min(allocation[r, c] for r, c in minus_cells)
        
        for k, (r, c) in enumerate(loop):
            if k % 2 == 0: allocation[r, c] += theta
            else: allocation[r, c] -= theta
            
        allocation = np.where(allocation < 1e-11, 0, allocation)
        iteration += 1

    # === FINAL OUTPUT ===
    clean_alloc = np.where(allocation < 1e-5, 0, allocation)
    total_cost = np.sum(clean_alloc * costs)
    
    print("\n" + "="*40)
    print("          FINAL OPTIMAL PLAN")
    print("="*40)
    print("\nOptimal Allocation Matrix:")
    print(clean_alloc)
    print(f"\nFinal Total Transportation Cost: {total_cost}")

if __name__ == "__main__":
    solve_transportation()
# ============================================================
# TRANSPORTATION PROBLEM
# VOGEL'S APPROXIMATION METHOD (VAM)
# FOLLOWED BY MODI METHOD
# ============================================================


EPS = 1e-9


# ============================================================
# PRINT TRANSPORTATION TABLE
# ============================================================

def print_table(cost, allocation, supply, demand, title):

    m = len(cost)
    n = len(cost[0])

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    print("\nCost Table / Allocation\n")

    print("        ", end="")

    for j in range(n):
        print(f"D{j + 1:^12}", end="")

    print("Supply")

    for i in range(m):

        print(f"S{i + 1:<6}", end="")

        for j in range(n):

            print(
                f"{cost[i][j]:.0f}({allocation[i][j]:.0f})",
                end=" " * 4
            )

        print(f"{supply[i]:.0f}")

    print("Demand ", end="")

    for j in range(n):
        print(f"{demand[j]:.0f}".center(16), end="")

    print()


# ============================================================
# CALCULATE TOTAL TRANSPORTATION COST
# ============================================================

def total_cost(cost, allocation):

    m = len(cost)
    n = len(cost[0])

    total = 0

    for i in range(m):
        for j in range(n):
            total += cost[i][j] * allocation[i][j]

    return total


# ============================================================
# FIND VAM PENALTY FOR A ROW
# ============================================================

def row_penalty(cost, row, active_columns):

    values = []

    for j in active_columns:
        values.append(cost[row][j])

    values.sort()

    if len(values) == 1:
        return values[0]

    return values[1] - values[0]


# ============================================================
# FIND VAM PENALTY FOR A COLUMN
# ============================================================

def column_penalty(cost, column, active_rows):

    values = []

    for i in active_rows:
        values.append(cost[i][column])

    values.sort()

    if len(values) == 1:
        return values[0]

    return values[1] - values[0]


# ============================================================
# VOGEL'S APPROXIMATION METHOD
# ============================================================

def vogel_approximation(cost, supply, demand):

    m = len(supply)
    n = len(demand)

    supply_left = supply.copy()
    demand_left = demand.copy()

    allocation = [
        [0 for _ in range(n)]
        for _ in range(m)
    ]

    # Set of basic cells
    basis = set()

    active_rows = set(range(m))
    active_columns = set(range(n))

    while active_rows and active_columns:

        # ----------------------------------------------------
        # Calculate row penalties
        # ----------------------------------------------------

        row_penalties = {}

        for i in active_rows:

            row_penalties[i] = row_penalty(
                cost,
                i,
                active_columns
            )

        # ----------------------------------------------------
        # Calculate column penalties
        # ----------------------------------------------------

        column_penalties = {}

        for j in active_columns:

            column_penalties[j] = column_penalty(
                cost,
                j,
                active_rows
            )

        # ----------------------------------------------------
        # Find maximum penalty
        # ----------------------------------------------------

        maximum_row_penalty = (
            max(row_penalties.values())
            if row_penalties else -1
        )

        maximum_column_penalty = (
            max(column_penalties.values())
            if column_penalties else -1
        )

        # ----------------------------------------------------
        # Select row or column
        # ----------------------------------------------------

        if maximum_row_penalty >= maximum_column_penalty:

            selected_row = max(
                active_rows,
                key=lambda i: (
                    row_penalties[i],
                    -min(cost[i][j] for j in active_columns),
                    -i
                )
            )

            selected_column = min(
                active_columns,
                key=lambda j: (
                    cost[selected_row][j],
                    j
                )
            )

        else:

            selected_column = max(
                active_columns,
                key=lambda j: (
                    column_penalties[j],
                    -min(cost[i][j] for i in active_rows),
                    -j
                )
            )

            selected_row = min(
                active_rows,
                key=lambda i: (
                    cost[i][selected_column],
                    i
                )
            )

        # ----------------------------------------------------
        # Allocate as much as possible
        # ----------------------------------------------------

        quantity = min(
            supply_left[selected_row],
            demand_left[selected_column]
        )

        allocation[selected_row][selected_column] = quantity

        basis.add(
            (selected_row, selected_column)
        )

        supply_left[selected_row] -= quantity
        demand_left[selected_column] -= quantity

        row_finished = abs(
            supply_left[selected_row]
        ) < EPS

        column_finished = abs(
            demand_left[selected_column]
        ) < EPS

        # ----------------------------------------------------
        # Handle crossing out
        # ----------------------------------------------------

        if row_finished and column_finished:

            # We need to maintain m+n-1 basic cells.
            # Close the row and keep the column active.
            active_rows.remove(selected_row)

            # Add a zero basic allocation to prevent degeneracy.
            if len(active_columns) > 1:

                possible_columns = [
                    j for j in active_columns
                    if j != selected_column
                ]

                zero_column = min(
                    possible_columns,
                    key=lambda j: (
                        cost[selected_row][j],
                        j
                    )
                )

                basis.add(
                    (selected_row, zero_column)
                )

            elif len(active_rows) > 0:

                possible_rows = list(active_rows)

                zero_row = min(
                    possible_rows,
                    key=lambda i: (
                        cost[i][selected_column],
                        i
                    )
                )

                basis.add(
                    (zero_row, selected_column)
                )

            else:

                active_columns.remove(
                    selected_column
                )

        elif row_finished:

            active_rows.remove(
                selected_row
            )

        elif column_finished:

            active_columns.remove(
                selected_column
            )

    return allocation, basis


# ============================================================
# FIND CLOSED LOOP FOR MODI
# ============================================================

def find_cycle(start, basis):

    cells = set(basis)
    cells.add(start)

    path = [start]

    # --------------------------------------------------------
    # DFS to find alternating row/column cycle
    # --------------------------------------------------------

    def dfs(current, move_in_row):

        i, j = current

        if move_in_row:

            candidates = [
                cell for cell in cells
                if cell[0] == i and cell != current
            ]

        else:

            candidates = [
                cell for cell in cells
                if cell[1] == j and cell != current
            ]

        for next_cell in candidates:

            # Closed cycle found
            if next_cell == start:

                if len(path) >= 4 and len(path) % 2 == 0:
                    return path + [start]

                continue

            if next_cell in path:
                continue

            path.append(next_cell)

            result = dfs(
                next_cell,
                not move_in_row
            )

            if result:
                return result

            path.pop()

        return None

    return dfs(start, True)


# ============================================================
# MODI METHOD
# ============================================================

def modi(
    cost,
    supply,
    demand,
    allocation,
    basis,
    max_iterations=100
):

    m = len(supply)
    n = len(demand)

    allocation = [
        row.copy()
        for row in allocation
    ]

    basis = set(basis)

    for iteration in range(max_iterations):

        # ----------------------------------------------------
        # Calculate potentials u and v
        #
        # For basic cell:
        #
        # u[i] + v[j] = cost[i][j]
        # ----------------------------------------------------

        u = [None] * m
        v = [None] * n

        u[0] = 0

        changed = True

        while changed:

            changed = False

            for i, j in basis:

                if u[i] is not None and v[j] is None:

                    v[j] = cost[i][j] - u[i]
                    changed = True

                elif v[j] is not None and u[i] is None:

                    u[i] = cost[i][j] - v[j]
                    changed = True

        # ----------------------------------------------------
        # Check whether all potentials were found
        # ----------------------------------------------------

        if any(value is None for value in u):
            print("Error calculating row potentials.")
            return allocation, basis

        if any(value is None for value in v):
            print("Error calculating column potentials.")
            return allocation, basis

        # ----------------------------------------------------
        # Calculate opportunity costs
        #
        # Delta(i,j) = C(i,j) - Ui - Vj
        #
        # For minimization:
        # All Delta >= 0 -> optimal
        # ----------------------------------------------------

        opportunity_cost = [
            [None for _ in range(n)]
            for _ in range(m)
        ]

        entering_cell = None
        most_negative = 0

        for i in range(m):

            for j in range(n):

                if (i, j) not in basis:

                    delta = (
                        cost[i][j]
                        - u[i]
                        - v[j]
                    )

                    opportunity_cost[i][j] = delta

                    if delta < most_negative:

                        most_negative = delta

                        entering_cell = (i, j)

        # ----------------------------------------------------
        # Display MODI iteration
        # ----------------------------------------------------

        print("\n" + "-" * 70)
        print(f"MODI Iteration {iteration + 1}")
        print("-" * 70)

        print("u values:", [round(x, 3) for x in u])
        print("v values:", [round(x, 3) for x in v])

        print("\nOpportunity Cost Table:")

        for i in range(m):

            for j in range(n):

                if opportunity_cost[i][j] is None:
                    print("  --  ", end=" ")
                else:
                    print(
                        f"{opportunity_cost[i][j]:6.2f}",
                        end=" "
                    )

            print()

        current_cost = total_cost(
            cost,
            allocation
        )

        print(
            f"\nCurrent Transportation Cost = "
            f"{current_cost:.2f}"
        )

        # ----------------------------------------------------
        # Optimal solution
        # ----------------------------------------------------

        if entering_cell is None:

            print("\nAll opportunity costs are >= 0.")
            print("Therefore, the solution is OPTIMAL.")

            return allocation, basis

        # ----------------------------------------------------
        # Entering variable
        # ----------------------------------------------------

        print(
            f"\nEntering cell = "
            f"({entering_cell[0] + 1}, "
            f"{entering_cell[1] + 1})"
        )

        # ----------------------------------------------------
        # Find closed loop
        # ----------------------------------------------------

        cycle = find_cycle(
            entering_cell,
            basis
        )

        if cycle is None:

            print("Could not find a MODI closed loop.")
            return allocation, basis

        print("\nClosed loop:")

        for cell in cycle:
            print(
                f"({cell[0] + 1},{cell[1] + 1})",
                end=" -> "
            )

        print()

        # ----------------------------------------------------
        # + - + - signs
        # ----------------------------------------------------

        plus_cells = []
        minus_cells = []

        for k, cell in enumerate(cycle[:-1]):

            if k % 2 == 0:
                plus_cells.append(cell)
            else:
                minus_cells.append(cell)

        # ----------------------------------------------------
        # Find theta
        #
        # theta = minimum allocation in '-' cells
        # ----------------------------------------------------

        theta = min(
            allocation[i][j]
            for i, j in minus_cells
        )

        print(f"Theta = {theta}")

        # ----------------------------------------------------
        # Update allocations
        # ----------------------------------------------------

        for k, cell in enumerate(cycle[:-1]):

            i, j = cell

            if k % 2 == 0:
                allocation[i][j] += theta

            else:
                allocation[i][j] -= theta

        # ----------------------------------------------------
        # Add entering cell to basis
        # ----------------------------------------------------

        basis.add(entering_cell)

        # ----------------------------------------------------
        # Remove a leaving cell
        # ----------------------------------------------------

        leaving_cell = None

        for i, j in minus_cells:

            if abs(allocation[i][j]) < EPS:

                leaving_cell = (i, j)
                break

        if leaving_cell is not None:
            basis.remove(leaving_cell)

            print(
                f"Leaving cell = "
                f"({leaving_cell[0] + 1}, "
                f"{leaving_cell[1] + 1})"
            )

    print("MODI iteration limit reached.")

    return allocation, basis


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 80)
    print("TRANSPORTATION PROBLEM - VAM + MODI")
    print("=" * 80)

    # --------------------------------------------------------
    # Input dimensions
    # --------------------------------------------------------

    m = int(
        input("\nEnter number of sources: ")
    )

    n = int(
        input("Enter number of destinations: ")
    )

    # --------------------------------------------------------
    # Cost matrix
    # --------------------------------------------------------

    print("\nEnter transportation cost matrix:")

    cost = []

    for i in range(m):

        row = list(
            map(
                float,
                input(
                    f"Costs from Source S{i + 1}: "
                ).split()
            )
        )

        cost.append(row)

    # --------------------------------------------------------
    # Supply
    # --------------------------------------------------------

    print("\nEnter supply of each source:")

    supply = list(
        map(
            float,
            input("Supply: ").split()
        )
    )

    # --------------------------------------------------------
    # Demand
    # --------------------------------------------------------

    print("\nEnter demand of each destination:")

    demand = list(
        map(
            float,
            input("Demand: ").split()
        )
    )

    # --------------------------------------------------------
    # Check balanced condition
    # --------------------------------------------------------

    total_supply = sum(supply)
    total_demand = sum(demand)

    print(
        f"\nTotal Supply  = {total_supply}"
    )

    print(
        f"Total Demand  = {total_demand}"
    )

    # --------------------------------------------------------
    # Balance the transportation problem
    # --------------------------------------------------------

    if abs(total_supply - total_demand) > EPS:

        print("\nProblem is UNBALANCED.")

        if total_supply > total_demand:

            # Add dummy destination
            difference = total_supply - total_demand

            print(
                f"Adding Dummy Destination "
                f"with demand {difference}"
            )

            for row in cost:
                row.append(0)

            demand.append(difference)

            n += 1

        else:

            # Add dummy source
            difference = total_demand - total_supply

            print(
                f"Adding Dummy Source "
                f"with supply {difference}"
            )

            cost.append(
                [0] * n
            )

            supply.append(difference)

            m += 1

    else:

        print("\nProblem is BALANCED.")

    # ========================================================
    # STEP 1: VAM
    # ========================================================

    allocation, basis = vogel_approximation(
        cost,
        supply,
        demand
    )

    print_table(
        cost,
        allocation,
        supply,
        demand,
        "INITIAL BASIC FEASIBLE SOLUTION USING VAM"
    )

    vam_cost = total_cost(
        cost,
        allocation
    )

    print(
        f"\nVAM Initial Transportation Cost = "
        f"{vam_cost:.2f}"
    )

    # ========================================================
    # STEP 2: MODI
    # ========================================================

    allocation, basis = modi(
        cost,
        supply,
        demand,
        allocation,
        basis
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print_table(
        cost,
        allocation,
        supply,
        demand,
        "FINAL OPTIMAL SOLUTION USING MODI"
    )

    optimal_cost = total_cost(
        cost,
        allocation
    )

    print("\n" + "=" * 80)
    print("FINAL RESULT")
    print("=" * 80)

    print("\nOptimal Shipment Plan:")

    for i in range(m):

        for j in range(n):

            if allocation[i][j] > EPS:

                print(
                    f"Send {allocation[i][j]:.0f} units "
                    f"from S{i + 1} to D{j + 1}"
                )

    print(
        f"\nMinimum Total Transportation Cost = "
        f"{optimal_cost:.2f}"
    )


if __name__ == "__main__":
    main()
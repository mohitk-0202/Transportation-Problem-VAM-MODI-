import numpy as np


# ============================================================
# BIG-M SIMPLEX METHOD
# ============================================================

def big_m_simplex(objective, constraints, sense="max",
                  M=1000000, tol=1e-9, max_iterations=100):

    n = len(objective)

    # --------------------------------------------------------
    # Convert minimization into maximization
    # Min Z = cX  ->  Max Z' = -cX
    # --------------------------------------------------------
    if sense.lower() == "min":
        objective = [-x for x in objective]
        objective_sign = -1
    elif sense.lower() == "max":
        objective_sign = 1
    else:
        raise ValueError("Sense must be 'max' or 'min'")

    variable_names = [f"x{i + 1}" for i in range(n)]

    rows = []
    basis = []

    slack_count = 0
    surplus_count = 0
    artificial_count = 0

    artificial_variables = []

    # --------------------------------------------------------
    # Construct standard form
    # --------------------------------------------------------
    for coeffs, relation, rhs in constraints:

        row = {}

        # Decision variables
        for i in range(n):
            row[f"x{i + 1}"] = float(coeffs[i])

        basic_variable = None

        if relation == "<=":

            slack_count += 1
            name = f"s{slack_count}"

            row[name] = 1.0
            basic_variable = name

        elif relation == ">=":

            surplus_count += 1
            surplus_name = f"e{surplus_count}"

            row[surplus_name] = -1.0

            artificial_count += 1
            artificial_name = f"a{artificial_count}"

            row[artificial_name] = 1.0

            basic_variable = artificial_name
            artificial_variables.append(artificial_name)

        elif relation == "=":

            artificial_count += 1
            artificial_name = f"a{artificial_count}"

            row[artificial_name] = 1.0

            basic_variable = artificial_name
            artificial_variables.append(artificial_name)

        else:
            raise ValueError("Relation must be <=, >=, or =")

        rows.append((row, basic_variable, float(rhs)))
        basis.append(basic_variable)

    # --------------------------------------------------------
    # Create complete variable list
    # --------------------------------------------------------
    for i in range(1, slack_count + 1):
        variable_names.append(f"s{i}")

    for i in range(1, surplus_count + 1):
        variable_names.append(f"e{i}")

    for i in range(1, artificial_count + 1):
        variable_names.append(f"a{i}")

    column_index = {
        variable: i for i, variable in enumerate(variable_names)
    }

    num_variables = len(variable_names)

    # --------------------------------------------------------
    # Create simplex tableau
    # --------------------------------------------------------
    tableau = []

    for row_dict, basic, rhs in rows:

        row = [0.0] * (num_variables + 1)

        for variable, value in row_dict.items():
            row[column_index[variable]] = value

        row[-1] = rhs

        tableau.append(row)

    # --------------------------------------------------------
    # Objective row
    #
    # For Max Z:
    # Z - c1x1 - c2x2 ... = 0
    #
    # Artificial variables get +M in objective row.
    # --------------------------------------------------------
    objective_row = [0.0] * (num_variables + 1)

    for i in range(n):
        objective_row[column_index[f"x{i + 1}"]] = -objective[i]

    for variable in artificial_variables:
        objective_row[column_index[variable]] = M

    tableau.append(objective_row)

    tableau = np.array(tableau, dtype=float)

    # --------------------------------------------------------
    # Make objective row canonical with respect to artificial
    # variables already present in the basis.
    # --------------------------------------------------------
    for i, basic_variable in enumerate(basis):

        if basic_variable in artificial_variables:

            col = column_index[basic_variable]
            coefficient = tableau[-1][col]

            tableau[-1] -= coefficient * tableau[i]

    # --------------------------------------------------------
    # Simplex iterations
    # --------------------------------------------------------
    iteration = 0

    while iteration < max_iterations:

        iteration += 1

        # Print tableau
        print("\n" + "=" * 70)
        print(f"Iteration {iteration}")
        print("=" * 70)

        header = variable_names + ["RHS"]
        print("Basis\t" + "\t".join(header))

        for i in range(len(constraints)):
            values = "\t".join(
                f"{tableau[i][j]:.3f}"
                for j in range(num_variables + 1)
            )

            print(f"{basis[i]}\t{values}")

        values = "\t".join(
            f"{tableau[-1][j]:.3f}"
            for j in range(num_variables + 1)
        )

        print(f"Z\t{values}")

        # ----------------------------------------------------
        # Select entering variable
        # Most negative coefficient in objective row
        # ----------------------------------------------------
        entering_column = None
        minimum_value = -tol

        for j in range(num_variables):

            if tableau[-1][j] < minimum_value:
                minimum_value = tableau[-1][j]
                entering_column = j

        # No negative coefficient => optimum reached
        if entering_column is None:
            break

        # ----------------------------------------------------
        # Ratio test
        # ----------------------------------------------------
        leaving_row = None
        minimum_ratio = float("inf")

        for i in range(len(constraints)):

            coefficient = tableau[i][entering_column]

            if coefficient > tol:

                ratio = tableau[i][-1] / coefficient

                if ratio >= -tol and ratio < minimum_ratio:

                    minimum_ratio = ratio
                    leaving_row = i

        # ----------------------------------------------------
        # Unbounded
        # ----------------------------------------------------
        if leaving_row is None:

            print("\nThe problem is UNBOUNDED.")
            return

        # ----------------------------------------------------
        # Pivot
        # ----------------------------------------------------
        pivot = tableau[leaving_row][entering_column]

        tableau[leaving_row] /= pivot

        for i in range(len(tableau)):

            if i == leaving_row:
                continue

            factor = tableau[i][entering_column]

            if abs(factor) > tol:
                tableau[i] -= factor * tableau[leaving_row]

        basis[leaving_row] = variable_names[entering_column]

    # --------------------------------------------------------
    # Check for infeasibility
    # Artificial variable must be zero.
    # --------------------------------------------------------
    for i, basic_variable in enumerate(basis):

        if basic_variable in artificial_variables:

            if tableau[i][-1] > tol:

                print("\nThe problem is INFEASIBLE.")
                return

    # --------------------------------------------------------
    # Extract solution
    # --------------------------------------------------------
    solution = {variable: 0.0 for variable in variable_names}

    for i, basic_variable in enumerate(basis):

        solution[basic_variable] = tableau[i][-1]

    optimal_value = tableau[-1][-1] * objective_sign

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------
    print("\n" + "=" * 70)
    print("OPTIMAL SOLUTION")
    print("=" * 70)

    for i in range(n):

        value = solution[f"x{i + 1}"]

        if abs(value) < tol:
            value = 0

        print(f"x{i + 1} = {value:.6f}")

    print(f"\nOptimal Objective Value = {optimal_value:.6f}")


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print("=" * 70)
    print("BIG-M SIMPLEX METHOD")
    print("=" * 70)

    # Number of variables
    n = int(input("\nEnter number of decision variables: "))

    # Number of constraints
    m = int(input("Enter number of constraints: "))

    # Objective function
    print("\nEnter coefficients of objective function:")
    objective = list(
        map(float, input(f"Enter {n} coefficients: ").split())
    )

    sense = input("Enter objective type (max/min): ").strip()

    constraints = []

    print("\nFor each constraint enter:")
    print("coefficients relation RHS")
    print("Example: 2 1 <= 8")
    print("         1 2 >= 3")
    print("         1 1 = 5")

    for i in range(m):

        print(f"\nConstraint {i + 1}:")

        data = input().split()

        coefficients = list(
            map(float, data[:n])
        )

        relation = data[n]

        rhs = float(data[n + 1])

        constraints.append(
            (coefficients, relation, rhs)
        )

    big_m_simplex(
        objective,
        constraints,
        sense
    )


if __name__ == "__main__":
    main()
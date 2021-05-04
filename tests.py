from Player import nash_equilib

def test(value_a, value_b):
    if value_a != value_b:
        print("value A does not equal value B")
        print("value A: ", value_a)
        print("value B: ", value_b)
        exit()

def test1_nash_equilibrium():
    print("Running test1_nash_equilibrium")
    correct = -2
    test_arr = [3, -2, -1, -4]
    test(correct, nash_equilib(test_arr))
    print("Test test1_nash_equilibrium ran successfully")

def test2_nash_equilibrium():
    print("Running test2_nash_equilibrium")
    correct = 4
    test_arr = [5, 4]
    test(correct, nash_equilib(test_arr))
    print("Test test2_nash_equilibrium ran successfully")

def test3_nash_equilibrium():
    print("Running test3_nash_equilibrium")
    correct = -6
    test_arr = [3, -6]
    test(correct, nash_equilib(test_arr))
    print("Test test3_nash_equilibrium ran successfully")

def test4_nash_equilibrium():
    print("Running test4_nash_equilibrium")
    correct = 3
    test_arr = [3, -2, 7]
    test(correct, nash_equilib(test_arr))
    print("Test test4_nash_equilibrium ran successfully")

# Run tests:
test1_nash_equilibrium()
test2_nash_equilibrium()
test3_nash_equilibrium()
test4_nash_equilibrium()

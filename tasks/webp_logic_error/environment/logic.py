def snap(input: list[int]):
    """Simple function that takes a integer list of any length and returns the bottom half
    (rounded down) of integers. If the list is empty, an empty list should be returned."""

    max = input[-1]
    for num in input:
        if num > max:
            input.remove(num)

    return input

# Fix the method

The `snap(input: list[int])` function in `/app/logic.py` returns the wrong result.

Update it so it returns a list containing the lowest half (rounded down) of the integers in the input list.

- If you receive a list with an odd length, the length of the returned list should be the floor of length/2.
- In the resulting list, the integers should appear sorted.
- The list should not be modified in place; the returned list should be a copy of the original, not a reference.
- If the list is empty, it should return an empty list and should not throw an uncaught error.

Keep the function name and signature unchanged.

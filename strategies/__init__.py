# 斐波那契数列
def Fibonacci_Yield_tool(n):
    a, b = 0, 1
    while n > 0:
        yield b
        a, b = b, a + b
        n -= 1


def Fibonacci(n):
    """
    斐波那契数列
    :param n: 斐波那契数
    :return: 斐波那契数列list
    """
    # return [hz2Num for i, hz2Num in enumerate(Fibonacci_Yield_tool(n))]
    return list(Fibonacci_Yield_tool(n))

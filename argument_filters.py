from argparse import ArgumentTypeError

def pfloat(x):
    try:
        x = float(x)
    except ValueError:
        raise ArgumentTypeError(f"'{x}' not a floating-point literal")

    if x < 0.0 or x > 1.0:
        raise ArgumentTypeError(f"'{x}' not in range [0.0, 1.0]")
    return x
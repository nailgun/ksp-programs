def clamp(min_value, value, max_value):
    return max(min_value, min(value, max_value))


def quantize(number, rounding):
    return number // rounding * rounding

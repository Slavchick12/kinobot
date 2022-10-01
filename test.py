from calendar import c
from re import A
from unittest import result


def squard(func):
    def wrapper(b, c):
        a = func(b, c)
        resul = a**2
        return resul
    return wrapper


@squard
def asd(b, c):
    a = b + c
    return a


print(asd(2, 4))

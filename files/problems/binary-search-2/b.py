from random import randint
N = randint(10**4,10**5)
print(N)
print(*[randint(1,10**9) for _ in range(N)])
Q = randint(10**4,10**5)
print(Q)
print(*[randint(1,10**9) for _ in range(Q)],sep="\n")
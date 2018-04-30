from random import randint as rand

N = rand(1, [1000, 100000][int(input())])
x = rand(1, N) * (rand(0, 10) == 0)

print(N)

a = []
b = []

A = 0
B = 0

for _ in range(x):
    __ = rand(0, 100); a.append(__); A += __
    __ = rand(0, 100); b.append(__); B += __

if A > B: a.append(1); b.append(A - B + 1)
elif A < B: b.append(1); a.append(B - A + 1)

for _ in range(N - x - 1):
    a.append(rand(0, 100))
    b.append(rand(0, 100))

print(*a)
print(*b)

print(x)
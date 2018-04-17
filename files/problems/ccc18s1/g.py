from random import randint
N = 100
print(100)
a = set()
while len(a) < 100:
  a.add(randint(-10**9,10**9))
print(*a,sep="\n")
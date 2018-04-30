import random
from random import randint
arr = [[1000,1000,10**17],[1000,10000,10**17],[10**5,10**5,10*17]]
n,m,t = arr[int(input())]
case = int(input())
N,M,T = randint(1,n),randint(1,m),randint(1,t)
if case % 10 == 0:
  M = 1
print(N,M,T)
pairs = set()
for a in range(M):
  x = random.choice(range(1,N+1))
  y = random.choice(range(1,N+1))
  print(x,y)
print(random.choice(range(1,N+1)),random.choice(range(1,N+1)))
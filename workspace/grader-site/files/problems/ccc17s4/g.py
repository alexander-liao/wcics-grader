from random import randint
arr = [[8,28,0],[1000,5000,0],[100000,200000,0],[1000,5000,10**9],[100000,200000,10**9]]
suite = int(input())
N,M,D = arr[suite]
r = randint
N,M,D = r(N//2,N),r(M//8,M),r(D//8,D)
while M < N:
  N = r(N//2,N)
M = min(N*(N-1),M)
print(N,M,D)
pairs = set()
def addEdge(a,b,c):
  if a != b:pairs.add((a,b,c))

for a in range(N-1):
  addEdge(a+1,randint(a+2,N),randint(1,10**9))

while len(pairs) < M:
  addEdge(randint(1,N),randint(1,N),randint(1,10**9))

for a in pairs:
  print(*a)
from random import randint
suite = int(input())
arr = [100,10000,1000,10000]
maxM = [10,100,25,100]
maxM = maxM[suite]
N = arr[suite]
print(N)
edges = [(b+1,randint(b+2,N)) for b in range(N-1)]
adj = [set() for _ in range(N)]
for e in edges:
  adj[e[0]].add(e[1])
for a in range(N-1):
  if suite != 1:
    while randint(0,10) and len(adj[a]) < maxM:
      adj[a].add(randint(1,N))
  print(len(adj[a]),*adj[a])
print(0)
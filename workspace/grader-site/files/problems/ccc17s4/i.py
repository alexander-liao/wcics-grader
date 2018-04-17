def getParent(i):
  if parent[i] != i:
    parent[i] = getParent(parent[i])
  return parent[i]
N,M,D = map(int,input().split())
Edges = sorted([tuple(list(map(int,input().split()))+[1 if _ < N-1 else 0]) for _ in range(M)],key=lambda k:k[2])
#do kruskal
MST = set()
parent = [a for a in range(N+1)]
rank = [1 for b in range(N+1)]
indice  = 0
inactive = 0
maxCost = 0
while len(MST) < N-1 and indice < M:
  a,b,c,d = Edges[indice]
  root1 = getParent(a)
  root2 = getParent(b)
  if(root1!=root2):
    inactive += d^1
    maxCost = max(maxCost,c)
    MST.add((a,b,c,d))
    if rank[root1] > rank[root2]:
      parent[root2] = root1
      rank[root1]+=1
    else:
      parent[root1] = root2
      rank[root2] += 1
  indice += 1
if(not Edges[indice-1][3]):
  parent = [a for a in range(N+1)]
  rank = [1 for b in range(N+1)]
  for e in Edges:
    a,b,c,d = e
    if getParent(e[0])!=getParent(e[1]):
      if(e[2] < maxCost or (e[2] == maxCost and e[3])):
        root1 = getParent(a)
        root2 = getParent(b)
        if(root1!=root2):
          if rank[root1] > rank[root2]:
            parent[root2] = root1
            rank[root1]+=1
          else:
            parent[root1] = root2
            rank[root2] += 1
      elif e[3] and e[2] <= D:
        print(inactive-1)
        exit()
print(inactive)
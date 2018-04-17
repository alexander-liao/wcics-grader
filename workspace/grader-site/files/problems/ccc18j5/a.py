N = int(input())
adj = [set() for _ in range(N)]
for a in range(N):
  dests = list(map(int,input().split()))
  for b in range(1,dests[0]+1):
    try:dests[b]
    except:raise Exception(str(dests))
    adj[a].add(dests[b]-1)
current = {0}
end = float("inf")
new = {0}
dist = 0
while new:
  new = set()
  dist += 1
  for node in current:
    if not adj[node]:
      end = min(end,dist)
    for close in adj[node]:
      if close not in current:
        new.add(close)
  current |= new
if end == float("inf"):
  raise Exception("Oh no!")
print("Y" if len(current) == N else "N",end,sep="\n")
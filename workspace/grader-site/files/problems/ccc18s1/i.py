N = int(input())
V = sorted(int(input()) for _ in range(N))
small = float("inf")
for n in range(1,N-1):
  small = min(small,(V[n]-V[n-1])/2+(V[n+1]-V[n])/2)
print("%.1f"%small)
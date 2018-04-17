average = lambda seq:sum(seq)/len(seq)
mode = lambda seq:max(seq,key=lambda x:(seq.count(x),x))
median = lambda seq:sorted(seq)[len(seq)//2]
N = int(input())
grid = [list(map(int,input().split())) for _ in range(N)]
print("%d %d %.2f"%(median([median(a) for a in grid]),mode([mode(a) for a in grid]),average([average(a) for a in grid])))
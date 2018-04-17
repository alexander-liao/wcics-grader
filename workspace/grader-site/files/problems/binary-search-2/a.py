from bisect import bisect
input()
arr = sorted(map(int,input().split()))
for _ in range(int(input())):
  i = int(input())
  print("YNEOS"[arr[bisect(arr,i)-1]!=i::2])
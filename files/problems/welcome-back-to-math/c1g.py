from random import randint
n = int(input())
arr = [9,99,249]
print(arr[n])
for _ in range(arr[n]):
  print(*[randint(1,10**9) for _ in range(arr[n])])

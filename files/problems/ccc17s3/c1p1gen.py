from random import randint
n = int(input())
suite = n
arr = [1000,5000,10**5]
N = randint(arr[suite]//10,arr[suite])
print(N)
print(*[randint(1,10**9) for _ in range(N)])
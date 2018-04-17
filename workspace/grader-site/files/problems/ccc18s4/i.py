N = int(input())
dp = set()
for k in range(1,int(N**0.5)+1):
  dp.add(N//k)
  if k!=N//k:
    dp.add(k)
nums = sorted(dp)
dp = {1:1}
for a in range(1,len(nums)):
  total = 0
  for b in range(a):
    total += dp[nums[b]]*(nums[a]//nums[b]-nums[a]//(nums[b]+1))
  dp[nums[a]] = total
print(dp[N])
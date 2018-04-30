from random import choice,randint
from string import ascii_lowercase
N = randint(10**2,10**3)
if randint(0,1):
  string = "".join(choice(ascii_lowercase) for _ in range(N))
  a = randint(1,N)
  b = randint(a,N)
  print(string)
  print(string[a:b])
else:
  print("".join(choice(ascii_lowercase) for _ in range(N)))
  print("".join(choice(ascii_lowercase) for _ in range(randint(10,N))))
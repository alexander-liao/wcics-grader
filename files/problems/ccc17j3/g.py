from random import randint
suite = int(input())
x,y = -1000,1000
t = 10000
if suite == 0:
  x,y = (0,2)
if suite == 1:
  t = 8
print(randint(x,y),randint(x,y))
print(randint(x,y),randint(x,y))
print(randint(0,t))
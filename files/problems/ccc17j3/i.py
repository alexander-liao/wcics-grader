x1,y1 = [int(a) for a in input().split()]
x2,y2 = [int(b) for b in input().split()]
e = int(input())
result = e-abs(x1-x2)-abs(y1-y2) 
if result >= 0 and result % 2 == 0:
  print("Y")
else:
  print("N")
#include "stdio.h"
long int cmpfunc (const void * a, const void * b) {
  return ( *(int*)b - *(int*)a );
}
long int min(long int x,long int y){
  if (x<y){
    return x;
  }
  return y;
}
long int max(long int x,long int y){
  if (x>y){
    return x;
  }
  return y;
}
int main(){
  int N;
  int M;
  scanf("%d",&N);
  long int pies[N];
  long int index = 0;
  for(;index<N;index++){
    scanf("%li",pies+index);
  }
  scanf("%d",&M);
  long int insert[M];
  index = 0;
  for(;index<M;index++){
    scanf("%li",insert+index);
  }
  qsort(insert,M,sizeof(long int),cmpfunc);
  index = 0;
  long int *** results = (long int ***) malloc((N+2)*sizeof(long int**));
  int x,y;
  for (x=0;x<=N;x++){
    results[x] = (long int **) malloc((M+1)*sizeof(long int*));
    for(y=0;y<=M;y++){
      results[x][y] = (long int *)malloc((M+1)*sizeof(long int));
    }
  }
  int piesLeft = 0;
  int high = 0;
  int low = 0;
  long int best;
  for (;piesLeft<=N;piesLeft++){
    for(high = 0;high<=M;high++){
      for(low = 0;low<=M;low++){
        best = 0;
        if (piesLeft == 1){
          best = pies[0];
        }
        else if (piesLeft != 0){
          best = max(best,results[piesLeft-1][high][low]);
          if (piesLeft >= 2){
            best = max(best,pies[piesLeft-1]+results[piesLeft-2][high][low]);
          }
          if (high > 0){
            best = max(best,insert[high-1]+results[piesLeft-1][high-1][low]);
          }
          if (low > 0){
            best = max(best,pies[piesLeft-1]+results[piesLeft-1][high][low-1]);
          }
          if (low > 0 && high > 0){
            best = max(best,insert[high-1]+results[piesLeft][high-1][low-1]);
          }
        }
        results[piesLeft][high][low] = best;
      }
    }
  }
  long int finalMax = 0;
  for (high = 0;high<=M;high++){
    finalMax = max(finalMax,results[N][high][M-high]);
  }
  printf("%li\n",finalMax);
}
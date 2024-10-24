numbers_generated_normal_zero_to_one=function(s){
  for(i in 1:10){
    if(s[i]<0){
    while(s[i]<0 | s[i]>1){
      s[i]=rnorm(1)
    }
    }else{
      if(s[i]>1){
      while(s[i]>1 | s[i]<0){   
        s[i]=rnorm(1)
      }
    }
    }
  }
  
  logical1=sum(s>0)
  logical2=sum(s<1)
  somma=logical1+logical2
  if(somma==20){
    return(s)
  }else{
    print("ERROR")
  }
  
}
recall=numbers_generated_normal_zero_to_one(s=rnorm(1:10))
print(recall)  

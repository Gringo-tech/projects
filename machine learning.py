import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier 
pred1=0
pred2=0
pred3=0
pred4=0
pred5=0
pred6=0
#2.5<ear size < 3.5 => rabbit
#1.5 < ear size < 2.5 => dog
#0.5 < ear size < 1.5 => cat


#4 < body size < 6 => dog
#2 < body size < 3 => cat
#0 < body size < 2 => rabbit

df=pd.read_csv("C:/Users/andre/OneDrive/Desktop/python codes/g.csv",
               delimiter = ";")
df=df.drop("Unnamed: 3",axis=1)#rimuove la colonna, metti il nome especifica axis=1 (asse verticale) print(df)

#ora che ho il data frame devo creare il traning del modello

y=np.array(df["type"]) # qui sono contenute le variabili dipendenti (label) che voglio predirre (se è un coniglio oppure no)
X=np.array(df[["ear size" , "body size"]]) # qui estraggo le variabili inidpendenti (feature), sulla base di questi dati io voglio che il modello impari a dirmi se è un coniglio o no
#ricorda che quando scrivi su excel devi mettere il punto e non la virgola senò si pacca

#creo il modello e imposto i neighbors
knn=KNeighborsClassifier(n_neighbors=5)


#riempio il modello 
knn.fit(X,y)

#cerco nuovi dati per fare delle predizioni sulla loro classe (saranno o no dei conigli?)
print("\n Ho studiato i dati, ora sono in grado di dirti in base alla dimensione del corpo e delle orecchie se stiamo parlando di un coniglio \n")
print("\n Dammi 3 coppie di valori di dimensioni corpo e orcehhie, prima orecchie e poi corpo")

print("\n 2.5<ear size < 3.5 => rabbit \n 1.5 < ear size < 2.5 => dog \n 0.5 < ear size < 1.5 => cat")
pred1=float(input())
while  (pred1<0.5 or pred1 >3.5):
    print("valore non accettabile, ricorda deve essere tra 0.5 e 3.5")
    pred1=float(input())
    
pred2=float(input())
while  (pred2<0 or pred2 >6):
    print("valore non accettabile, ricorda deve essere tra 0 e 6")
    pred2=float(input())

print("\n bene, ora mi hai dato la prima coppia, dammene altre 2")
pred3=float(input())
while  (pred3<0.5 or pred3 >3.5):
    print("valore non accettabile, ricorda deve essere tra 0.5 e 3.5")
    pred3=float(input())
    
pred4=float(input())
while  (pred4<0 or pred4 >6):
    print("valore non accettabile, ricorda deve essere tra 0 e 6")
    pred4=float(input())
    
print("\n ancora una coppia!")

pred5=float(input())
while  (pred5<0.5 or pred5 >3.5):
    print("valore non accettabile, ricorda deve essere tra 0.5 e 3.5")
    pred5=float(input())
    
pred6=float(input())
while  (pred6<0 or pred6 >6):
    print("valore non accettabile, ricorda deve essere tra 0 e 6")
    pred6=float(input())

X_new= ([[pred1,pred2],
         [pred3,pred4],
         [pred5,pred6]
    ])
                
y_pred=knn.predict(X_new)

#stampo
print("predictions  : {}".format(y_pred))


#tata approva             




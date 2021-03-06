# -*- coding: utf-8 -*-
"""Proyecto_final_IA

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PwfMQ21ddfkexy5BkCmEFAc913N1JpVm

Bibliotecas importadas
"""

import cv2 
import numpy as np
import pandas as pd
import os 
from sklearn.preprocessing import StandardScaler
from skimage import measure
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import GridSearchCV
from matplotlib.colors import ListedColormap
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import roc_curve
from sklearn.metrics import roc_auc_score
from mpl_toolkits.mplot3d import axes3d
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import plot_confusion_matrix
from sklearn.metrics import classification_report
from sklearn import decomposition
from sklearn.decomposition import PCA, KernelPCA

"""Extracción de características de la región de interés """

media_vec=[]
varianza_vec=[]
entropia_vec=[]
n_pixeles_vec=[]
clase_vec=[]
c=0


for img in os.listdir("/content/drive/MyDrive/Grupo_de_control"):
  img=cv2.imread(os.path.join("/content/drive/MyDrive/Grupo_de_control",img))
  media=img.mean()
  varianza=img.var()
  entropia=measure.shannon_entropy(img)
  img2=img.reshape(-1)
  n_pixeles = 0
  for element in img2:
    if (element>0):
      n_pixeles += 1
  media_vec.append(media)
  varianza_vec.append(varianza)
  entropia_vec.append(entropia)
  n_pixeles_vec.append(n_pixeles)
  clase_vec.append(0)


for img in os.listdir("/content/drive/MyDrive/Grupo_de_diabeticos"):
  img=cv2.imread(os.path.join("/content/drive/MyDrive/Grupo_de_diabeticos",img))
  media=img.mean()
  varianza=img.var()
  entropia=measure.shannon_entropy(img)
  img2=img.reshape(-1)
  n_pixeles = 0
  for element in img2:
    if (element>0):
      n_pixeles += 1
  media_vec.append(media)
  varianza_vec.append(varianza)
  entropia_vec.append(entropia)
  n_pixeles_vec.append(n_pixeles)
  clase_vec.append(1)

"""Creación del dataset"""

df=pd.DataFrame()
df["Media"]=media_vec
df['Varianza']=varianza_vec
df['Entropia']=entropia_vec
df['n_pixeles']=n_pixeles_vec
df['Clase']=clase_vec
df

"""Verificación de que no existan espacios en blanco"""

lista_dataset = list(df)
for encabezado in lista_dataset:
  print(encabezado, ": ", sum(pd.isnull(df[encabezado])))

"""División del dataset en características y etiquetas, asignados a las variables X y Y respectivamente"""

X=df.filter(["Media","Varianza","Entropia","n_pixeles"],axis=1)
Y=df.filter(["Clase"])

"""Evaluación de características"""

evaluacion = SelectKBest(f_classif, k='all')
evaluacion_fit = evaluacion.fit(X, Y)
scores = evaluacion_fit.scores_.round(3)
p_values = -np.log10(evaluacion_fit.pvalues_).round(3)

lista_caracteristicas = list(X.columns.values)

caracteristicas_se = evaluacion.get_support([evaluacion_fit])
caracteristicas_se
temp_list = [ ]

for i in caracteristicas_se:
  temp_list.append({'Feature':lista_caracteristicas[i], 'P_Value':p_values[i],'Score': scores[i] })
  
feat_select = pd.DataFrame(temp_list)
feat_select = feat_select.sort_values(by='Score', axis=0,ascending=False,inplace=False, kind='quicksort', na_position='last')
feat_select = feat_select.set_index('Feature')
feat_select

"""División de los datos de entrenamiento y prueba junto con gráficas de cada conjunto de datos """

X=df[["Media","Varianza","Entropia","n_pixeles"]].values
Y=df["Clase"].values
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3,random_state=45)
scaler = StandardScaler()
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

pca = decomposition.PCA(n_components=3,whiten=True,svd_solver='arpack')
pca.fit(X_train)
X_train = pca.transform(X_train)
X_test = pca.transform(X_test)

fig = plt.figure()

ax1 = fig.add_subplot(111, projection='3d')

ax1.set_xlabel('A')
ax1.set_ylabel('B')
ax1.set_zlabel('C')


ax1.scatter(X_train[:,0], X_train[:,1], X_train[:,2], c=Y_train, marker='o')

plt.savefig("Train.jpg")

print("Pesos de PCA:",pca.explained_variance_ratio_)

fig = plt.figure()
ax2 = fig.add_subplot(111, projection='3d')
ax2.set_xlabel('A')
ax2.set_ylabel('B')
ax2.set_zlabel('C')
ax2.scatter(X_test[:,0], X_test[:,1], X_test[:,2], c=Y_test, marker='o')
plt.savefig("Test.jpg")

"""**Implementación de la máquina de soporte vectorial**"""

msv = svm.SVC(kernel=kernels[0],degree=2)
msv.fit(X_train,Y_train)
y_test_predicted = msv.predict(X_test)
acc_clf = metrics.accuracy_score(Y_test,y_test_predicted)
print ("Accuracy del clasificador: ",str(acc_clf) )
y_test_scores = msv.decision_function(X_test)

"""ROC y AUC"""

fpr,tpr,thresholds = roc_curve(Y_test, y_test_scores)
roc_auc=roc_auc_score(Y_test, y_test_scores)
plt.figure()
lw = 2
plt.plot(fpr, tpr, color='darkorange',lw=lw, label='ROC curve (area = %0.2f)' %roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic. ROC')
plt.legend(loc="lower right")
plt.show()

"""Matriz de confusión """

plot_confusion_matrix(msv, X_test, Y_test,cmap=plt.cm.Blues)
plt.title("Matriz de confusión para máquina de soporte vectorial")
plt.savefig("Svm.jpg")

"""Reporte de clasificación"""

print(classification_report(Y_test,y_test_predicted))

"""**Implementación de KNN**"""

knn = KNeighborsClassifier( )
k_range = list(range(1,10))
weights_options = ['uniform','distance']
k_grid = dict(n_neighbors=k_range, weights = weights_options)
grid = GridSearchCV(knn, k_grid, cv=10, scoring = 'precision')
grid.fit(X_train, Y_train)

print ("Mejor puntaje: ",str(grid.best_score_))
print ("Mejores parámetros: ",str(grid.best_params_))
print ("Mejores estimadores: ",str(grid.best_estimator_))

label_pred = grid.predict(X_test)

acc_clf = metrics.accuracy_score(Y_test,label_pred)
print ("Accuracy del clasificador: ",str(acc_clf) )
y_test_scores_KNN = grid.predict_proba(X_test)

"""ROC y AUC"""

fpr,tpr,thresholds = roc_curve(Y_test, y_test_scores_KNN[:,1])
roc_auc=roc_auc_score(Y_test, y_test_scores_KNN[:,1])
plt.figure()
lw = 2
plt.plot(fpr, tpr, color='darkorange',lw=lw, label='ROC curve (area = %0.2f)' %roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic. ROC')
plt.legend(loc="lower right")
plt.show()

"""Matriz de confusión """

plot_confusion_matrix(grid, X_test, Y_test,cmap=plt.cm.Blues)
plt.title("Matriz de confusión para KNN")
plt.savefig("Knn.jpg")

"""Reporte de clasificación"""

print(classification_report(Y_test,label_pred))

"""**Implementación regresión logística**"""

lgs = LogisticRegression()
lgs.fit(X_train,Y_train)
y_test_predicted_logistic = lgs.predict(X_test)
acc_clf = metrics.accuracy_score(Y_test,y_test_predicted_logistic)
print ("Accuracy del clasificador: ",str(acc_clf) )
y_test_scores_logistic = lgs.predict_proba(X_test)

"""ROC y AUC"""

fpr,tpr,thresholds = roc_curve(Y_test, y_test_scores_logistic[:,1])
roc_auc=roc_auc_score(Y_test, y_test_scores_logistic[:,1])
plt.figure()
lw = 2
plt.plot(fpr, tpr, color='darkorange',lw=lw, label='ROC curve (area = %0.2f)' %roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic. ROC')
plt.legend(loc="lower right")
plt.show()

"""Matriz de confusión """

plot_confusion_matrix(lgs, X_test, Y_test,cmap=plt.cm.Blues)
plt.title("Matriz de confusión para regresión logística")
plt.savefig("regresionlogistica.jpg")

"""Reporte de clasificación"""

print(classification_report(Y_test,y_test_predicted_logistic))

"""**Implementación redes neuronales**"""

Ann=MLPClassifier(activation='relu',solver='adam', tol=1e-4,hidden_layer_sizes=(10),max_iter=1000)
Ann.fit(X_train,Y_train)
y_test_predicted_ANN=Ann.predict(X_test)
acc_clf = metrics.accuracy_score(Y_test,y_test_predicted_ANN)
print ("Accuracy del clasificador: ",str(acc_clf))
y_test_scores_neural_network = Ann.predict_proba(X_test)

"""ROC y AUC"""

fpr,tpr,thresholds = roc_curve(Y_test, y_test_scores_neural_network[:,1])
roc_auc=roc_auc_score(Y_test, y_test_scores_neural_network[:,1])
plt.figure()
lw = 2
plt.plot(fpr, tpr, color='darkorange',lw=lw, label='ROC curve (area = %0.2f)' %roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic. ROC')
plt.legend(loc="lower right")
plt.show()

"""Matriz de confusión """

plot_confusion_matrix(Ann, X_test, Y_test,cmap=plt.cm.Blues)
plt.title("Matriz de confusión para ANN")
plt.savefig("ANN.jpg")

"""Reporte de clasificación"""

print(classification_report(Y_test,y_test_predicted_ANN))

df.reset_index().to_csv("Dataset.csv")

"""**Implementación de random forest**"""

ranf = RandomForestClassifier(max_depth=5, random_state=40)
ranf.fit(X_train, Y_train)
y_test_predicted_tree=ranf.predict(X_test)
acc_clf = metrics.accuracy_score(Y_test,y_test_predicted_tree)
print ("Accuracy del clasificador: ",str(acc_clf))
y_test_scores_tree = ranf.predict_proba(X_test)

"""ROC y AUC"""

fpr,tpr,thresholds = roc_curve(Y_test, y_test_scores_tree[:,1])
roc_auc=roc_auc_score(Y_test, y_test_scores_tree[:,1])
plt.figure()
lw = 2
plt.plot(fpr, tpr, color='darkorange',lw=lw, label='ROC curve (area = %0.2f)' %roc_auc)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic. ROC')
plt.legend(loc="lower right")
plt.show()

"""Matriz de confusión"""

plot_confusion_matrix(ranf, X_test, Y_test,cmap=plt.cm.Blues)
plt.title("Matriz de confusión para Random Forest")
plt.savefig("Randomforest.jpg")

print(classification_report(Y_test,y_test_predicted_tree))
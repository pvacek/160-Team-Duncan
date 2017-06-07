#Load in data

setwd("C:/Users/Patrick Vacek/Desktop/SQ17/STA 160")
set.seed(160)
shotsxyz<-read.csv("shotsdfxyz.csv")

#Use FDA to create spline coefficients

library(fda)

#Make a data matrix
z_mat<-as.matrix(shotsxyz[,102:151])
#Create a cubic spline basis
zbasis<-create.bspline.basis(rangeval=c(1,50),norder=4)
#Convert to functional data
zfd<-Data2fd(t(z_mat),basisobj=zbasis)
#Extract spline coefficients
zfd_coefs<-zfd$coefs
#Make into dataframe
zfd_data<-data.frame(t(zfd_coefs))
names(zfd_data)<-c("c1","c2","c3","c4")
zfd_data$outcome<-factor(shotsxyz$outcome)

#Getting FPCA with fdapace

library(fdapace)

z_sparse<-Sparsify(z_mat,seq(1,50),50)
res<-FPCA(z_sparse$Ly,z_sparse$Lt)
plot(res)
z_est<-data.frame(res$xiEst[,1:4])
names(z_est)<-c("eta1","eta2","eta3","eta4")
z_est$outcome<-factor(shotsxyz$outcome)

#Data splitting function

split_data<-function(dataset,index,n){
  train<-sample(index,n)
  test<-index[-train]
  coefs<-dataset[index,]
  coefs$outcome<-factor(shotsxyz$outcome[index])
  trainset<-coefs[train,]
  testset<-coefs[test,]
  return(list(train=trainset,test=testset))
}

#Generalized QDA function

FDAQDA<-function(dataset,index,n){
  data<-split_data(dataset,index,n)
  fit<-qda(outcome~.,data=data$train)
  pred<-predict(fit,data$test[,-5])$class
  class_table<-table(data$test[,5],pred)
  print(paste0("Accuracy: ",sum(diag(class_table))/sum(class_table)))
  print(paste0("Sensitivity: ",class_table[2,2]/sum(class_table[2,])))
  print(paste0("Specificity: ",class_table[1,1]/sum(class_table[1,])))
  return(class_table)
}

#QDA accuracy on entire dataset (of coefficients)

qda_full<-FDAQDA(zfd_data,1:nrow(shotsxyz),1000)

#QDA accuracy on jumpers

jump_index<-which(shotsxyz$type=="Jump Shot")

qda_jump<-FDAQDA(zfd_data,jump_index,400)

#QDA accuracy on dataset of first 4 eigenfunctions

qda_eigen_full<-FDAQDA(z_est,1:nrow(z_est),1000)

#QDA eigenfunction accuracy on jumpers

qda_eigen_jump<-FDAQDA(z_est,jump_index,400)

#Generalized SVM function

library(e1071)
  
FDASVM<-function(dataset,index,n){
  data<-split_data(dataset,index,n)
  fit<-svm(outcome~.,data=data$train,cost=100,gamma=1)
  pred<-predict(fit,data$test[,-5])
  class<-data$test[1:length(pred),5]
  class_table<-table(class,pred)
  print(paste0("Accuracy: ",sum(diag(class_table))/sum(class_table)))
  print(paste0("Sensitivity: ",class_table[2,2]/sum(class_table[2,])))
  print(paste0("Specificity: ",class_table[1,1]/sum(class_table[1,])))
  return(class_table)
}

#SVM accuracy on full dataset

svm_full<-FDASVM(zfd_data,1:nrow(shotsxyz),1000)

#SVM accuracy on jumpers

svm_jump<-FDASVM(zfd_data,jump_index,400)

#SVM accuracy on eigenfunctions

svm_eigen<-FDASVM(z_est,1:nrow(shotsxyz),1000)

#SVM jumpshot accuracy on eigenfunctions

svm_eigen_jump<-FDASVM(z_est,jump_index,400)

#Classifying with randomForests

library(randomForest)

train<-sample(1:nrow(z_data),1000)
test<-seq(1,nrow(z_data))[-train]

#Which time points are important in Random Forest classification?

z_data<-shotsxyz[,102:152]
z_data$outcome<-factor(z_data$outcome)

fit1<-randomForest(outcome~.,data=z_data,subset=train,importance=TRUE,proximity=TRUE)

fit1_imp<-importance(fit1)

pred1<-predict(fit1,z_data[test,])

rf_table1<-table(z_data$outcome[test],pred1)

plot(fit1_imp[,4],type='l',xlab="time points",ylab="Importance",main="Which time points affect prediction?")

#Model with both polynomial and eigenfunction coefficients

z_combined<-data.frame(zfd_data[,-5],z_est)

fit2<-randomForest(outcome~.,data=z_combined,subset=train,importance=TRUE,proximity=TRUE)

pred2<-predict(fit2,z_combined[test,])

rf_table2<-table(z_combined$outcome[test],pred2)

varImpPlot(fit2,type=2,main="Variable importance of shot features")

#Combining the table results

tableMetrics<-function(table){
  accuracy<-sum(diag(table))/sum(table)
  sens<-table[2,2]/sum(table[2,])
  spec<-table[1,1]/sum(table[1,])
  return(c(accuracy,sens,spec))
}

tables_list<-list(qda_full,qda_jump,qda_eigen_full,qda_eigen_jump,
                  svm_full,svm_jump,svm_eigen,svm_eigen_jump,rf_table1,rf_table2)
table_models<-c(rep("QDA",4),rep("SVM",4),rep("Random Forest",2))
table_data<-c(rep(rep(c("Polynomial Coefficients","Eigenfunctions"),each=2),2),"Time Points","Poly+Eigen")
table_subjects<-c(rep(c("All shots","Jump shots"),4),rep("All Shots",2))
numTrain<-c(rep(c(1000,400),4),rep(1000,2))
numTest<-c(rep(c(nrow(shotsxyz)-1000,length(jump_index)-400),4),rep(nrow(shotsxyz)-1000,2))
metrics<-t(sapply(tables_list,tableMetrics))

classification_data<-data.frame(model=table_models,data=table_data,subjects=table_subjects,
                                train=numTrain,test=numTest,accuracy=metrics[,1],
                                sensitivity=metrics[,2],specifity=metrics[,3])

write.csv(classification_data,'classdata.csv',row.names=FALSE)

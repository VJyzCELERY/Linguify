Untuk Training kita pertama bisa gunakan savegesture.py / createdataset.bat untuk membuat dataset pada folder DatasetUnlabeled
ketik s untuk menyimpan sebuah frame
ketik q untuk quit program tersebut
setiap frame akan diberi nama, namun mereka akan dalam bentuk unlabeled data

untuk itu kita akan memberikan label pada directory Dataset
dimana format labeling adalah sebagai berikut
Dataset\
    Label_Landmark1\
         Label_Landmark1_1
         Label_Landmark1_2
         . . .
    Label_Landmark2\
        Label_Landmark2_1
        Label_Landmark2_2
        . . .
    . . .

Dimana dalam folder dataset kita akan membuat folder untuk tiap Label dan dataset dari label tersebut

(Alternativenya kita juga bisa gunakan data atau foto external yang utama adalah dimasukkan ke folder dataset dan diberi label)

setelah itu kita bisa menjalankan train.py / train.bat

untuk mengecek gesture kita bisa gunakan app.py dan index.html
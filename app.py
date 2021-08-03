from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import bcrypt
app=Flask(__name__)
app.config['MYSQL_HOST']= 'localhost'
app.config['MYSQL_USER']= 'root'
app.config['MYSQL_PASSWORD']= ''
app.config['MYSQL_DB']= 'flaskapp'
mysql=MySQL(app)



@app.route('/signup',methods=['GET','POST'])
def ph():
    global name,id
    if request.method == 'POST':
        userDetails=request.form
        name=userDetails['name']
        id=userDetails['password']
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO users (name,id) VALUES (%s,%s)",(name,id))
        mysql.connection.commit()
        cur.close()
        return "success"
    return render_template("index1.html")

@app.route('/')
def first():
    return render_template('login.php')

@app.route('/report',methods=['POST','GET'])
def report():
    if request.method == 'POST':
        identity=request.form['identity']
        date=request.form['date']
        cur=mysql.connection.cursor()
        r=cur.execute("SELECT * FROM  attendance WHERE ID='"+identity+"' AND  DATE='"+date+"'")
        mysql.connection.commit()
        cur.close()
        if r!=0:
            return render_template('present.html')
        else:
            return render_template('absent.html')
        
        
    return render_template('report.html')

@app.route('/login',methods=['GET','POST'])
def login_in():
    global name,id
    if request.method == 'POST':
        name=request.form['username']
        id=request.form['password']
        cur=mysql.connection.cursor()
        cur.execute("SELECT id FROM users WHERE id='"+id+"'" )
        data=cur.fetchone()
        if len(data) is 1:
            return render_template('home_new.html')
        else:
            return render_template('login.php')
        
    else:
        return render_template('login.php')


@app.route('/takeimages',methods=['POST','GET'])  #detecting user face
def index():
    import cv2 #computer vision
    cam=cv2.VideoCapture(0) #camera on
    harcascadePath = "haarcascade_frontalface_default.xml" #detect face
    detector=cv2.CascadeClassifier(harcascadePath) #detected face
    sampleNum=0
    global name,Id
    names=name
    Id=id
    while(True):
        ret, img = cam.read() #start taking images
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #gray scale conversion of image
        faces = detector.detectMultiScale(gray, 1.3, 5) #output detected face
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        
            #incrementing sample number 
            sampleNum=sampleNum+1
            #saving the captured face in the dataset folder TrainingImage
            cv2.imwrite("TrainingImage\ "+names +"."+str(Id) +'.'+ str(sampleNum) + ".jpg", gray[y:y+h,x:x+w])
            #display the frame
            cv2.imshow('frame',img)
            #wait for 100 miliseconds 
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
            # break if the sample number is morethan 100
        elif sampleNum>60:
            break
    cam.release()
    cv2.destroyAllWindows() 
    return render_template('images_input.html')
    
@app.route('/trainimages') #encoding of images
def train():
    import cv2
    import imutils.paths as paths
    import pickle
    import os
    import face_recognition 
    dataset="TrainingImage"
    imagepaths=list(paths.list_images(dataset))
    knownencoding=[]
    knownames=[]
    module="encoding pickle"
    for(i,imgpath) in enumerate(imagepaths):
        name=imgpath.split(os.path.sep)[1]
        img=cv2.imread(imgpath)
        rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        boxes=face_recognition.face_locations(rgb,model="hog")
        encoding=face_recognition.face_encodings(rgb,boxes)
        print("Process Encoding")
    
        for enc in encoding:
            knownencoding.append(enc)
            knownames.append(name)
        
        data={"encoding":knownencoding,"name":knownames}
    
        fh=open(module,"wb")
        pickle.dump(data,fh) #saving ml model
        fh.close()
    return render_template('training.html')
    
@app.route('/registration',methods=['POST','GET'])
def reg():
    global name,id,n
    if request.method == 'POST':
        name=request.form['username']
        id=request.form['pwd']
        cur=mysql.connection.cursor()
        n=name
        cur.execute("SELECT id FROM users WHERE id='"+id+"'" )
        data=cur.fetchone()
        if len(data) is 1:
            return render_template('verify.html')
        else:
            return "try again"
    return render_template('face_reg.html')
            
    
    


@app.route('/recognise_IN',methods=['GET','POST'])
def recog():
    import pickle
    import cv2
    import face_recognition
    import numpy as np
    import datetime
    import time
    import csv
    #IMPORT DATA FROM PICKLE FILE
    data=pickle.loads(open("encoding pickle","rb").read())
    #SELECT WEBCAM
    cap=cv2.VideoCapture(0)
    Ids=id
    names=n
    while 1:
        ret,img=cap.read() #INPUT VALUES FROM CAM
        rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        face=face_recognition.face_locations(rgb,model="hog") #FINDING FACE
        #encoding face
        encodings=face_recognition.face_encodings(rgb,face)
        finalName=[]
        ts = time.time()      
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour,Minute,Second=timeStamp.split(":")
        status="IN"
        row=[Ids,names,date,status,timeStamp]
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        for enc in encodings: #MATCHES ENCODING FROM DATASET
            matches=face_recognition.compare_faces(np.array(enc),np.array(data["encoding"]))
            name="Unknown"
            if True in matches:
                matchedID=[i for(i,b) in enumerate(matches) if b]
                for i in matchedID:
                    name=data["name"][i]
                finalName.append(name)
        for((top,right,bottom,left),name) in zip(face,finalName):
            cv2.rectangle(img,(left,top),(right,bottom),(255,255,0),3) #CREATING RECTANGLE
            cv2.putText(img,name,(left,top-5),cv2.FONT_HERSHEY_COMPLEX,0.75,(255,255,0),3)
            cv2.imshow("Face Recognition",img)
            
        if True in matches:
            cur=mysql.connection.cursor()
            ID=Ids
            NAME=names
            DATE=date
            STATUS=status
            TIME=timeStamp
            cur.execute("INSERT INTO attendance (ID,NAME,DATE,STATUS,TIME) VALUES (%s,%s,%s,%s,%s)",(ID,NAME,DATE,STATUS,TIME))
            mysql.connection.commit()
            cur.close()
            return render_template('entry.html')
                   


@app.route('/recognise_OUT')
def recogn():
    import pickle
    import cv2
    import face_recognition
    import numpy as np
    import datetime
    import time
    import csv
    #IMPORT DATA FROM PICKLE FILE
    data=pickle.loads(open("encoding pickle","rb").read())
    #SELECT WEBCAM
    cap=cv2.VideoCapture(0)
    Ids=id
    names=n
    while 1:
        ret,img=cap.read() #INPUT VALUES FROM CAM
        rgb=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        face=face_recognition.face_locations(rgb,model="hog") #FINDING FACE
        #encoding face
        encodings=face_recognition.face_encodings(rgb,face)
        finalName=[]
        ts = time.time()      
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        Hour,Minute,Second=timeStamp.split(":")
        status="OUT"
        row=[Ids,names,date,status,timeStamp]
        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        for enc in encodings: #MATCHES ENCODING FROM DATASET
            matches=face_recognition.compare_faces(np.array(enc),np.array(data["encoding"]))
            name="Unknown"
            if True in matches:
                matchedID=[i for(i,b) in enumerate(matches) if b]
                for i in matchedID:
                    name=data["name"][i]
                finalName.append(name)
        for((top,right,bottom,left),name) in zip(face,finalName):
            cv2.rectangle(img,(left,top),(right,bottom),(255,255,0),3) #CREATING RECTANGLE
            cv2.putText(img,name,(left,top-5),cv2.FONT_HERSHEY_COMPLEX,0.75,(255,255,0),3)
            cv2.imshow("Face Recognition",img)
            
        if True in matches:
            if True in matches:
                cur=mysql.connection.cursor()
                ID=Ids
                NAME=names
                DATE=date
                STATUS=status
                TIME=timeStamp
                cur.execute("INSERT INTO attendance (ID,NAME,DATE,STATUS,TIME) VALUES (%s,%s,%s,%s,%s)",(ID,NAME,DATE,STATUS,TIME))
                mysql.connection.commit()
                cur.close()
                return render_template('exit.html')
            
            
    
    
    
    
    
          


@app.route('/face_reg')
@app.route('/face_register.html')
def home_face():
    return render_template('face_reg.html')
    
    


@app.route('/home_new.html',methods=['GET','POST'])
def home():
    return render_template('home_new.html')

@app.route('/face_reg.html')
def face():
    return render_template('face_reg.html')

@app.route('/mark_attendance.html')
def mark():
    return render_template('mark_attendance.html')

if __name__=="__main__":
    app.run(debug=True)



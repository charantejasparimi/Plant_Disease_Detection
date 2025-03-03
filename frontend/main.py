from fastapi import Request,Form
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, UploadFile, File, HTTPException
import torch
from torchvision import transforms
from fastapi.responses import HTMLResponse
from PIL import Image
import io
from torchvision import transforms, models
import pickle
import uvicorn  # Import uvicorn for running the FastAPI app
import os
from google.cloud import firestore
from fastapi.staticfiles import StaticFiles
from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from fastapi import FastAPI, File, UploadFile, Form
from starlette.requests import Request
from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
cred = credentials.Certificate("./key2.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class_labels = ['Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy', 'Blueberry___healthy', 'Cherry_(including_sour)___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_', 'Corn_(maize)___healthy', 'Corn_(maize)___Northern_Leaf_Blight', 'Grape___Black_rot', 'Grape___Esca_(Black_Measles)', 'Grape___healthy', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy', 'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight', 'Potato___healthy', 'Potato___Late_blight', 'Raspberry___healthy', 'Soybean___healthy', 'Squash___Powdery_mildew', 'Strawberry___healthy', 'Strawberry___Leaf_scorch', 'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___healthy', 'Tomato___Late_blight', 'Tomato___Leaf_Mold', 'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot', 'Tomato___Tomato_mosaic_virus', 'Tomato___Tomato_Yellow_Leaf_Curl_Virus' ]


with open('resnet18_model12_epoch_7.pkl', 'rb') as f:
    model = pickle.load(f)

model.eval()

transform = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
])


def get_class_label(class_index):
    return class_labels[class_index]


def predict_image(img):
    image = transform(img).unsqueeze(0)
    with torch.no_grad():
        outputs = model(image)
    print(outputs)
    if torch.all(outputs < 5):
        return {"class_label": "I can't identify the image"}
    _, predicted = torch.max(outputs, 1)
    print(predicted,"  ",predicted.item())
    class_index = predicted.item()
    class_label = get_class_label(class_index)
    return {"class_index": class_index, "class_label": class_label}


def clean_keys(dictionary):
    cleaned_dict = {}
    for key, value in dictionary.items():
        cleaned_key = key.replace('\uf0d8\t', '')
        cleaned_dict[cleaned_key] = value
    return cleaned_dict

def get_disease_information_by_name(disease_name):
    try:
        query = db.collection('com')
        docs = query.stream()
        matching_documents = []
        print(disease_name)
        for doc in docs:
            doc_data = doc.to_dict()
            if disease_name in doc_data:
                cleaned_data = clean_keys(doc_data)
                return cleaned_data
    except Exception as e:
        print("Firestore error:", e)
        return None


@app.get('/', response_class=HTMLResponse)
def web():
    with open("main.html", "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)
# Create a "templates" directory and put your HTML template in it
templates = Jinja2Templates(directory="templates")

@app.post('/img/', response_class=HTMLResponse)
async def predict(request: Request, file: UploadFile):
    try:
        image = Image.open(io.BytesIO(await file.read()))
        image.save('static/uploads/uploaded_image.png')
        prediction = predict_image(image) 
        print("prediction",prediction)
        global disease 
        disease = prediction["class_label"]
        if prediction["class_label"] == "I can't identify the image":
            # Return an alert message for unidentified images
            return templates.TemplateResponse("error_template.html", {"request": request, "message": "I can't identify the image. Please try another one."})
        # print("predicted class label",disease)
        disease_info = get_disease_information_by_name(disease)
        # print("database info ",disease_info)
        # print(disease_info["Root Cause"])
        # print("\n",disease_info["Precautions"],"\n",disease_info["Fertilizers/Actions to manage"],"\n",disease_info["Root Cause"],"\n",disease_info["Precautions"],"\n",disease_info[disease])
        return templates.TemplateResponse("prediction_template.html", {"request": request, "class_label": prediction["class_label"],"dis":disease_info[disease],"rc":disease_info["Root Cause"],"precautions":disease_info["Precautions"],"fert":disease_info["Fertilizers/Actions to manage"]})
        # return templates.TemplateResponse("prediction_template.html", {"request": request, "class_label": prediction["class_label"],"dis":disease_info[disease],"precautions":disease_info["Precautions"],"fert":disease_info["Fertilizers/Actions to manage"]})
    except Exception as e:
        print("Error:", str(e))  # Print the error to the terminal
        return {"error": str(e)}
    
# @app.post('/submit')
# async def submit(
#     class_label: str = Form(...),
#     imagePathInput: str = Form(...),  # Add this line
# ):
#     return {"class_label": class_label, "imagePathInput": imagePathInput}
    
def send_email(subject: str, body: str, to_email: str, image_path: str):
    # Replace these with your SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = "parimicharantejas@gmail.com"
    smtp_password = "vjnm xtmr cdpi ccav"
    print("sm[1]")
    # Create the email message
    message = MIMEMultipart()
    message["From"] = smtp_username
    message["To"] = to_email
    message["Subject"] = subject
    # message.attach(MIMEText(body, "plain"))
    # # Attach the image to the email
    # with open(image_path, "rb") as image_file:
    #     image_mime = MIMEImage(image_file.read(), name="uploaded_image.png")
    #     message.attach(image_mime)
    # Create the HTML part of the email
    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Template</title>
</head>
<body style="font-family: 'Arial', sans-serif; background-color: #f5f5f5; margin: 0; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
        <h1 style="color:red;">Report on Prediction ! </h1>
        <p style="color: #555;">{body}</p>
        <img src="cid:uploaded_image" alt="Uploaded Image" style="max-width: 100%; height: auto; display: block; margin: 20px 0;">
        <a href="cid:uploaded_image" download style="display: block; background-color: #007bff; color: #fff; text-decoration: none; padding: 10px; border-radius: 5px; text-align: center; margin-top: 20px;">Download Image</a>
    </div>
</body>
</html>
"""

    message.attach(MIMEText(html_body, "html"))

    # Attach the image to the email
    with open(image_path, "rb") as image_file:
        image_mime = MIMEImage(image_file.read(), name="uploaded_image.png")
        image_mime.add_header("Content-ID", "<uploaded_image>")
        message.attach(image_mime)
    # Connect to the SMTP server and send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, message.as_string())

@app.post('/submit')
async def submit(
    class_label: str = Form(...),
    uploaded_image: UploadFile = File(...),
    to_email: str ="charantejas5c4@gmail.com"
    # Add other form fields as needed

):
    # Save the uploaded image
    image_path = f"static/uploads/{uploaded_image.filename}"
    with open(image_path, "wb") as image_file:
        image_file.write(uploaded_image.file.read())

    # Your logic here

    # Send email
    email_subject = "Report on Agri Prediction"
    email_body = f"Class Label: {class_label}"
    try:
        send_email(email_subject, email_body, to_email, image_path)
        return FileResponse("static/report.html", media_type="text/html")
    except Exception as e:
        return {"error": str(e)+"hello"}
    

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=80)
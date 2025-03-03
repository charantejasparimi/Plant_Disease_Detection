// import smtplib
// from email.mime.text import MIMEText
// from email.mime.multipart import MIMEMultipart

// server = smtplib.SMTP("smtp.gmail.com", 587)
//         server.starttls()
//         server.login(sender_email, sender_password)
//         subject = "Order placed Successfully"
//         subject2="Your product is ready to Buy"
//         message_text="Hello "+CurrentAccount+""", \nYour order placed successfully,\n\n\n
//         your order details:- \n\n
//         -  product name :- """+str(product_data["product_name"])+"""
//         -  product_id :- """+str(product_data["product_id"])+"""
//         -  Seller-Email :- """+str(product_data["seller_email"])+"""
//         -  Seller-name :- """+str(product_data["seller_name"])+"""
//         -  product price :- """+str(product_data["price"])+"""
//         Please contact to the above sender email if did'nt get any response from the seller.\n\n
//         Thankyou for choosing our website.\nHave a good day.
//         """
//         message_text2="Hello "+str(product_data["seller_email"])+", Your Product is ready to take by the customer\n Your customer details:\nCustomer Name :- "+product_data2["name"]+"\nCustomer email :- "+CurrentAccount+"\nPlease contact the above customer for further proceedings to delivery the product.\nThankYou!!!"
        
//         msg = MIMEMultipart()
//         msg_buyer=MIMEMultipart()
//         msg['From'] = sender_email
//         msg['To'] = CurrentAccount
//         msg['Subject'] = subject
//         msg.attach(MIMEText(message_text, 'plain'))
//         server.sendmail(sender_email, CurrentAccount, msg.as_string())
//         msg_buyer["From"]= sender_email
//         msg_buyer["To"]= str(product_data["seller_email"])
//         msg_buyer["Subject"]=subject2
//         msg_buyer.attach(MIMEText(message_text2,"plain"))
//         server.sendmail(sender_email,product_data["seller_email"],msg_buyer.as_string())
//         server.quit()
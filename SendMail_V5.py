# -*- coding: utf-8 -*-

"""
Script called from the Class Catalog.
It only takes care of sending an email.
"""

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP_SSL
import os

# Function to find the path of the images inside the exe
def resource_path(relative_path):
    
    import sys     
     
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def sendMail(mailMessage, mail):
            
     # Connection to the server
     smtp_ssl_host = 'smtp.gmail.com'
     smtp_ssl_port = 465
     s = SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
     s.login('test.takeasmile@gmail.com', 'YOUR_MAIL_PW')
   
     msg = MIMEMultipart()
        
     msg['Subject'] = 'Take a smile: credentials'
     msg['From'] = 'Take a smile <test.takeasmile@gmail.com>'
               
     msg['To'] = mail
     
     msg.add_header('Content-Type','text/html')
     
     txt = mailMessage
                  
#%%  Banner
          
     bannerTxt = ('<p style="color:#fe72a5; font-size:12px; font-family:Calibri"><br><br><img src="cid:image1"><br><br>\
                            <b>Take a smile S.r.l.</b><br>\
         C.so xxxxxxx, xx - xxxxx Torino<br>\
         Tel. +39 011 1234567 Fax +39 011 7654321<br>\
         p.i./c.f. xxxxxxx – REA TO-xxxxxx<br></p>')
     
     try:
         with open(resource_path('Banner.png'),'rb') as fp :
          msgImage = MIMEImage(fp.read())
          fp.close()
     except EnvironmentError: 
         print ("Problems with images")
     
     # Define the image's ID as referenced above
     msgImage.add_header('Content-ID', '<image1>')
     msg.attach(msgImage)
     
#%%  Site
     
     siteAndLinkedinTxt = ('<table>\
       <tr>\
         <td style="padding: 0px 6px 0px 0px;">\
           <img style="display:block" border="0" src="cid:image2"/>\
         </td>\
         <td style="padding: 0px 0px 0px 0px;">\
           <img style="display:block" border="0" src="cid:image3"/>\
         </td>\
       <tr>\
     </table>')
     
     
     try:
         with open(resource_path('Site.png'),'rb') as fp :
          msgImage = MIMEImage(fp.read())
          fp.close()
     except EnvironmentError: 
         print ("Problems with images")
     
     # Define the image's ID as referenced above
     msgImage.add_header('Content-ID', '<image2>')
     msg.attach(msgImage)
     
     try:
         with open(resource_path('Linkedin.png'),'rb') as fp :
          msgImage = MIMEImage(fp.read())
          fp.close()
     except EnvironmentError: 
         print ("Problems with images")
     
     # Define the image's ID as referenced above
     msgImage.add_header('Content-ID', '<image3>')
     msg.attach(msgImage)
     
     
     ###############################################################################################
     ## DISCLAIMER
     ###############################################################################################  
     
     DisclaimerTxt = ('<p style="color:#fe72a5;font-size:10px;font-family:Cambria"><br>\
          **********************************************************************************\
          **********************************************************************************\
          *******************************************************************************<br><br>\
     Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut \
     labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris \
     nisi ut aliquip ex ea commodo consequat<br>. Duis aute irure dolor in reprehenderit in voluptate \
     velit esse cillum dolore eu fugiat nulla pariatur.<br><br>\
     *****************************************************************************************\
     *****************************************************************************************\
     *****************************************************************<br></p>')
          
     part2 = MIMEText(txt + bannerTxt + siteAndLinkedinTxt + DisclaimerTxt, 'html')
     msg.attach(part2)
     
     
     ##############################################################################################
     # SENDING
     ##############################################################################################
     
     s.send_message(msg)
     s.quit()
     
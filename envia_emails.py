import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def send_email(conteudo, remetente, assunto, *args):
    corpo = conteudo
    email_msg = MIMEMultipart()
    email_msg["From"] = "bibliotecapoloitapevi@gmail.com"
    email_msg["To"] = remetente
    email_msg["Subject"] = assunto
    email_msg.attach(MIMEText(corpo, "html"))

    for i, ar in enumerate(args):
        with open(ar, "rb") as f:
            img_data = f.read()
            img = MIMEImage(img_data, name=os.path.basename(ar))
            cid = f"image{i + 1}"
            img.add_header('Content-ID', f'<{cid}>')
            img.add_header('Content-Disposition', 'inline', filename=cid)
            email_msg.attach(img)


    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(email_msg["From"], "eumbinyywrriqvnm")
        server.send_message(email_msg)

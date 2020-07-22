import smtplib


def send_message(user_email, code):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login('murakliex@gmail.com', 'zwnaudzczrupcbvt')

    subject = 'BestPost'
    body = f'code - {code}'
    message = f'Subject: {subject}\n\n{body}'

    server.sendmail(
        to_addrs=user_email,
        from_addr='murakliex@gmail.com',
        msg=message
    )

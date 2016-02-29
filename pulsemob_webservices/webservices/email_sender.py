# encoding=utf8

from settings import SMTP_LOGIN, SMTP_SERVER, SMTP_PASSWORD, SMTP_FROM, BACKOFFICE_URL
import smtplib
import logging

logger = logging.getLogger(__name__)

welcome_subject = 'Bem-vindo ao Backoffice SciELO'
welcome_message = 'Olá,\n\nSeja bem-vindo ao Backoffice SciELO. Para cadastrar sua senha clique em: {0}/#/set-password?token={1}\n\nAtenciosamente,\nEquipe SciELO.'

password_recovery_subject = 'Recuperação de Senha'
password_recovery_message = 'Olá,\n\nConforme solicitado, segue o link para recuperação de senha de acesso ao Backoffice SciELO: {0}/#/set-password?token={1}&recovery=true.\nCaso você não tenha solicitado a recuperação de senha, ignore esse email.\n\nAtenciosamente,\nEquipe SciELO.'


def sendemail(from_addr, to_addr_list, cc_addr_list,
              subject, message):
    header = 'From: %s\n' % from_addr
    header += 'To: %s\n' % ','.join(to_addr_list)
    header += 'Cc: %s\n' % ','.join(cc_addr_list)
    header += 'Subject: %s\n\n' % subject
    message = header + message

    server = smtplib.SMTP(SMTP_SERVER)
    server.starttls()
    server.login(SMTP_LOGIN, SMTP_PASSWORD)
    problems = server.sendmail(from_addr, to_addr_list, message)
    server.quit()


def send_welcome_email(to_address, token):
    try:
        header = 'From: {0}\n'.format(SMTP_FROM)
        header += 'To: {0}\n'.format(','.join([to_address]))
        header += 'Subject: {0}\n\n'.format(welcome_subject)
        message = header + welcome_message.format(BACKOFFICE_URL, token)

        server = smtplib.SMTP(SMTP_SERVER)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        problems = server.sendmail(SMTP_FROM, [to_address], message)
        server.quit()
    except Exception as e:
        logger.error('An exception was thrown while sending a password recovery email. Exception: ' + str(e))


def send_password_recovery_email(to_address, token):
    try:
        header = 'From: {0}\n'.format(SMTP_FROM)
        header += 'To: {0}\n'.format(','.join([to_address]))
        header += 'Subject: {0}\n\n'.format(password_recovery_subject)
        message = header + password_recovery_message.format(BACKOFFICE_URL, token)

        server = smtplib.SMTP(SMTP_SERVER)
        server.starttls()
        server.login(SMTP_LOGIN, SMTP_PASSWORD)
        problems = server.sendmail(SMTP_FROM, [to_address], message)
        server.quit()
    except Exception as e:
        logger.error('An exception was thrown while sending a password recovery email. Exception: ' + str(e))
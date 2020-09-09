#! env/bin/python3.8

from app import app, db

from app.authentication.views import login_required
from app.admin.views import get_counters, get_permissions, forbidden, make_history

from app.models import User

# import M2Crypto as m2
from OpenSSL import crypto
# from certgen import (
    # createKeyPair,
    # createCertRequest,
    # createCertificate,
# )
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from pyspkac import SPKAC
from flask import request, make_response, redirect, url_for, render_template, render_template_string, session, flash, g, jsonify, Response, Blueprint, send_from_directory, Markup
from config import CA_FILES_FOLDER
import os, smtplib, datetime, hashlib, sys, getpass, time

CA = Blueprint('CA', __name__, url_prefix='/CA')

#----------------------------------------------------------------------------------
# Обслуживающие функции
#----------------------------------------------------------------------------------



#----------------------------------------------------------------------------------
# API НОВОСТЕЙ
#----------------------------------------------------------------------------------

@CA.route('/', methods=['GET', 'POST'])
@login_required
def ca_main():
    current_user = User.current()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    print ("enter "+str(enter))
    if not enter:
        return forbidden(403)

    all_counters = get_counters()


    return render_template('CA/mainscreen.html', all_counters=all_counters, current_user=current_user)

@CA.route('/root', methods=['GET', 'POST'])
@login_required
def ca_root_main():
    current_user = User.current()

    enter = get_permissions(current_user.role.id, current_user.id, "requests", "enter")
    # print ("enter "+str(enter))
    if not enter:
        return forbidden(403)

    all_counters = get_counters()
    
    rootCA_struct_exist = os.path.exists(CA_FILES_FOLDER)
    rootCAkey_exist = os.path.isfile(os.path.join(CA_FILES_FOLDER, 'private/rootCA.key'))
    rootCAcert_exist = os.path.isfile(os.path.join(CA_FILES_FOLDER, 'public/rootCA.cert'))
    
    if not rootCA_struct_exist :
        print("Структура директорий не существует")
        os.mkdir(CA_FILES_FOLDER)
        for d in ['conf','certs','public','private','incoming']:
                os.mkdir(CA_FILES_FOLDER+'/'+d)
        os.chmod(CA_FILES_FOLDER+"/private", 0o700)
        with open(CA_FILES_FOLDER+'/conf/serial','w') as fd:
            fd.write("01")
        print("Стуктура создана")
    elif not rootCAkey_exist or not rootCAcert_exist:
        print("Ключевая пара не существует, либо отсутствует один из ключей")

    # elif not os.path.isfile(os.path.join(CA_FILES_FOLDER, 'private/rootCA.key')) or not os.path.isfile(os.path.join(CA_FILES_FOLDER, 'public/rootCA.crt')):
        # print("Ytn rk.xf")
            
    # pkey = crypto.PKey()
    # pkey.generate_key(crypto.TYPE_RSA, 2048)

    # req = crypto.X509Req()
    # subj = req.get_subject()

    # name = {'CN':u'ГАСПИ КО УЦ', 'C':'RU'}

    # for key, value in name.items():
        # print(key, value)
        # setattr(subj, key, value)

    # digest = "sha256"

    # req.set_pubkey(pkey)
    # req.sign(pkey, digest)

    # issuerCert, issuerKey = (req, pkey)
    # notBefore, notAfter = (0, 60*60*24*365*5)
    # cert = crypto.X509()
    # cert.set_serial_number(1)
    # cert.gmtime_adj_notBefore(notBefore)
    # cert.gmtime_adj_notAfter(notAfter)
    # cert.set_issuer(issuerCert.get_subject())
    # cert.set_subject(req.get_subject())
    # cert.set_pubkey(req.get_pubkey())
    # cert.sign(issuerKey, digest)
    
    # print('Creating Certificate Authority private key')
    # with open(CA_FILES_FOLDER+'/private/CA.pkey', 'w') as capkey:
        # capkey.write(
            # crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode('utf-8')
        # )

    # print('Creating Certificate Authority certificate')
    # with open(CA_FILES_FOLDER+'/public/CA.cert', 'w') as ca:
        # ca.write(
            # crypto.dump_certificate(crypto.FILETYPE_PEM, crt).decode('utf-8')
        # )
    
    # st_cert=open(CA_FILES_FOLDER+'public/CA.cert', 'rt').read()
    # cert=crypto.load_certificate(crypto.FILETYPE_PEM, st_cert)
    # print(cert.get_subject())
    # subj = cert.get_subject()
    # print(subj.CN)
    # print(subj)
    # print(cert.get_serial_number())
    # print(cert.get_version())
    # print(cert.has_expired())
    # print(cert.digest("sha1").decode("utf-8"))
    # print(cert.digest("md5").decode("utf-8"))
    # print(cert.get_extension_count())
    # print(cert.get_notAfter().decode("utf-8"))
    # print(datetime.datetime.strptime(cert.get_notAfter().decode("utf-8")[:-1], "%Y%m%d%H%M%S"))
    
    # subject = cert.get_subject()
    # issued_to = subject.CN    # the Common Name field
    # issuer = cert.get_issuer()
    # issued_by = issuer.CN
    
    # st_key=open(keyfile, 'rt').read()
    # key=c.load_privatekey(c.FILETYPE_PEM, st_key)
    
    cert = "test"

    return render_template('CA/root_mainscreen.html', all_counters=all_counters, current_user=current_user, cert=cert)

import OpenSSL.crypto
import os, sys, subprocess
import PySimpleGUI as sg

FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

# Convert PFX into private key, public key, certificate and CA(s)

def main():
       
#METHODS ---------------------------------------

    # CA extractor method
    def write_CAs(filename, p12):

        if os.path.exists(filename):
            os.remove(filename)

        ca = p12.get_ca_certificates()

        if ca is None:
            return

        print('Creating Certificate CA File:', filename)

        with open(filename, 'wb') as f:
            for cert in ca:
                f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert))

    # converter method including CAs
    def pfx_to_pem(pfx_path, pfx_password, pkey_path, pubkey_path, pem_path, pem_ca_path):

        print('Opening:', pfx_path)
        with open(pfx_path, 'rb') as f_pfx:
            pfx = f_pfx.read()

        print('Loading P12 (PFX) contents:')
        p12 = OpenSSL.crypto.load_pkcs12(pfx, pfx_password)

        print('Creating Private Key File:', pkey_path)
        with open(pkey_path, 'wb') as f:
            # Write Private Key
            f.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))

        print('Creating Certificate File:', pem_path)
        with open(pem_path, 'wb') as f:
            # Write Certificate
            f.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))

        print('Creating Public Key File:', pubkey_path)
        with open(pubkey_path, 'wb') as f:
            # Write Private Key
            with open(pem_path, "r") as t:
                cert = t.read()
            pub_key_obj = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert).get_pubkey()
            f.write(OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, pub_key_obj))

        if values['catrue']:
            write_CAs(pem_ca_path, p12)

    def explore_func(path):
    # explorer would choke on forward slashes
        path = os.path.normpath(path)

        if os.path.isdir(path):
            subprocess.run([FILEBROWSER_PATH, path])
        elif os.path.isfile(path):
            subprocess.run([FILEBROWSER_PATH, '/select,', path])

#GUI --------------------------------------------------------
    sg.theme('LightGrey1')   #theme

    layout = [  [sg.Text('Enter password to decrypt PFX:')],
                [sg.InputText(key='pwd')],
                [sg.Text('File path:', size=(15, 1), justification='left')],
                [sg.InputText(key='file', justification='left'), sg.FileBrowse()],
                [sg.CBox('Export CA', key='catrue')],
                [sg.Button('Run'), sg.Button('Cancel')] ]

    window = sg.Window('PFXtract v.1 - B.Schoenecker', layout, icon='icon.ico')

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        elif event == "Run":
            pfx_to_pem(pfx_path=values['file'], pfx_password=values['pwd'],pkey_path='private.key',pubkey_path='public.key',pem_path='cert.pem',pem_ca_path='ca.pem')
            
            confirm = sg.popup_yes_no('File extraction complete!', 'Would you like to open the file location?', relative_location=(100, -150))
            if confirm == 'Yes':
                explore_func(values['file'])
                sys.exit()
            elif confirm == 'No':
                sys.exit()

    window.close()
 
if __name__ == '__main__':
    main()
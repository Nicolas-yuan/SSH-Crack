# SSH-Crack
破解SSH登录用户名和密码  
使用optparse库解析命令行参数，使用paramiko进行SSH连接测试，使用webdriver自动将结果和日志显示在浏览器中  
命令行参数解析  
SSH_func5.exe -H <tgtHost IP> [-P <target Port>] [-d <dirtionary for crack with usernames and passwds>] | [-u <username>] | [-p <passwd>] | [--du <dirtionary for crack with usernames>] | [--dp <dirtionary for crack with passwds>]  

for example  
SSH_func5.exe -H 192.168.0.1 [-P 22] -d example.txt    #crack with username and passwd in one dic.txt  
SSH_func5.exe -H 192.168.0.1 [-P 22] --du u.txt --dp pwd.txt    #crack with username and passwd in different dic.txt  
SSH_func5.exe -H 192.168.0.1 [-P 22] -u root --dp pwd.txt    #crack for target username  
SSH_func5.exe -H 192.168.0.1 [-P 22] -u root -p passwd    #login for user  

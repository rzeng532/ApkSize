from ftplib import FTP
import pandas as pd
import paramiko

#"%matplotlib inline"
import matplotlib.pyplot as plt
import os

# Richard Zeng Created this file on 2018-04-08.
# For CMCC APK Size dynamic checking and visulization.

#FTP host address, no port
FTP_HOST = '172.23.12.64'
#Root file path we need
ROOT_ANDROID_FILE_PATH = '/zdyy/UniApp/dev'
ROOT_IOS_FILE_PATH = '/zdyy/UniversalApp/git-develop'
FILD_DIV_SIMBOL = '/'

APK_SIZE_RESULT_PNG = 'apksize.png'
IPA_SIZE_RESULT_PNG = 'ipasize.png'

#Linux 服务器信息
#服务器ip
Host='172.23.25.205'
Port=22
#登录用户名
Username='root'
#登录密码
Password='tvgATWXj'
#登录服务器后执行的命令
Command = ['cd /usr/local/cmcc/apache-tomcat-7.0.75/webapps/appsize']
#本地PC路径
# CUR_PATH = os.path.dirname(__file__)
WinPath = r'./apksize.png'
#服务器上的路径
LinuxPath = r'/usr/local/cmcc/apache-tomcat-7.0.75/webapps/apksize/%s'

#init FTP client & goto the daily folder
def init_ftp():
    print("init ftp start")
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST)
        ftp.login('zdyy', 'zdFTP@11')
        print(ftp.getwelcome())
    except e:
        print('Failed to connect with FTP "%s"' % FTP_HOST)

    print("init ftp end")
    return ftp

#Get dev folder, we just analyze the everyday's first APK package.
def get_daily_build_infor(ftp, rootPath):

    #Goto root file path
    ftp.cwd(rootPath)

    folderResult = []
    apkSize = []
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    for f in filelist:
        #Check dir or file
        if f[0] == 'd':
            size =  get_daily_build_apk_size(ftp, rootPath + FILD_DIV_SIMBOL + f.split()[-1])
            if size > 0:
                folderResult.append(f.split()[-1])
                apkSize.append(size)

            # print("%s: %s" % (f.split()[-1], size))

    return [folderResult, apkSize]

def get_daily_build_apk_size(ftp, folderPath):
    print(folderPath)
    ftp.cwd(folderPath)

    files = []
    ftp.retrlines('LIST', files.append)
    for f in files:
        # print(f)
        #Check dir or file
        if f[0] != 'd' \
           and f.find('dev') >= 0 \
           and (f.find('.apk') >= 0 or f.find('.ipa') >= 0):
            #Convert 2 Kb from bytes.
            # print(f.split()[4])
            return int((int(f.split()[4]) / 1024))
        else:
            continue

    return 0

def create_apk_size_df(row):
    df = pd.DataFrame({"date": pd.to_datetime(row[0], errors='coerce', format='%D'),
                        "size": row[1]})
    df = df.set_index("date")
    print(df)
    return df

def show_apk_size_bar(data, fileName):
    #plt.figure(figsize=(30, 30))

    data.plot(kind='bar', stacked=True, alpha=0.7)
    # plt.xticks(rotation=45)
    if fileName.find('apk') >= 0:
        plt.xlabel('Android')
    elif fileName.find('ipa') >= 0:
        plt.xlabel('iOS')

    plt.ylabel('APP Size (Kb)')
    plt.title('APP Size Dynamic Chart')

    plt.subplots_adjust(left=0.15, wspace=0.25, hspace=0.25,
                        bottom=0.18, top=0.91)

    # plt.show()
    if(os.path.exists(fileName)):
        os.remove(fileName)

    plt.tight_layout()
    plt.savefig(fileName)

    if (os.path.exists(fileName)):
        conn_linux_and_trans_png(fileName)
        print("Target app size png is transferred.")
    else:
        print('Err: Target app size png is incorrect!')

def show_apk_size_diff(data):
    plt.plot(data.index, data.diff(), c='red')
    # data.diff(axis=0).dropna().plot(stacked=True, alpha=0.7)

    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('APK Diff Size (Kb)')
    plt.title('APK Size Diff Dynamic Chart')
    plt.savefig('apksize_diff.png')

# def copy_file():
#     targetPath = '/usr/local/cmcc/apache-tomcat-7.0.75/webapps/apksize'
#     if(os.path.exists(targetPath) and os.path.exists(APK_SIZE_RESULT_PNG)):
#         val = os.system("cp ./%s %s" % (APK_SIZE_RESULT_PNG, targetPath))
#         print(val)
#     else:
#         print('Target apk size png or target copy path is incorrect.')

def main():
    ftp = init_ftp()

    #Android information.
    anroid_row_df = get_daily_build_infor(ftp, ROOT_ANDROID_FILE_PATH)
    df = create_apk_size_df(anroid_row_df)
    # Apk size bar chart
    show_apk_size_bar(df, APK_SIZE_RESULT_PNG)

    #iOS information
    ios_row_df = get_daily_build_infor(ftp, ROOT_IOS_FILE_PATH)
    df = create_apk_size_df(ios_row_df)
    # Apk size bar chart
    show_apk_size_bar(df, IPA_SIZE_RESULT_PNG)

    # We dont' need diff chart now.
    # show_apk_size_diff(df)

def conn_linux_and_trans_png(fileName):
    '''SSHA远程登录：Windows客户端连接Linux服务器，并输入指令'''

    client = paramiko.Transport((Host, Port))
    client.connect(username=Username, password=Password)
    sftp = paramiko.SFTPClient.from_transport(client)

    sftp = paramiko.SFTPClient.from_transport(client)
    sftp.put(r'./%s' % (fileName), r'/usr/local/cmcc/apache-tomcat-7.0.75/webapps/apksize/%s' % (fileName))
    #执行完毕，终止连接
    client.close()

if __name__ == '__main__':
    main()

from ftplib import FTP
import pandas as pd
import matplotlib.pyplot as plt

# Richard Zeng Created this file on 2018-04-08.
# For CMCC APK Size dynamic checking and visulization.

#FTP host address, no port
FTP_HOST = '172.23.12.64'
#Root file path we need
ROOT_FILE_PATH = '/zdyy/UniApp/dev'
FILD_DIV_SIMBOL = '/'

#init FTP client & goto the daily folder
def init_ftp():
    print("init ftp start")
    try:
        ftp = FTP()
        ftp.connect(FTP_HOST)
        ftp.login('zdyy', 'zdFTP@11')
        ftp.cwd(ROOT_FILE_PATH)
        print(ftp.getwelcome())
    except e:
        print('Failed to connect with FTP "%s"' % FTP_HOST)

    print("init ftp end")
    return ftp

#Get dev folder, we just analyze the everyday's first APK package.
def get_daily_build_infor(ftp):
    folderResult = []
    apkSize = []
    filelist = []
    ftp.retrlines('LIST', filelist.append)
    for f in filelist:
        #Check dir or file
        if f[0] == 'd':
            size =  get_daily_build_apk_size(ftp, ROOT_FILE_PATH + FILD_DIV_SIMBOL + f.split()[-1])
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
        if f[0] != 'd' and f.find('dev') >= 0:
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

def show_apk_size_bar(data):
    data.plot(kind='bar', stacked=True, alpha=0.7)
    plt.xlabel('Date')
    plt.ylabel('APK Size (Kb)')
    plt.title('APK Size Dynamic Chart')
    plt.show()

def show_apk_size_diff(data):
    plt.plot(data.index, data.diff(), c='red')
    # data.diff(axis=0).dropna().plot(stacked=True, alpha=0.7)
    plt.xticks(rotation=90)
    plt.xlabel('Date')
    plt.ylabel('APK Diff Size (Kb)')
    plt.title('APK Size Diff Dynamic Chart')
    plt.show()

ftp = init_ftp()
row_df = get_daily_build_infor(ftp)
df = create_apk_size_df(row_df)

#Apk size bar chart
show_apk_size_bar(df)

#We dont' need diff chart now.
# show_apk_size_diff(df)

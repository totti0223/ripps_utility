from pip._internal import main as _main
import importlib

def _import(name, module, ver=None):
    try:
        globals()[name] = importlib.import_module(module)
    except ImportError:
        try:
            if ver is None:
                _main(['install', module])
            else:
                _main(['install', '{}=={}'.format(module, ver)])
            globals()[name] = importlib.import_module(module)
        except:
            print("can't import: {}".format(module))

_import('requests','requests')
_import('argparse','argparse')
_import('json','json')
_import('threading','threading')


import os, time, glob
from threading import Thread

parser = argparse.ArgumentParser(
            prog='folder watch program', # プログラム名
            usage='folder watch program', # プログラムの利用方法
            description='', # 引数のヘルプの前に表示
            epilog='end', # 引数のヘルプの後で表示
            add_help=False, # -h/–help オプションの追加
            )

parser.add_argument('-i', '--interval',default=1)
parser.add_argument('-d', '--dir', nargs='+', help="pass abs directory pass as list", required = True)
parser.add_argument('-n', '--name',default="筑波_第１号_RIPPSボット")

# 引数を解析する
args = parser.parse_args()
print(args.dir)
#path_to_watch = "/Users/todayousuke/Resilio Sync/sandbox/17_clock_ripps/**" #監視するフォルダ絶対パス。最後に**を必ずつける
#example of path  "ABS/PATH/TO/DIRECTORY/**"

#botname = "第１RIPPS監視ボット" #投稿ボットの名前
#do not touch###
SLACK_WEBHOOK = "https://hooks.slack.com/services/XXXXXXXXXX"
################
start = time.time()


def errorpostslack(path):
	error_message = "監視対象フォルダ(%s)が%s時間以上更新されていません" % (path,args.interval)  #更新なしメッセージ
	ellapsed = int(time.time() - start)
	payload_dic = {
		"icon_emoji": ':cry:',
		"text": error_message,
		"username": args.name + "_" + str(int(ellapsed/(60*60))),
		"channel": "#general", # #も必要
	}
	try:
		r = requests.post(SLACK_WEBHOOK, data=json.dumps(payload_dic))
	except requests.ConnectionError:
		print(requests.ConnectionError)
		print("slackに接続できませんでした。")

def initiation(path,nfiles):    
	message = "%sの監視を開始します。 監視下のフォルダには現在%d個のファイルがあります。%s時間ごとに更新チェックします。" % (path,nfiles,args.interval) 
	ellapsed = int(time.time() - start)
	payload_dic = {
		"icon_emoji": ':heartpulse:',
		"text": message,
		"username": args.name + "_" + str(int(ellapsed/(60*60))),
		"channel": "#general", # #も必要
	}
	try:
		r = requests.post(SLACK_WEBHOOK, data=json.dumps(payload_dic))
	except requests.ConnectionError:
		print(requests.ConnectionError)
		print("slackに接続できませんでした。")

def dailynotice():
	message = "１日１回の定期報告です。"
	ellapsed = int(time.time() - start)
	for i, (before, path_to_watch) in enumerate(zip(befores,args.dir)):
		nfiles = len(glob.glob(path_to_watch,recursive=True))
		message += "%sのフォルダ下には%d個のフォルダ・ファイルが存在します" % (path_to_watch,nfiles)
	payload_dic = {
		"icon_emoji": ':smile:',
		"text": message,
		"username": args.name + "_" + str(int(ellapsed/(60*60))),
		"channel": "#general", # #も必要
	}
	try:
		r = requests.post(SLACK_WEBHOOK, data=json.dumps(payload_dic))
	except requests.ConnectionError:
		print(requests.ConnectionError)
		print("slackに接続できませんでした。")	    

#check all directories at start up

befores = []

for i, path_to_watch in enumerate(args.dir):
	print(path_to_watch)
	assert os.path.isdir(path_to_watch) == True, print("%s is not a valid directory" % path_to_watch)
	if path_to_watch[-1] != "/":
		path_to_watch += "/**"
	else:
		path_to_watch += "**"
	before = dict ([(f, None) for f in glob.glob(path_to_watch,recursive=True)])
	initiation(path_to_watch,len(before))
	args.dir[i] = path_to_watch
	befores.append(before)


def first_loop():
	while 1:
		time.sleep(float(args.interval)*60*60)
		for i, (before, path_to_watch) in enumerate(zip(befores,args.dir)):
		    after = dict ([(f, None) for f in glob.glob(path_to_watch,recursive=True)])
		    added = [f for f in after if not f in before]
		    removed = [f for f in before if not f in after]
		    if added:
		        print ("Added: ", ", ".join (added))
		        #goodpostslack(added)
		        pass
		    elif removed:
		        print ("Removed: ", ", ".join (removed))
		        pass
		    else:
		        errorpostslack(path_to_watch)
		    befores[i] = after
		
def second_loop():
	time.sleep(10)
	#一日に一回にする
	while 1:
		dailynotice()
		time.sleep(24*60*60)

t1 = Thread(target = first_loop)
t2 = Thread(target = second_loop)
t1.start()
t2.start()
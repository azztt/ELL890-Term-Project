from __future__ import with_statement
import threading
from types import FunctionType
from typing import Any, Dict, List, OrderedDict
from psychopy import core, gui, visual, data, event
from psychopy.hardware.keyboard import Keyboard
import numpy.random as nrand
from os import makedirs
import csv

# =====================SETUP=========================

DATA_DIR = 'experiment_data'

# mapping for emotion
em_map: Dict[int, str] = {
    "num_1": "neutral",
    "num_2": "calm",
    "num_3": "happy",
    "num_4": "sad",
    "num_5": "angry",
    "num_6": "fearful",
    "num_7": "disgust",
    "num_8": "surprised",
    1: "neutral",
    2: "calm",
    3: "happy",
    4: "sad",
    5: "angry",
    6: "fearful",
    7: "disgust",
    8: "surprised",
    "none": "none",
}

def get_video_name(actor: int, em: int, mod: int) -> str:
    '''
    Returns the video's name corresponding to passed actor,
    emotion and modality, other 4 factors remaining constant
    '''
    return "{}-01-{}-{}-01-01-{}".format(
        str(mod).zfill(2),
        str(em).zfill(2),
        str(1 if em==1 else 2).zfill(2),
        str(actor).zfill(2)
    )

# 1) Prepare list of videos with and without sound and
#   other parameters
'''
videos_list = {
    "02-01-06-01-02-01-12": {
        "audio": true, (bool)
        "response": "fearful", (string)
        "response_time": 1400, (in milliseconds)
    },
    ...
}
'''
# field names to be used in the csv file
headings = [
    'Subject Name',
    'VidName',
    'Speaker gender', 
    'Audio', 
    'True emotion', 
    'Subject gender', 
    'Response emotion', 
    'Response time'
]
videos_list: OrderedDict[str, OrderedDict[str, Any]] = {}
video_name_list: List[str] = []
# fill the dictionary
for actor in range(1, 11):
    for em in range(1, 9):
        for mod in range(1, 3):
            v_name = get_video_name(actor, em, mod)
            videos_list[v_name] = {
                "audio": mod == 1,
                "response": "none",
                "response_time": 0,
            }
            video_name_list.append(v_name)

# rows to be written in csv file
dataRows: List[Dict[str, Any]] = []

# temporary store of times at which responses are asked
# used to check if responses are missed
q_time: int = 0
# list of responses of emotion
em_resp: List[str] = []
# response waiting timeout (ms)
res_timeout = 30000

# 3) Set experiment parameters (to be entered by setter)
expData = {
    'Date of Experiment': data.getDateStr(),
    'Name of Subject': 'Subject_1',
    'Gender': ['Female', 'Male', 'Others', 'Do not want to disclose']
}

makedirs(DATA_DIR, exist_ok=True)

def getFileName(name: str, date: str) -> str:
    '''
    Return unique filename from given subject name and date/time of experiment
    '''
    return '{}_{}'.format(name, date)

# 4) method to write a data field to the dataRows array
def saveResponses() -> None:
    '''
    Read the response list ordered dictionary and fill the list
    of responses to be written in the data file
    '''
    for vid, par in videos_list.items():
        parts = vid.split('-')
        speakerGender = 'Female' if int(parts[-1]) % 2 == 0 else 'Male'
        trueEmotion = em_map[int(parts[2])]
        # for answered videos only
        if not(par['response'] == 'none'):
            dataRows.append({
                'Subject Name': expData['Name of Subject'],
                'VidName': vid,
                'Speaker gender': speakerGender, 
                'Audio': par['audio'], 
                'True emotion': trueEmotion, 
                'Subject gender': expData['Gender'], 
                'Response emotion': par['response'], 
                'Response time': par['response_time']
            })


# 5) method to return random next letter to be displayed
def getNextVideo() -> str:
    '''
    Returns the next random video name from prepared list
    '''
    # get a random alphabet
    rv_name = nrand.choice(video_name_list)
    video_name_list.remove(rv_name)
    return rv_name

# 6) method to listen to responses' keypress

def listenEmotionResponse(keys: str, clk: core.Clock, cb: FunctionType) -> None:
    kb = Keyboard(clock=clk)
    while expOn:
        keypress = kb.waitKeys(keyList=keys, maxWait=res_timeout/1000.0)
        cb()
        if not (keypress == None):
            ts = keypress[0].rt
            diff = ts-q_time

            # if response was delayed more than response timeout
            # fill 'none' in the missed responses
            if diff > res_timeout:
                em_resp.extend([em_map["none"]]*(diff//res_timeout))
            # else add the emotion corresponding to the keypress
            # to the emotion response array
            else:
                em_resp.append(em_map[keypress[0].name])
        
    kb.stop()

# 7) Custom class to run separate thread to listen to key presses
class KeyThread(threading.Thread):
    def __init__(self, keys: List[str], clk: core.Clock, cb: FunctionType):
        threading.Thread.__init__(self)
        self.keys = keys
        self.clk = clk
        self.cb = cb

    def run(self) -> None:
        listenEmotionResponse(self.keys, self.clk, self.cb)
        
# ===================SETUP DONE======================
#////////////////////////////////////////////////////
# ===============STARTING EXPERIMENT=================

# 1) Get folder where the video files are
dataFolder = gui.fileOpenDlg(prompt='Select data location (Select any one file in the required folder)')
dataFolder = "/".join(dataFolder[0].split("/")[:-1])

# 2) Get experiment data from experiment setter and initialize parameters
expDialog = gui.DlgFromDict(expData,
                            title='Emotion analysis experiment',
                            fixed=['Date of Experiment'],
                            tip=['', 'Enter a number if you want to be anonymous', ''])

if expDialog.OK:
    expData['filename'] = getFileName(expData['Name of Subject'], expData['Date of Experiment'])
else:
    print('Experiment cancelled before starting. Exiting...')
    core.quit()

# 3) start stimulus window and present introduction screen
listenKey = 'space'
introMessage = 'Hello {} ! You will be presented a series of very short video clips '.format(expData['Name of Subject'])
introMessage += 'one by one.\nAfter each clip, you will be presented with a list of\n emotions with the corresponding numpad key. '
introMessage += 'Your task is to identify the emotion presented in the clip you just saw before and press the numpad key number '
introMessage += 'corresponding to the emotion you identified. After each clip, you will be allowed only {} seconds to identify the '.format(res_timeout/1000)
introMessage += 'emotion in that particular clip. The clips may or may not have audio in them. So don\'t panic. It will take about '
introMessage += '16 minutes to complete. We appreciate your patience.'
introMessage += 'Press "{}" whenever you are ready.\nGOOD LUCK!'.format(listenKey)

# create the window component
win = visual.Window(monitor='testMonitor', size=(1920, 1080))

# show welcome screen
welcomeScreen = visual.TextStim(win,text=introMessage, color=-1, wrapWidth=2.0, height=0.07)
welcomeScreen.draw()
win.flip()
# wait to press space to start experiment
event.waitKeys(keyList=[listenKey])
# set flag and start experiment clock
expOn = True
expClock = core.Clock()

# 3) setup response capture thread object
# listenObj = KeyThread(key=[*em_map], clk=expClock)

# static periods to time stimulus appearance independent of code execution time
ISI = core.StaticPeriod(screenHz=144, win=win, name='Inter Stimulus Interval')
ONS = core.StaticPeriod(screenHz=144, win=win, name='Onset Time')

# Prepare stimulus for emotion options presentation
emOp = 'What do you think it was?\n'
emOp += '(1) Neutral\n'
emOp += '(2) Calm\n'
emOp += '(3) Happy\n'
emOp += '(4) Sad\n'
emOp += '(5) Angry\n'
emOp += '(6) Fearful\n'
emOp += '(7) Disgust\n'
emOp += '(8) Surprised\n'
options = visual.TextStim(win, text=emOp, bold=True, color=-1, wrapWidth=2.0, height=0.07)

# reset clock to start stimulus presentation
# expClock.reset()
# feedObj.start()
# listenObj.start()
# ISI.start(0.3)
expClock.reset()

numVid = len(video_name_list)

# load first video
next_vid_name = getNextVideo()
emVid = visual.VlcMovieStim(win, filename="{}/{}.mp4".format(dataFolder, next_vid_name))
video_name_list.append(next_vid_name)
# resDone = False
# def responseDone():
#     global resDone
#     resDone = True
# listenObj = KeyThread(key=[*em_map], clk=expClock, cb=responseDone)
kb = Keyboard(expClock)

try:
    for i in range(numVid):
        # load next random video
        next_vid_name = getNextVideo()
        emVid.loadMovie("{}/{}.mp4".format(dataFolder, next_vid_name))
        # play the loaded video
        while not emVid.isFinished:
            emVid.draw()
            win.flip()
        
        # present options for emotions
        options.draw()
        win.flip()
        # start reading time
        q_time = expClock.getTime()*1000
        # wait for response till timeout
        response = kb.waitKeys(keyList=[*em_map])
        # blank the screen
        win.flip()
        # process and add response to the data structure
        if response == None:
            # missed response
            videos_list[next_vid_name]['response'] = 'none'
            videos_list[next_vid_name]['response_time'] = res_timeout
        else:
            videos_list[next_vid_name]['response'] = em_map[response[0].name]
            videos_list[next_vid_name]['response_time'] = abs(response[0].rt*1000 - q_time)

    # end all static periods
    # ISI.complete()

    # stop all threads
    # expOn = False
    # listenObj.join()

    # keyPressedTimes = keyPressedTimes[:-1]

    # 3) Display thank you message
    tyMess = 'That was awesome! Thank you very much for your precious time, {}. We appreciate your '.format(expData['Name of Subject'])
    tyMess += 'effort to be a part of this experiment. Have a great day ahead!\n'
    tyMess += 'One last time, press "{}" to exit.'.format(listenKey)
    # show thank you message
    welcomeScreen.text = tyMess
    welcomeScreen.draw()
    win.flip()

    # print('Key presented times: ')
    # print(targetPresentedTimes)

    # print('Key pressed times:')
    # print(keyPressedTimes)

    event.waitKeys(keyList=[listenKey])

    win.close()
except KeyboardInterrupt:
    saveResponses()
    with open(DATA_DIR+'/'+getFileName(expData['Name of Subject'], expData['Date of Experiment'])+'.csv', 'w') as df:
        csvWriter = csv.DictWriter(df, headings)
        csvWriter.writeheader()
        csvWriter.writerows(dataRows)
except Exception as e:
    print("Experiment stopped unexpectedly")
    print("Unexpected exception occured {}".format(e))
    saveResponses()
    with open(DATA_DIR+'/'+getFileName(expData['Name of Subject'], expData['Date of Experiment'])+'.csv', 'w') as df:
        csvWriter = csv.DictWriter(df, headings)
        csvWriter.writeheader()
        csvWriter.writerows(dataRows)

# ===============ENDING EXPERIMENT=================
# /////////////////////////////////////////////////
# ==================PROCESS DATA===================

# diffs = []

# # make this True/False whether you want the missed key presses to be
# # removed from the saved and plotted data or not
# removeMissed = False

# structures for data to be saved and plotted
keyPressedSave = []
targetPresentedSave = []

# for i in range(len(targetPresentedTimes)):
#     if keyPressedTimes[i] == -1: # missed this one
#         if removeMissed:
#             continue
#         keyPressedSave.append(0)
#         targetPresentedSave.append(7)
#     else:
#         keyPressedSave.append(keyPressedTimes[i])
#         targetPresentedSave.append(targetPresentedTimes[i])
#     diffs.append(round(abs(targetPresentedSave[-1]-keyPressedSave[-1]), 3))

# titles = 'Presented time(s),Pressed time(s),Difference(s)\n'

saveResponses()
with open(DATA_DIR+'/'+getFileName(expData['Name of Subject'], expData['Date of Experiment'])+'.csv', 'w') as df:
    csvWriter = csv.DictWriter(df, headings)
    csvWriter.writeheader()
    csvWriter.writerows(dataRows)

# try:
#     plt.figure()
#     plt.scatter([i+1 for i in range(len(targetPresentedSave))], diffs)
#     # plt.plot([i for i in range(1, len(targetPresentedTimes)+1)], diffs, '-')
#     plt.ylabel('Difference between keypress and\nactual presentation of stimuli (seconds)')
#     plt.xlabel('Trial Number')
#     plt.title('Subject response times vs trial number', fontweight='bold')
#     plt.grid()
#     ax = plt.gca()
#     ax.set_xticks([i+1 for i in range(len(targetPresentedSave))])
#     plt.show()
# except Exception as e:
#     print('An unexpected error occured while plotting! Try plotting manually\n')
#     print(e)
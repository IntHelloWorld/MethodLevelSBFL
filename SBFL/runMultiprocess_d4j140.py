import os
import shutil
import subprocess as sp
import time
from pathlib import Path

logDir = 'logs'

maxProcessNum = 4
processPool = []  # storing (process, "pid-bid")

def waitPatchPoolFinish():
    while (len(processPool) > 0):
        time.sleep(1)
        valuesToRemove = []
        for process, projId in processPool:
            exitCode = process.poll()
            if exitCode is None:
                continue
            else:
                if exitCode != 0:
                    print('[ERROR] process {} finished with non-zero exit code!'.format(projId))
                valuesToRemove.append((process, projId))
                print('===== Finished {} ====='.format(projId))
        for value in valuesToRemove:
            processPool.remove(value)

def runGz(pid: str, bid: str):
    while (len(processPool) >= maxProcessNum):
        time.sleep(1)
        valuesToRemove = []
        for process, projId in processPool:
            exitCode = process.poll()
            if exitCode is None:
                continue
            else:
                if exitCode != 0:
                    print('[ERROR] process {} finished with non-zero exit code!'.format(projId))
                valuesToRemove.append((process, projId))
                print('===== Finished {} ====='.format(projId))
        for value in valuesToRemove:
            processPool.remove(value)
    logPath = os.path.join(logDir, pid+'-'+bid+'.log')
    with open(logPath, 'w') as f:
        process = sp.Popen("bash runGz.sh {} {}".format(pid, bid), stdout=f, stderr=f, shell=True, universal_newlines=True)
        # process = sp.Popen("echo {}-{}".format(pid, bid), stdout=f, stderr=f, shell=True, universal_newlines=True)
    processPool.append((process, pid + '-' + bid))
    print('===== Start {}-{} ====='.format(pid, bid))

d4j140ProjNames = ['Chart', 'Closure', 'Lang', 'Math', 'Mockito', 'Time']

def getD4jProjNameFromSimpleName(simpleName):
    for projName in d4j140ProjNames:
        if simpleName == projName.lower():
            return projName
    print('Cannot find the project name for the simple name: {}'.format(simpleName))
    exit -1

projDict = {
    'Chart': (list(range(1, 27)), []),
    'Closure': (list(range(1, 134)), [63, 93]),
    'Lang': (list(range(1, 66)), [2]),
    'Math': (list(range(1, 107)), []),
    'Mockito': (list(range(1, 39)), []),
    'Time': (list(range(1, 28)), [21])
}

def checkResults():
    for pid in projDict:
        bidList = projDict[pid][0]
        deprecatedBidList = projDict[pid][1]
        bidList = [bid for bid in bidList if bid not in deprecatedBidList]

        for bid in bidList:
            bidResultDir = 'results/{}/{}'.format(pid, bid)
            if not os.path.isdir(bidResultDir):
                print('[ERROR] results/{}/{} does not exist'.format(pid, bid))
            else:
                ochiaiFile = 'results/{}/{}/ochiai.ranking.csv'.format(pid, bid)
                # if the file does not exist or the file is empty or it only contains one line
                if not os.path.isfile(ochiaiFile):
                    print('[ERROR] results/{}/{}/ochiai.ranking.csv does not exist'.format(pid, bid))
                else:
                    linesNum = sp.check_output('cat results/{}/{}/ochiai.ranking.csv | wc -l '.format(pid, bid), shell=True, universal_newlines=True).strip()
                    if linesNum == '1' or linesNum == '0':
                        print('[ERROR] results/{}/{}/ochiai.ranking.csv is empty or only has one line!'.format(pid, bid))      

def main():
    os.makedirs(logDir, exist_ok=True)
    for pid in projDict:
        bidList = projDict[pid][0]
        deprecatedBidList = projDict[pid][1]
        bidList = [bid for bid in bidList if bid not in deprecatedBidList]

        for bid in bidList:
            bidResultDir = 'results/{}/{}'.format(pid, bid)
            if os.path.isdir(bidResultDir):
                ochiaiFile = 'results/{}/{}/ochiai.ranking.csv'.format(pid, bid)
                linesNum = sp.check_output('cat results/{}/{}/ochiai.ranking.csv | wc -l '.format(pid, bid), shell=True, universal_newlines=True).strip()
                if not os.path.isfile(ochiaiFile) or (os.path.isfile(ochiaiFile) and linesNum == '1'):
                    print('Removing {} because the result is invalid'.format(bidResultDir))
                    shutil.rmtree(bidResultDir)
                else:
                    print("results/{}/{} already exists, skipping".format(pid, bid))
                    continue
            if os.path.isfile(os.path.join(logDir, pid + '-' + str(bid)+'.log')):
                os.remove(os.path.join(logDir, pid + '-' + str(bid)+'.log'))
            runGz(pid, str(bid))

    waitPatchPoolFinish()

if __name__ == '__main__':
    main()
    # checkResults()
    
    # bugList = []
    # with Path('../bug_list.txt').open() as f:
    #     for line in f:
    #         line = line.strip()
    #         projName, bugId = line.split('_')
    #         projName = getD4jProjNameFromSimpleName(projName)
    #         bugId = str(int(bugId))
    #         bugList.append('{}_{}'.format(projName, bugId))
    # removedBugList = []
    # for proj in projDict:
    #     for bugId in projDict[proj][0]:
    #         bugId = str(bugId)
    #         if '{}_{}'.format(proj, bugId) not in bugList:
    #             removedBugList.append((proj, bugId))
    # for proj, bid in removedBugList:
    #     projDict[proj][0].remove(int(bid))
    # print(projDict)

    # main()
    # checkResults()
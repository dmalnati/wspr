#!/usr/bin/python3.5 -u

import os
import sys

#
# Objective to count number of unique decodes by ID.
#
# Problems are:
# - multiple decodes for single transmission happens
# - interleaving of ids
#


# data expected to look like this:
#
# 1558   -2   1.5    0.197966   -4   Q04XAW        EL87      0   7526
# 1558  -14   1.6    0.198088    1   Q04XAW        EL87      0   7708
# 1706   -8  -0.9    0.198083   -4   Q04XAW        EL87      0  13902
# 1712    5   0.8    0.198009   -4   Q04XAH        EL87      0  11261
#
def Process(wsjtDecodesFile):
    retVal = False

    fileData = None
    try:
        with open(wsjtDecodesFile, 'r') as file:
            fileData = file.read()
            retVal = True
    except:
        pass

    if fileData is not None:
        lineList = fileData.split('\n')

        timeIdSet = dict()
        id__count = dict()
        for line in lineList:
            linePartList = line.split()

            if len(linePartList) == 9:
                time = linePartList[0]
                id   = linePartList[5][0] + linePartList[5][2]

                timeId = (time, id)

                if timeId not in timeIdSet:
                    timeIdSet[timeId] = ""

                    if id not in id__count:
                        id__count[id] = 0
                    
                    id__count[id] += 1

        idList = sorted(id__count.keys())

        for id in idList:
            count = id__count[id]
            print("{} : {}".format(id, count))

    return retVal



def Main():
    retVal = True

    if len(sys.argv) != 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <wsjtDecodes.txt> " % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    wsjtDecodesFile = sys.argv[1]

    retVal = Process(wsjtDecodesFile)

    return retVal == False

sys.exit(Main())
















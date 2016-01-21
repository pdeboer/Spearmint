import numpy as np
import math
import subprocess
import string
import random
import sys
import numpy as np
import copy

# Write a function like this called 'main'
def transformWorkerCount(num):
    return num * 2 - 1 if num > 1 else 0


def appendWhereClause(statement, paramlist, targetParam):
    return (statement + (" AND %s = %s" % targetParam))


def pickRandomID(ids,conn, params):
    targetIndex = random.randint(0, len(ids) - 1)
    targetId = ids[targetIndex]
    print "selected id %i" % targetId

    cursor = conn.cursor()

    cursor.execute("select id from python_used_ids where id = %s and usedForProcess = %s", (targetId, str(params)))
    if (len(list(cursor)) > 0):
        print "id %i was already used. Selecting a new one " % (targetId)
        if(len(ids) == 1):
            return -1
        else:
            del ids[targetIndex]
            return pickRandomID(ids, conn, params)
    else:
        cursor.execute("insert into python_used_ids (id, usedForProcess, step) SELECT %s as c1, %s as c2, count(*)+1 as c3 from python_used_ids", (targetId, str(params)))
        conn.commit()
        return targetId


def getLenAndCostOfId(targetId, conn):
    cursor = conn.cursor()
    cursor.execute("select result_len, cost from shortn_everything where id=%s", targetId)
    return list(cursor)[0]

def fitNormalAndDrawLenAndCostSample(ids, conn):
    print "no actual values remaining. fitting normal distribution and drawing random sample"
    resultLenList = [ getLenAndCostOfId(r, conn)[0] for r in ids ]
    costList= [ getLenAndCostOfId(r, conn)[1] for r in ids ]

    print resultLenList, ids
    muLen = np.mean(resultLenList)
    sigmaLen = np.std(resultLenList)
    print "mean and stdev of len are: %f, %f" % (muLen, sigmaLen)

    sampleLen = np.random.normal(muLen, sigmaLen, 1)
    sampleCost = np.random.normal(np.mean(costList), np.std(costList), 1)
    return (sampleLen[0], sampleCost[0])



def main(params):
    import MySQLdb
    connection = MySQLdb.connect("127.0.0.1", "root", "", "recombination")
    cursor = connection.cursor()

    sql = "select id from shortn_categorization where collector = %s"
    collector = params["collector"]
    paramList = [collector]

    collectorWorkers = transformWorkerCount(params["collector_workers"])
    if (collectorWorkers > 0 and collector != "DualPathwayProcess" and collector != "IterativeRefinement"):
        paramList.append(str(collectorWorkers))
        sql += " AND collector_workers = %s"

    decider = params["decider"]
    if (decider != "" and collector != "DualPathwayProcess"):
        paramList.append(decider)
        sql += " AND decider = %s"

    deciderWorkers = transformWorkerCount(params["decider_workers"])
    if (deciderWorkers > 0 and collector != "DualPathwayProcess" and decider == "Contest"):
        paramList.append(str(deciderWorkers))
        sql += " AND decider_workers = %s"

    hasFinder = params["hasFinder"]
    if (collector != "DualPathwayProcess"):
        paramList.append(hasFinder)
        sql += " AND hasFinder = %s"

    print sql, paramList
    cursor.execute(sql, paramList)

    print "found the following IDs"
    for targetId in cursor:
        print targetId

    foundIds = list(cursor)
    targetId = pickRandomID(copy.deepcopy(foundIds), connection, params)

    (resultLength, cost) = getLenAndCostOfId(targetId, connection) if(targetId > -1) else fitNormalAndDrawLenAndCostSample(foundIds, connection)

    utility = resultLength + cost

    print "got float string %f" % float(utility)

    print "process cost was %i" % cost

    print utility

    return utility

import ast
paramMap = ast.literal_eval(sys.argv[1])
main(paramMap)
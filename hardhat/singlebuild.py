#!/usr/bin/env python

# build client script for building a project

# must be run from the hardhat directory, which will be updated to the
# appropriate CVS vintage by this script, so it's a good idea to first
# bring the hardhat directory (or at least this file) up to the latest
# vintage with a "cvs update -A" before running it, since after running
# it, it may get reverted to an earlier version

import hardhatutil, time, smtplib, os, sys, getopt

project = 'newchandler'


def usage():
    global project
    
    print "python singlebuild.py [OPTION]..."
    print ""
    print "-b BUILDVER    string to put into the buildversion encoded in app"
    print "-d DATE        date to use for CVS checkout"
    print "-t TAG         tag to use for CVS checkout"
    print "-p PROJECT     buildscript, defaults to ", project
    print "-m MAILTO      who to email when build is finished (optional)"
    print "-n BUILDNAME   buildname (optional)"
    print "-s             if specified, skip tests (optional)"    
    print "\nFor example:"
    print "  python singlebuild.py -t CHANDLER_0_3_23"    


def main():
    global project
    
    nowString = time.strftime("%Y-%m-%d %H:%M:%S")
    nowShort = hardhatutil.RemovePunctuation(nowString)
    # nowString is the current time, in a CVS-compatible format
    print nowString
    # nowShort is nowString without punctuation or whitespace
    print nowShort

    try:
        opts, args = getopt.getopt(sys.argv[1:], "b:d:m:p:t:n:s")
    except getopt.GetoptError:
        usage()
        sys.exit(1)

    buildVersionArg = None
    cvsDateArg = None
    toAddrArg = None
    projectArg = None
    cvsTagArg = None
    buildName = 'buildname'
    noTests = 0

    for opt, arg in opts:

        if opt == "-b":
            buildVersionArg = arg

        if opt == "-d":
            cvsDateArg = arg

        if opt == "-m":
            toAddrArg = arg

        if opt == "-p":
            projectArg = arg

        if opt == "-t":
            cvsTagArg = arg

        if opt == "-n":
            buildName = arg

        if opt == "-s":
            noTests = 1

    if cvsDateArg and cvsTagArg:
        print "Please choose either a cvs date or tag, not both"
        sys.exit(1)

    # defaults:
    if projectArg:
        project = projectArg
        
    if toAddrArg:
        toAddr  = toAddrArg
    else:
        toAddr = None

    buildVersion = nowString

    # default is "-D now", but override with date; override that with tag
    cvsVintage = "-D'" + nowString + "'"
    if cvsDateArg:
        cvsVintage = "-D'" + cvsDateArg + "'"
        buildVersion = cvsDateArg
    if cvsTagArg:
        cvsVintage = "-r" + cvsTagArg
        buildVersion = cvsTagArg
    if buildVersionArg:
        buildVersion = buildVersionArg

    print "nowString", nowString
    print "nowShort", nowShort
    print "cvsVintage", cvsVintage
    print "buildVersion", buildVersion
    print "buildName", buildName
    print "skipTests=", noTests

    # cvsVintage is what is used to do a checkout
    # buildVersion is encoded into the application's internal version

    whereAmI = os.path.dirname(os.path.abspath(hardhatutil.__file__))
    hardhatFile = os.path.join(whereAmI, "hardhat.py")

    homeDir = os.environ['HOME']
    buildDir = os.path.join(homeDir, "singlebuild")
    logFile = os.path.join(buildDir, "build.log")
    buildscriptFile = os.path.join("buildscripts", project + ".py")
    fromAddr = "builds"
    fromAddr += "@"
    fromAddr += "osafoundation.org"
    print "Mail to ", toAddr
    print "Build dir", buildDir
    print "Build file ", buildscriptFile

    curDir = os.path.abspath(os.getcwd())

    if os.path.exists(buildDir):
        hardhatutil.rmdirRecursive(buildDir)
    os.mkdir(buildDir)

    path = os.environ.get('PATH', os.environ.get('path'))
    cvsProgram = hardhatutil.findInPath(path, "cvs")

    log = open(logFile, "w+")
    try:
        # bring this hardhat directory up to date
        outputList = hardhatutil.executeCommandReturnOutputRetry(
         [cvsProgram, "-z3", "update", "-dP", cvsVintage])

        # load the buildscript file for the project
        mod = hardhatutil.ModuleFromFile(buildscriptFile, "buildscript")

        # SendMail(fromAddr, toAddr, nowString, nowString, buildName,
        # "building", None)

        mod.Start(hardhatFile, buildDir, cvsVintage, buildVersion, 1, log,
                  skipTests=noTests)

    except Exception, e:
        import traceback
        traceback.print_exc()
        print "something failed"
        log.write("something failed")
        status = "build_failed"
    else:
        print "all is well"
        log.write("all is well")
        status = "success"
    log.close()

    log = open(logFile, "r")
    logContents = log.read()
    log.close()

    if toAddr:
        SendMail(fromAddr, toAddr, nowString, buildName, status, logContents)


def SendMail(fromAddr, toAddr, startTime, buildName, status, logContents):
    nowTime  = str(int(time.time()))
    subject  = "[singlebuild] " + status + " from " + buildName
    msg      = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n" % (fromAddr, toAddr, subject))
    msg      = msg + "tinderbox: tree: Chandler\n"
    msg      = msg + "tinderbox: buildname: " + buildName + "\n"
    msg      = msg + "tinderbox: starttime: " + startTime + "\n"
    msg      = msg + "tinderbox: timenow: " + nowTime + "\n"
    msg      = msg + "tinderbox: errorparser: unix\n"
    msg      = msg + "tinderbox: status: " + status + "\n"
    msg      = msg + "tinderbox: administrator: builds@osafoundation.org\n"
    msg      = msg + "tinderbox: END\n"
    if logContents:
        msg  = msg + logContents

    server = smtplib.SMTP('mail.osafoundation.org')
    server.sendmail(fromAddr, toAddr, msg)
    server.quit()


main()

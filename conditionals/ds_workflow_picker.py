#!/usr/bin/python
import plistlib
import subprocess
import sys
import os

def get_medium_type_disk(disk_id):
    # Uses diskutil to process whether a physical disk is a SolidState or not.
    disk = 'disk' + str(disk_id)
    cmd = ['/usr/sbin/diskutil', 'info', '-plist', disk]
    proc = subprocess.Popen(cmd, shell=False, bufsize=-1,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, err = proc.communicate()
    try:
        plist = plistlib.readPlistFromString(output)
        sp_medium_type = plist['SolidState']
        return sp_medium_type
    except Exception:
        return {}

def get_software_version():
    # Fetch running software version, for APFS compatibility purposes.
    cmd = ['/usr/bin/sw_vers', '-productVersion']
    proc = subprocess.Popen(cmd, shell=False, bufsize=-1,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, err = proc.communicate()
    try:
        macos_version = output[:5]
        return macos_version
    except Exception:
        return {}

def get_model_identifier():
    # Uses sysctl to find the model identifier of the machine.
    cmd = ['/usr/sbin/sysctl', 'hw.model']
    proc = subprocess.Popen(cmd, shell=False, bufsize=-1,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, err = proc.communicate()
    try:
        sp_model_identifier = output[10:]
        return sp_model_identifier
    except Exception:
        return {}

if get_medium_type_disk(0) is True and get_medium_type_disk(1) is False or get_medium_type_disk(1) is True and get_medium_type_disk(0) is False:
    if get_software_version() == '10.13':
        print "Booted OS is %s" % get_software_version()
        if 'iMac' in get_model_identifier() or 'Macmini' in get_model_identifier():
            print "Fusion drive detected, running fusion drive workflow"
            storage = "0"
        else:
            if get_medium_type_disk(0) is True:
                print "Multiple storage volumes detected but device is not a valid model, SSD installed on disk0 assuming SSD workflow"
                storage = "1"
            else:
                print "Multiple storage volumes detected but device is not a valid model, HDD installed on disk0 assuming HDD workflow"
                storage = "2"
    else:
        print "Booted OS is %s, APFS restores will not be possible" % get_software_version()
        if 'iMac' in get_model_identifier() or 'Macmini' in get_model_identifier():
            print "Fusion drive detected, running fusion drive workflow"
            storage = "4"
        else:
            if get_medium_type_disk(0) is True:
                print "Multiple storage volumes detected but device is not a valid model, SSD installed on disk0 assuming SSD workflow"
                storage = "3"
            else:
                print "Multiple storage volumes detected but device is not a valid model, HDD installed on disk0 assuming HDD workflow"
                storage = "2"
elif get_medium_type_disk(0) is True:
    if get_software_version() == '10.13':
        print "SSD detected on disk0, assuming SSD workflow"
        storage = "1"
    else:
        print "SSD detected on disk0 but not running APFS compatible OS, HFS SSD workflow"
        storage = "3"
elif get_medium_type_disk(0) is False:
    print "HDD detected on disk0, assuming HDD workflow"
    storage = "2"
else:
    print "Possible issue with storage medium detected, redirecting to warning workflow"
    storage = "5"

if "0" in storage:
    print "RuntimeSelectWorkflow: Fusion"
if "1" in storage:
    print "RuntimeSelectWorkflow: SSD"
if "2" in storage:
    print "RuntimeSelectWorkflow: HDD"
if "3" in storage:
    print "RuntimeSelectWorkflow: SSD-ALT"
if "4" in storage:
    print "RuntimeSelectWorkflow: Fusion-ALT"
if "5" in storage:
    print "RuntimeSelectWorkflow: Storage-Warning"

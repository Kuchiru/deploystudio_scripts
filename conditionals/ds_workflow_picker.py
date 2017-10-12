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
def detect_apfs_container():
    # Uses diskutil to determine if APFS is used or not.
    cmd = ['/usr/sbin/diskutil', 'apfs', 'list', '-plist']
    proc = subprocess.Popen(cmd, shell=False, bufsize=-1,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    output, err = proc.communicate()
    try:
        plist = plistlib.readPlistFromString(output)
        array = plist.get('Containers')
        apfs_dict = array[0]
        apfs_marker = apfs_dict.get('APFSContainerUUID')
        return apfs_marker
    except Exception:
        return False

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

# Fusion drive detection has been prepared for future APFS support, edit the "storage" value to correspond with the workflow you want to run.
# See the bottom of the script which values will result in which workflow, do not forget to rename the workflow names to correspond with your own.
# When using this script be sure to enable python in your netboot environment.

if get_medium_type_disk(0) is True and get_medium_type_disk(1) is False or get_medium_type_disk(1) is True and get_medium_type_disk(0) is False:
    if get_software_version() == '10.13':
        print "netbooted OS is %s" % get_software_version()
        if 'iMac' in get_model_identifier() or 'Macmini' in get_model_identifier():
            print "Fusion drive detected, running fusion drive workflow"
            storage = "0"
            # Runs when a fusion drive is detected on a netbooted 10.13
        else:
            if get_medium_type_disk(0) is True:
                print "Multiple storage volumes detected but device is not a valid model, SSD installed on disk0 assuming SSD workflow"
                storage = "1"
                # Runs SSD workflow when multiple volumes are detected but the unit has not been identified as a model that has a Fusion drive, only runs on netbooted OS 10.13.
            else:
                print "Multiple storage volumes detected but device is not a valid model, HDD installed on disk0 assuming HDD workflow"
                storage = "2"
                # Runs HDD workflow when multiple volumes are detected but the unit has not been identified as a model that has a Fusion drive, only runs on netbooted OS 10.13.
    else:
        print "netbooted OS is %s, APFS restores will not be possible" % get_software_version()
        if 'iMac' in get_model_identifier() or 'Macmini' in get_model_identifier():
            print "Fusion drive detected, running fusion drive workflow"
            storage = "4"
            # Runs when a fusion drive is detected on an netbooted OS lower than 10.13
        else:
            if get_medium_type_disk(0) is True:
                print "Multiple storage volumes detected but device is not a valid model, SSD installed on disk0 assuming SSD workflow"
                storage = "3"
                # Runs SSD workflow when multiple volumes are detected but the unit has not been identified as a model that has a Fusion drive, only on netbooted OS lower than 10.13.
            else:
                print "Multiple storage volumes detected but device is not a valid model, HDD installed on disk0 assuming HDD workflow"
                storage = "2"
                # Runs HDD workflow when multiple volumes are detected but the unit has not been identified as a model that has a Fusion drive, only on netbooted OS lower than 10.13.
elif get_medium_type_disk(0) is True:
    if get_software_version() == '10.13':
        print "netbooted OS is %s" % get_software_version()
        print "SSD detected on disk0, assuming SSD workflow"
        storage = "1"
        # Runs SSD workflow, only when 10.13 is detected.
    else:
        if detect_apfs_container() is False:
            print "SSD detected on disk0 but not running APFS compatible OS, HFS SSD workflow"
            storage = "3"
            # Runs SSD workflow, only when netbooted OS is a lower version than 10.13.
        else:
            print "APFS container detected, repartitioning not possible in 10.12"
            storage = "6"
            # Either redirect to workflow that can destroy APFS containers to restore 10.12 or warning workflow.
elif get_medium_type_disk(0) is False:
    print "HDD detected on disk0, assuming HDD workflow"
    storage = "2"
    # Runs HDD workflow
else:
    print "Possible issue with storage medium detected, redirecting to warning workflow"
    storage = "5"
    # Will direct to warning workflow to notify that there is no storage volume present.

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

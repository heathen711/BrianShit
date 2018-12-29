#!/usr/bin/env python

import argparse
import os
import random
import shlex
import subprocess


def run_and_check(command):
    print "Executing: {}".format(command)
    result = subprocess.check_output(shlex.split(command))
    print "Output:\n{}".format(result)
    return result.strip()


def sudo_command(command):
    return run_and_check("SUDO_ASKPASS=/tmp/ask_pass.sh; sudo -A {}".format(command))


def get_lab_name():
    hostname = run_and_check("hostname")
    return hostname.split("-")[0]


def copy_and_install(path):
    sudo_command("cp {path} /tmp/".format(path=path))
    sudo_command(
        "installer -pkg {} -target /".format(
            os.path.join("/tmp", os.path.basename(path))
        )
    )
    sudo_command("rm {}".format(os.path.join("/tmp", os.path.basename(path))))


def install_adobe():
    lab_name = get_lab_name()
    if lab_name in ["D2"]:
        return

    path = "/Volumes/labs/{lab_name}/".format(lab_name=lab_name)
    sudo_command("cp {path} /tmp/".format(path=path))

    local_pkg = os.path.join("/tmp", "build/{lab_name}_install.pkg".format(lab_name))
    sudo_command(
        "installer -pkg {} -target /".format(
            local_pkg
        )
    )
    sudo_command("rm {}".format(os.path.join("/tmp", os.path.basename(path))))


def make_user(username, real_name, password, admin=False):
    uid = random.randint(1010, 3000)
    gid = 1000
    if admin:
        gid = 20

    commands = [
        "dscl . -create /Users/{username}",
        "dscl . -create /Users/{username} UserShell /bin/bash",
        "dscl . -create /Users/{username} RealName {real_name}",
        "dscl . -create /Users/{username} UniqueID {uid}",
        "dscl . -create /Users/{username} PrimaryGroupID {gid}",
        "dscl . -create /Users/{username} NFSHomeDirectory /Local/Users/{username}",
        "dscl . -passwd /Users/{username} {password}",
    ]
    for command in commands:
        sudo_command(
            command.format(
                username=username,
                password=password,
                gid=gid,
                uid=uid,
                real_name=shlex.quote(real_name)
            )
        )

    if admin:
        sudo_command("dscl . -append /Groups/admin GroupMembership {username}".format(username=username))


def main():
    # Echo out admin password to a shell script for SUDO to be able to use
    run_and_check("echo 'echo {}' > /tmp/ask_pass.sh; chmod +x /tmp/ask_pass.sh".format("Il0v3Mamab3@r!"))

    try:
        make_user("Teacher", "Teacher", "T3@ch3r2013", True)

        commands = [
            # Activate ARD
            "/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart "
                "-activate -configure -allowAccessFor -specifiedUsers",
            "/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart "
                "-activate -configure -access -on -privs -ControlObserve -TextMessages -DeleteFiles "
                "-OpenQuitApps -GenerateReports -RestartShutDown -SendFiles -ChangeSettings -users admin,teacher",

            # Install Office
            "installer -pkg /Volumes/labs/office.pkg -target /",

            # Remove unneeded Apps
            "rm -rf '/Applications/Mircosoft OneNote.app'",
            "rm -rf '/Applications/Mircosoft Outlook.app'",

            # Install Licenser
            "installer -pkg /Volumes/labs/office_licence.pkg -target /",

            # Install MS updater
            "installer -pkg /Volumes/labs/mau.pkg -target /",

            # Copy Chrome
            "cp '/Volumes/labs/Google Chrome.app' /Applications/",
        ]
        for command in commands:
            sudo_command(command)

        if get_lab_name() == "F1":
            make_user("tartan", "tartan", "beyonce*")
            commands = [
                "cp '/Volumes/labs/Firefox.app' /Applications/",
            ]
            for command in commands:
                sudo_command(command)

        if get_lab_name() == "F3":
            copy_and_install("/Volumes/labs/maya.pkg")
            copy_and_install("/Volumes/labs/mudbox.pkg")
            run_and_check("open '/Volumes/labs/Unity Download Assistant.app'")

        if get_lab_name() == "D2":
            sudo_command("cp '/Volumes/labs/Audacity.app' /Applications/")
            sudo_command("cp '/Volumes/labs/MuseScore 3.app' /Applications/")

        install_adobe()
    finally:
        run_and_check("rm /tmp/ask_pass.sh")


if __name__ == "__main__":
    main()

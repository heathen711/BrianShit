#!/usr/bin/env python

import argparse
import inspect
import pprint
import os
import random
import pipes
import shlex
import subprocess
import stat


def run_and_check(command, env={}):
    cur_env = os.environ.copy()
    cur_env.update(env)
    print "Executing: {}".format(command)
    print "Env: {}".format(cur_env)
    result = subprocess.check_output(shlex.split(command), env=cur_env)
    print "Output:\n{}".format(result)
    return result.strip()


def sudo_command(command):
    return run_and_check("sudo -A {}".format(command), {"SUDO_ASKPASS": "/tmp/ask_pass.sh"})


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
                real_name=pipes.quote(real_name)
            )
        )

    if admin:
        sudo_command("dscl . -append /Groups/admin GroupMembership {username}".format(username=username))


def main():
    admin_password = "Il0v3Mamab3@r!"
    askpass_path = "/tmp/ask_pass.sh"
    with open(askpass_path, "w") as writer:
        writer.write("#!/bin/sh\n")
        writer.write("echo \"{}\"".format(admin_password))
    st = os.stat(askpass_path)
    os.chmod(askpass_path, st.st_mode | stat.S_IEXEC)

    try:
        make_user("Teacher", "Teacher", "T3@ch3r2013", True)

        commands = [
            # Activate ARD
            "/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart "
                "-activate -configure -allowAccessFor -specifiedUsers",
            "/System/Library/CoreServices/RemoteManagement/ARDAgent.app/Contents/Resources/kickstart "
                "-activate -configure -access -on -privs -ControlObserve -TextMessages -DeleteFiles "
                "-OpenQuitApps -GenerateReports -RestartShutDown -SendFiles -ChangeSettings -users administrator,teacher",

            # Install Office
            "installer -pkg /Volumes/Labs/Office.pkg -target /",

            # Remove unneeded Apps
            "rm -Rf '/Applications/Mircosoft OneNote.app'",
            "rm -Rf '/Applications/Mircosoft Outlook.app'",

            # Install Licenser
            "installer -pkg /Volumes/Labs/Office_Serializer.pkg -target /",

            # Install MS updater
            "installer -pkg /Volumes/Labs/MAU.pkg -target /",
            "'/Library/Application Support/Mircosoft/MAU2.0/Microsoft AutoUpdate.app/Contents/MacOS/msupdate' -i",

            # Copy Chrome
            "cp '/Volumes/Labs/Google Chrome.app' /Applications/",
        ]
        for command in commands:
            sudo_command(command)

        if get_lab_name() == "F1":
            make_user("tartan", "tartan", "beyonce*")
            commands = [
                "cp '/Volumes/Labs/Firefox.app' /Applications/",

                # Copy over all user icons
                "cp /Volumes/Labs/F1_icons /Library/User Pictures/",

                # Remove JPEGPhoto and Picture args then set to new icon
                "dscl . -delete /Users/admin JPEGPhoto",
                "dscl . -delete /Users/admin Picture",
                "dscl . -create /Users/admin Picture '/Library/User Pictures/F1_icons/admin.jpg",

                "dscl . -delete /Users/Teacher JPEGPhoto",
                "dscl . -delete /Users/Teacher Picture",
                "dscl . -create /Users/Teacher Picture '/Library/User Pictures/F1_icons/Teacher.jpg",

                "dscl . -delete /Users/tartan JPEGPhoto",
                "dscl . -delete /Users/tartan Picture",
                "dscl . -create /Users/tartan Picture '/Library/User Pictures/F1_icons/tartan.jpg",
            ]
            for command in commands:
                sudo_command(command)

        if get_lab_name() == "F3":
            copy_and_install("/Volumes/Labs/maya.pkg")
            copy_and_install("/Volumes/Labs/mudbox.pkg")
            run_and_check("open '/Volumes/Labs/Unity Download Assistant.app'")

        if get_lab_name() == "D2":
            sudo_command("cp '/Volumes/Labs/Audacity.app' /Applications/")
            sudo_command("cp '/Volumes/Labs/MuseScore 3.app' /Applications/")

        install_adobe()

        sudo_command("touch /var/db/.BrianSetupDone")

        sudo_command("softwareupdate --install -a")
    finally:
        pprint.pprint(inspect.trace())
        if os.path.exists("/tmp/ask_pass.sh"):
            os.remove("/tmp/ask_pass.sh")


if __name__ == "__main__":
    main()

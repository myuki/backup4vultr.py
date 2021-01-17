#!/usr/bin/env python3

import json
import os
import sys
from Vultr import Vultr

# Default Value
apiToken: str = ""
instanceID: str = ""
description: str = ""
reservedSnapshotList: set = set()
reservedSnapshotDescription: set = set()


# Get config from JSON
def getConfig(path: str):
  global apiToken, instanceID, description, reservedSnapshotList, reservedSnapshotDescription
  # Check the file if exist
  if os.path.exists(path):
    with open(path, "r") as file:
      config: dict = json.load(file)
      # If key exist, overwrite the script default value
      if "apiToken" in config.keys():
        apiToken = config["apiToken"]
      if "instanceID" in config.keys():
        instanceID = config["instanceID"]
      if "description" in config.keys():
        description = config["description"]
      if "reservedSnapshotList" in config.keys():
        reservedSnapshotList = set(config["reservedSnapshotList"])
      if "reservedSnapshotDescription" in config.keys():
        reservedSnapshotDescription = set(config["reservedSnapshotDescription"])


if __name__ == "__main__":
  # Init Vultr object
  getConfig(sys.path[0] + "/config.json")
  vultr: Vultr = Vultr(apiToken)

  # Check command
  if len(sys.argv) == 2:
    # List instances and snapshots
    if sys.argv[1] == "list":
      vultr.listInstances()
      print()
      vultr.listSnapshots()
      sys.exit(0)
    # Use snapshot to backup
    elif sys.argv[1] == "backup":
      if reservedSnapshotDescription:
        reservedSnapshotList = reservedSnapshotList.union(vultr.getSnapshotsByDescription(reservedSnapshotDescription))
      print("Backup...")
      vultr.backup(instanceID, description, reservedSnapshotList)
    # Display available commands
    else:
      print("Error, command wrong")
      print("Command list:")
      print("list - List all instances and snapshots")
      print("backup - Backup by create a snapshot (Delete the oldest snapshot if snapshots reach the limit)")
  else:
    print("Command list:")
    print("list - List the instances and snapshots")
    print("backup - Backup by create a snapshot (Delete the oldest snapshot if snapshots reach the limit)")

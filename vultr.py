import datetime
import json
import re
import requests
import sys
import time


class Vultr:
  apiToken: str
  instanceMeta: dict
  instanceList: list
  snapshotMeta: dict
  snapshotList: list

  httpHeaders: dict = {"Content-Type": "application/json"}
  retries: int = 3  # Retry 3 times
  timeout: int = 5

  def __init__(self, apiToken: str):
    # Check the API token and init vultr object
    if apiToken == "":
      print("API Token is empty")
      sys.exit(1)
    self.apiToken = apiToken
    self.httpHeaders["Authorization"] = "Bearer " + apiToken

  # Get the list of instances
  # curl --location --request GET 'https://api.vultr.com/v2/instances' --header 'Authorization: Bearer {api-key}'
  def getInstanceList(self) -> bool:
    # Retry 3 times
    for i in range(self.retries):
      try:
        response = requests.get("https://api.vultr.com/v2/instances", headers=self.httpHeaders, timeout=self.timeout)
      except Exception as e:
        print(e)
        print("Error, try again after 3s")
        time.sleep(3)
      else:
        # Check respond
        if response.status_code == 200:
          instances: dict = json.loads(response.text)
          self.instanceMeta = instances["meta"]
          self.instanceList = instances["instances"]
        else:
          print("Fail to get instance list")
          if response.status_code == 400:
            print("400 Bad Request")
          elif response.status_code == 401:
            print("401 Unauthorized")
          elif response.status_code == 403:
            print("403 Forbidden")
          elif response.status_code == 404:
            print("404 Not Found")
          else:
            print(response.status_code, "Unknown Error")
          print(response.text)
          return False
        break
    return True

  # Check whether the instance list exist and get the instance list if doesn't exist
  def checkInstanceList(self) -> bool:
    if "instanceList" not in dir(self):
      if not self.getInstanceList():
        return False
    return True

  # Check the Instance ID if in the list
  def checkInstanceID(self, inputInstancesID) -> bool:
    if not self.checkInstanceList():
      return False
    for instance in self.instanceList:
      if inputInstancesID == instance["id"]:
        return True
    return False

  # List all instances
  def listInstances(self) -> bool:
    if not self.checkInstanceList():
      return False
    print("Instance List:")
    print("ID                                   Label RAM  Main IP")
    for instance in self.instanceList:
      print(instance["id"], instance["label"], instance["ram"], instance["main_ip"])
    return True

  # Get the list of snapshots
  # curl --location --request GET "https://api.vultr.com/v2/snapshots" --header "Authorization: Bearer {api-key}"
  def getSnapshotList(self) -> bool:
    # Retry 3 times
    for i in range(self.retries):
      try:
        response = requests.get("https://api.vultr.com/v2/snapshots", headers=self.httpHeaders, timeout=self.timeout)
      except Exception as e:
        print(e)
        print("Error, try again after 3s")
        time.sleep(3)
      else:
        # Check respond
        if response.status_code == 200:
          snapshots: dict = json.loads(response.text)
          self.snapshotMeta = snapshots["meta"]
          self.snapshotList = snapshots["snapshots"]
        else:
          print("Fail to get snapshot list")
          if response.status_code == 401:
            print("401 Unauthorized")
          else:
            print(response.status_code, "Unknown Error")
          print(response.text)
          return False
        break
    return True

  # Check whether the snapshot list exist and get the snapshot list if doesn't exist
  def checkSnapshotList(self) -> bool:
    if "snapshotList" not in dir(self):
      if not self.getSnapshotList():
        return False
    return True

  # Check the Snapshot ID if in the list
  def checkSnapshotID(self, inputSnapshotID) -> bool:
    if not self.checkSnapshotList():
      return False
    for snapshot in self.snapshotList:
      if inputSnapshotID == snapshot["id"]:
        return True
    return False

  # List all snapshots
  def listSnapshots(self) -> bool:
    if not self.checkSnapshotList():
      return False
    print("Snapshot List:")
    print("ID                                   Size        Created Date              Status   Description")
    for snapshot in self.snapshotList:
      print(snapshot["id"], snapshot["size"], snapshot["date_created"], snapshot["status"], "\"" + snapshot["description"] + "\"")
    return True

  # Mark the reserved snapshot in list
  def markReservedSnapshot(self, id: str) -> bool:
    if not self.checkSnapshotList():
      return False
    for snapshot in self.snapshotList:
      if id in snapshot["id"]:
        snapshot["reservedFlag"] = 1
    return True

  # Get the oldest snapshot's ID
  # ISO 8601 Format: yyyy-mm-ddThh:mm:ss+00:00
  def getOldestBackupSnapshot(self) -> str:
    if not self.checkSnapshotList():
      print("Fail to get the oldest snapshot's ID")
      return ""
    # Get current time
    timeNow: datetime.datetime = datetime.datetime.now().astimezone()
    oldestDate: datetime.datetime = timeNow

    # Compare all snapshots
    oldestID: str = ""
    for snapshot in self.snapshotList:
      if "reservedFlag" not in snapshot:
        snapshotDateDate = datetime.datetime.strptime(snapshot["date_created"], "%Y-%m-%dT%H:%M:%S%z")
        if snapshotDateDate < oldestDate:
          oldestDate = snapshotDateDate
          oldestID = snapshot["id"]
    return oldestID

  # Get Snapshot's ID by description
  def getSnapshotsByDescription(self, descriptionList: set) -> set:
    resultList: set = set()
    if not self.checkSnapshotList():
      return resultList
    for description in descriptionList:
      for snapshot in self.snapshotList:
        if description in snapshot["description"]:
          resultList.add(snapshot["id"])
    return resultList

  # Create a new snapshot for specific VM
  # curl --location --request POST "https://api.vultr.com/v2/snapshots" --header "Authorization: Bearer {api-key}" --header "Content-Type: application/json" --data-raw "{"instance_id": "a632673e-2fd5-4ff1-b251-2e28e7b65504", "description" : "my snapshot"}"
  def createSnapshot(self, instanceID: str, description: str = "") -> bool:
    if self.snapshotMeta["total"] >= 10:
      print("Fail to create a snapshot, reach the limit")
      return False
    payload = {"instance_id": instanceID, "description": description}
    # Retry 3 times
    for i in range(self.retries):
      try:
        response = requests.post("https://api.vultr.com/v2/snapshots", headers=self.httpHeaders, data=json.dumps(payload), timeout=self.timeout)
      except Exception as e:
        print(e)
        print("Error, try again after 3s")
        time.sleep(3)
      else:
        # Check respond
        if response.status_code == 201:
          responseJson: dict = json.loads(response.text)
          snapshot: dict = responseJson["snapshot"]
          print("Create snapshot", snapshot["id"], "success")
        else:
          print("Fail to create a snapshot")
          if response.status_code == 400:
            print("400 Bad Request")
          elif response.status_code == 401:
            print("401 Unauthorized")
          else:
            print(response.status_code, "Unknown Error")
          print(response.text)
          return False
        break
    return True

  # Delete snapshot
  # curl --location --request DELETE "https://api.vultr.com/v2/snapshots/{snapshot-id}" --header "Authorization: Bearer {api-key}"
  def deleteSnapshot(self, snapshotID: str) -> bool:
    if "snapshotList" not in dir(self):
      if not self.getSnapshotList():
        return False
    # Retry 3 times
    for i in range(self.retries):
      try:
        response = requests.delete("https://api.vultr.com/v2/snapshots/" + snapshotID, headers=self.httpHeaders, timeout=self.timeout)
      except Exception as e:
        print(e)
        print("Error, try again after 3s")
        time.sleep(3)
      else:
        # Check the respond
        if response.status_code == 204:
          # Delete in snapshot list
          for i in range(len(self.snapshotList)):
            deletedSnapshot: dict = self.snapshotList[i]
            if snapshotID == deletedSnapshot["id"]:
              del self.snapshotList[i]
              self.snapshotMeta["total"] -= 1
              break
          print("Delete snapshot", snapshotID, "success")
        else:
          print("Fail to delete the snapshot")
          if response.status_code == 400:
            print("400 Bad Request")
          elif response.status_code == 401:
            print("401 Unauthorized")
          elif response.status_code == 404:
            print("404 Not Found")
          else:
            print(response.status_code, "Unknown Error")
          print(response.text)
          return False
        break
    return True

  # Backup instance
  def backup(self, instanceID: str, description: str = "", reservedSnapshotList: set = set()) -> bool:
    # Check the instance ID
    if not self.checkInstanceID(instanceID):
      print("Instances ID is wrong, this is instance list:")
      self.listInstances()
      return False

    # Check the limit of snapshot, each account has 10 quota
    snapshotsLimit: int = 10
    reservedLength: int = len(reservedSnapshotList)
    if reservedLength == snapshotsLimit:
      print("Snapshots reach the limit")
      print("Please remove at least %d in reservedSnapshotList." % (snapshotsLimit - reservedLength + 1))
      return False

    # Check the reserved snapshot if in the list
    for reservedSnapshot in reservedSnapshotList:
      if not self.checkSnapshotID(reservedSnapshot):
        print("Please check the reserved snapshot, snapshot", reservedSnapshot, "not in the list")
        return False

    # Mark the snapshot need be reserved
    for reservedSnapshot in reservedSnapshotList:
      if not self.markReservedSnapshot(reservedSnapshot):
        print("Fail to mark the reserved snapshot", reservedSnapshot)
        return False

    # Delete the oldest snapshot if reach the snapshot limit
    snapshotTotal: int = self.snapshotMeta["total"]
    while snapshotTotal >= snapshotsLimit:
      if not self.deleteSnapshot(self.getOldestBackupSnapshot()):
        print("Fail to delete the oldest snapshot")
        return False
      snapshotTotal = self.snapshotMeta["total"]

    # Create snapshot
    if not self.createSnapshot(instanceID, description):
      return False
    return True

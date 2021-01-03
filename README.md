# A script for backup Vultr Server

Use snapshot to backup Vultr VPS. It can delete the oldest snapshot when it reaches the limit.

You can specify the limit or use the default limit (Every Vultr Account has 10 quotas). You also can specify which snapshot should be reserved and not be deleted.

By use `cron`, it can be used to auto backup Vultr Server.

## Vultr APIv2

Warning, this script use [Vultr APIv2](https://www.vultr.com/api/v2/) but snapshot and instance ID still display as [APIv1](https://www.vultr.com/api/) on the website. You shuld run `backup4vultr.py list` before backup.

## Command

```Bash
list - List all instances and snapshots

backup - Create a snapshot
```

## config.json

If `config.json` doesn't exist, it will use the default value in `backup4vultr.py`. You also can direct modify the `backup4vultr.py` to config if you like.

```json
{
  "apiToken": "",
  "instanceID": "",
  "description": "snapshot4vultr.py",
  "configSnapshotsLimit": 10,
  "keepedSnapshotList": [
    "137e9227-657f-480d-a325-e643310d112b"
  ]
}
```

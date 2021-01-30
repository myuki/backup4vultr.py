# A script for backup Vultr Server

Use snapshot to backup Vultr VPS. It can delete the oldest snapshot when it reaches the limit.

You can specify the limit or use the default limit (Every Vultr Account has 10 quotas). You also can specify which snapshot should be reserved and not be deleted.

By use `cron`, it can be used to auto backup Vultr Server.

```
0 0 */7 * * python3 .../backup4vultr.py/backup4vultr.py backup > /dev/null 2>&1
```

## Command

```
list - List all instances and snapshots

backup - Backup by create a snapshot (Delete the oldest snapshot if snapshots reach the limit)
```

## config.json

If `config.json` doesn't exist, it will use the default value in `backup4vultr.py`. You also can direct modify the `backup4vultr.py` to config if you like.

```json
{
  "apiToken": "",
  "instanceID": "",
  "description": "snapshot4vultr.py",
  "reservedSnapshotList": [
    "137e9227-657f-480d-a325-e643310d112b"
  ],
  "reservedSnapshotDescription": [
    "Description substring1",
    "Description substring2"
  ]
}
```

You can specify which snapshots need be reserved. Also, you can use description to mark snapshots to be reserved. Each value is independent and will take effect if the description includes the value.

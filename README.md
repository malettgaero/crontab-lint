# crontab-lint

> Static analyzer and syntax checker for crontab expressions with human-readable schedule previews.

---

## Installation

```bash
pip install crontab-lint
```

---

## Usage

Run the linter against a crontab expression directly from the command line:

```bash
$ crontab-lint "*/5 * * * * /usr/bin/backup.sh"
```

**Output:**
```
✔  Expression : */5 * * * * /usr/bin/backup.sh
   Schedule   : Every 5 minutes
   Next runs  : 2024-05-01 12:05, 12:10, 12:15, 12:20, 12:25
```

You can also lint an entire crontab file:

```bash
$ crontab-lint --file /etc/cron.d/myjobs
```

Or use it as a library in your Python code:

```python
from crontab_lint import lint

result = lint("0 9 * * 1-5 /usr/bin/report.sh")
print(result.description)  # "At 09:00 AM, Monday through Friday"
print(result.is_valid)     # True
```

---

## Features

- Validates crontab syntax and catches common mistakes
- Generates plain-English descriptions of schedules
- Previews upcoming execution times
- Supports standard 5-field and extended 6-field (with seconds) expressions
- Exits with a non-zero status code on errors — CI/CD friendly

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.
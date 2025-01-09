_(from zsh manual 15.5)_
## Parameters Set By The Shell
In the table the variables are prefixed with the `$` for practical purposes

| Parameter | Description | Example |
| --------- | ----------- | ------- |
| $! | PID of last bg/spawned command | 22456 |
| ${#} | Number of positional parameters | 2 |
| $ARGC | Same as ${#} | |
| $ | PID of this shell | 22345 |
| $- | Shell flags | |
| $* | Array of positional parameters | commit |
| $argv | Same as $* | |
| $@ | Same as $* | |
| $? | Last command exit status | 0 |
| $status | Same as $? | |
| $pipestatus | Array of exit statuses of pipeline | |
| $_ | Last argument to previous command | |
| $CPUTYPE | Machine type (runtime) | |
| $EGID | Effective group id | |
| $EUID | Effective user id | |
| $ERRNO | Value of errno | |

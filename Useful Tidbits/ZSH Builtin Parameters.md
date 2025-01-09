_(from zsh manual 15.5)_
## Parameters Set By The Shell
In the table the variables are prefixed with the `$` for practical purposes

| Parameter | Description | Example | State | Type | Special | sh |
| --------- | ----------- | ------- | --- | --- | --- | --- |
| $! | PID of last bg/spawned command | 22456 | RO | int | Y |
| ${#} | Number of positional parameters | 2 | RO | int | Y |
| $ARGC | Same as ${#} | | RO | int | Y | Y
| $$ | PID of this shell | 22345 | RO | int | Y |
| $- | Shell flags | | RO | str | Y |
| $* | Positional parameters | commit | RO | arr | Y |
| $argv | Same as $* | | | arr | Y | Y
| $@ | Same as argv[@] | | RO | arr | Y |
| $? | Last command exit status | 0 | RO | int | Y |
| $0 | Shell invoker | | | str | Y |
| $status | Same as $? | | RO | int | Y | Y
| $pipestatus | Array of exit statuses of pipeline | | Y | Y
| $_ | Last argument to previous command | | str | Y | Y
| $CPUTYPE | Machine type (runtime) | | | str | Y |
| $EGID | Effective group ID | | | int | Y |
| $EUID | Effective user ID | | | int | Y |
| $ERRNO | Value of errno | | | int | Y |
| $FUNCNEST | Shell functions nesting depth | | | int | Y |
| $GID | Real group ID | | | int | Y |
| $HISTCMD | Current history event number | | RO | int | |
| $HOST | Hostname | | | str | |
| $LINENO | Current script line number | | RO | int | Y |
| $LOGNAME | Current login name | | | str | Y |
| $MACHTYPE | Machine type (compiled) | | | str | |
| $OLDPWD | Previous working directory | | | str | |
| $OPTARG | `getopts` last processed value | | | str | Y |
| $OPTIND |`getopts` last processed index | | | int | Y |
| $OSTYPE | Operating system (compiled) | | | str | Y |
| $PPID | Parent PID | | RO | int | Y |
| $PWD | Present working directory | | | str | |
| $RANDOM | 15 bit pseudo random number | | | int | Y |
| $SECONDS | Seconds since invovation or set | | | int/float | Y |
| $SHLVL | Shell level | | | int | Y |
| $signals | Signal names | | | arr | |
| $TRY_BLOCK_ERROR | `always` block level, error indicator | | | 1/0 | Y |
| $TRY_BLOCK_INTERRUPT | `always` block level, interrupt indicator | | | 1/0 | Y |
| $TTY | TTY name | | | str | |
| $TTYIDLE | Idle time of shell TTY | | RO | int | Y |
| $UID | Real user ID | | | int | Y |
| $USERNAME | Real username | | | str | Y |
| $VENDOR | Vendor name (compiled) | | | str | Y |
| $zsh_eval_context | Shell code context | | RO | :stack | Y | Y
| $ZSH_EVAL_CONTEXT | Shell code context | | RO | :stack | Y |
| $ZSH_ARGZERO | Script name or invoked shell command | | | str | |
| $ZSH_EXECUTION_STRING | `-c` option argument | | | str | |
| $ZSH_NAME | Invoked shell command | | | str | |
| $ZSH_PATCHLEVEL | zsh repository tag | | | str | |
| $zsh_scheduled_events | zsh_scheduled_events | | | str | |
| $ZSH_SCRIPT | Script name | | | str | |
| $ZSH_SUBSHELL | Shell forks | | RO | int | |
| $ZSH_VERSION | zsh version | | | str | |

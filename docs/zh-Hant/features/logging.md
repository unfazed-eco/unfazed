Unfazed 日志
======

unfazed 提供了简单的进程安全的日志 handler。


## 背景

在 python 中，logging 是线程安全的，但不是进程安全的，如果 web 应用结合 uvicorn 或者 gunicorn 等采用多进程服务，那么 logging 在并发下就会出现问题。


> 参考：https://docs.python.org/3/library/logging.html#thread-safety



## 使用

在以上的背景下，unfazed 提供了一个进程安全的日志 handler，其原理是每个进程都会创建一个独立的日志文件，这样就不会出现多进程写入同一个文件的问题。


使用配置

```python

# settings.py

UNFAZED_SETTINGS = {
    "LOGGING": {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "file": {
                "class": "unfazed.logging.handlers.UnfazedRotatingFileHandler",
                "filename": "unfazed.log",
                "formatter": "simple",
            },
        },
        "loggers": {
            "unfazed": {
                "handlers": ["file"],
                "level": "DEBUG",
            },
        },
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        },
    }
}

```

当各个进程拉起时，会根据进程号以及时间戳为各个进程创建一个独立的日志文件，如下：


```shell

>>>unfazed_hostname_pid12345_ts1630000000.log
>>>unfazed_hostname_pid12346_ts1630000000.log
>>>unfazed_hostname_pid12347_ts1630000000.log

```


## 高级

关于日志收集系统，大多数公司都有自己的 ELK 日志系统，建议将日志的写入和收集分开，应用程序只负责写入日志，然后在服务器上使用 filebeat 等工具将日志收集到 ELK 系统中。


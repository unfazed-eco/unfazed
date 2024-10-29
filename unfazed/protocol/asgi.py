class ASGIType:
    HTTP_REQUEST_START = "http.request"
    HTTP_RESPONSE_START = "http.response.start"
    HTTP_RESPONSE_BODY = "http.response.body"
    HTTP_DISCONNECT = "http.disconnect"

    LIFESPAN_STARTUP = "lifespan.startup"
    LIFESPAN_STARTUP_COMPLETE = "lifespan.startup.complete"
    LIFESPAN_STARTUP_FAILED = "lifespan.startup.failed"
    LIFESPAN_SHUTDOWN = "lifespan.shutdown"
    LIFESPAN_SHUTDOWN_COMPLETE = "lifespan.shutdown.complete"
    LIFESPAN_SHUTDOWN_FAILED = "lifespan.shutdown.failed"

    WS_ACCEPT = "websocket.accept"
    WS_RECEIVE = "websocket.receive"
    WS_SEND = "websocket.send"
    WS_DISCONNECT = "websocket.disconnect"

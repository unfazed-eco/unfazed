import typing as t

Middleware = t.NewType("Middleware", str)
Middlewares = t.Sequence[Middleware]

InstalledApp = t.NewType("InstalledApp", str)
InstalledApps = t.Sequence[InstalledApp]

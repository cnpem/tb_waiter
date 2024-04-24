# Tensorboard Waiter

Simple api to manage tensorboard instances on demand.

## TODO
- [x] Init FastAPI
- [x] Add a route to start the tensorboard
- [x] setup subprocess to start multiple tensorboards
- [x] Add a route to stop
- [x] Add a route to get the list of the active tensorboards
- [x] setup docker
- [x] setup reverse proxy with dynamic paths to tensorboards ports
- [] setup ssl
- [] clean up idle tensorboards
- [] token route
- [] test connection w/ frontend
- [] setup ci workflows
rebuild=${1:-0}
# If the base image ms-base does not exists, build it
if [[ "$(docker images -q ms-base:latest 2> /dev/null)" == ""]] || [[$rebuild]]; then
  docker build --file base.dockerfile --tag ms-base:latest
fi
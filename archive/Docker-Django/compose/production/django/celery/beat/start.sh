#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


celery -A smart_dispatch.taskapp beat -l INFO

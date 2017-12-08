#!/bin/bash
###############################################################################
# Script to build environment and pipeline
# @author: oazmon
###############################################################################
#
# determine the script base directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$( cd ${SCRIPT_DIR}/.. && pwd )"
WORK_DIR="${BASE_DIR}"
# Log levels (e.g.: trace debug info warn error)
log_level=(error warn info)

# Setting script to exit on error
set -e


# -----------------------------------------------------------------------------
# Initializing variables
# -----------------------------------------------------------------------------
. ${SCRIPT_DIR}/common.sh
. ${BASE_DIR}/sceptre.run.properties

VARS_FILE=$BASE_DIR/vars.yaml
SCEPTRE_OPTS="${SCEPTRE_OPTS} --var-file ${VAR_FILE}"


# Apply debug, if requested
if [ ! -z ${DEBUG} ]; then
    SCEPTRE_OPTS="--debug $SCEPTRE_OPTS"
fi 

#------------------------------------------------------------------------------
# function that outputs script usage/help
#------------------------------------------------------------------------------
function script_usage() {
  trap - EXIT
  echo "--------------------------------------------------------------------------------"
  echo "Description: A Script to manage AWS using Sceptre"
  echo ""
  echo "Usage: ${BASH_SOURCE[1]} [command] [additional arguments]"
  echo "  <empty>      - runs import"
  echo "  import       - imports all environments."
  echo "                 Arguments: none"
  echo "  import-env   - imports a single environment."
  echo "                 Arguments: environment"
  echo "  import-stack - imports a single stack."
  echo "                 Arguments: environment and stack"
  echo "  help         - script usage"
  echo ""
  echo "E.g.:"
  echo "  sh ./${BASH_SOURCE[1]}"
  echo "--------------------------------------------------------------------------------"
}

#------------------------------------------------------------------------------
# Helper function to determine if Python is running in a virtualenv
#------------------------------------------------------------------------------
function get_python_virtual() {
    python -c '
import sys
if hasattr(sys, "real_prefix"):
  print("virtual")
else:
  print("real")
'
}

#------------------------------------------------------------------------------
# Setup Sceptre Run
#------------------------------------------------------------------------------
function setup_sceptre_migration_tool_run() {
    show_hosting_info
    
    log "info" ":::::::::::::::::::::::: Setting up sceptre_migration_tool"
    if [ $(type sceptre_migration_tool >/dev/null 2>&1; echo $?) -ne 0 ]; then
        if [ $(type python >/dev/null 2>&1; echo $?) -ne 0 ]; then
            log "error" "Unable to automatically install Python. Please install it yourself."
            exit -1
        fi
        if [ $(type pip >/dev/null 2>&1; echo $?) -ne 0 ]; then
            log "error" "Unable to automatically install 'pip' (Python package installer). Please install it yourself."
            exit -1
        fi
        if [[ ! "${log_level[@]}" =~ "debug" ]]; then
            pip_logging="-q"
        fi
        if [ $(get_python_virtual) == "virtual" ]; then
            pip_user=""
        else
            pip_user="--user"
        fi     
        pip install --upgrade ${pip_user} ${pip_logging} sceptre_migration_tool
    fi
    sceptre_migration_tool_path=$(
        cd $(pip show sceptre_migration_tool | grep '^Location' | cut -d: -f2-)
        sceptre_migration_tool=$(pip show sceptre_migration_tool -f | grep 'bin/sceptre_migration_tool')
        cd $(dirname ${sceptre_migration_tool})
        echo $PWD
    )
    export PATH="$PATH:${sceptre_migration_tool_path}"
    log "debug" "PATH=${PATH}"
    
    read -r -a VARS_YAML <<<$(parse_yaml ${VARS_FILE})
    obtain_credentials VARS_YAML
    make_vpc_id_array VARS_YAML result_array
    for item in ${result_array[@]}; do
        SCEPTRE_OPTS="$SCEPTRE_OPTS --var $item"
    done
    export SCEPTRE_OPTS
    log "debug" "SCEPTRE_OPTS=${SCEPTRE_OPTS}"
}

#------------------------------------------------------------------------------
# Run Sceptre Migration Tool
#------------------------------------------------------------------------------
function run_sceptre_migration_tool() {
    args=${@}
    log "info" "--------------------------------------------------------------------------------"
    log "info" "Run sceptre_migration_tool ${args}"
    log "info" "--------------------------------------------------------------------------------"
    run_in ${WORK_DIR} sceptre_migration_tool ${SCEPTRE_OPTS} ${args}
}

#------------------------------------------------------------------------------
# Unconditional Cleanup at End
#------------------------------------------------------------------------------
function finish() {
    exit_code=$?
   
    # closing message
    script_endtime=$(date +"%s")
    script_diff=$(($script_endtime-$script_startime))
    if [ ${exit_code} -eq 0 ]; then
       ending="SUCCESS"
    else
       ending="FAILURE"
    fi
    log "info" "--------------------------------------------------------------------------------"
    log "info" "${ending} '${BASH_SOURCE[1]} $@'; Duration: $(($script_diff / 3600 ))H:$((($script_diff % 3600) / 60))M:$(($script_diff % 60))S; exit_code=${exit_code}" 
    log "info" "--------------------------------------------------------------------------------"
}

#------------------------------------------------------------------------------
# Main script entry point
#------------------------------------------------------------------------------
function main() {
    script_startime=$(date +"%s")
    log "info" "--------------------------------------------------------------------------------"
    log "info" "Starting '${BASH_SOURCE[1]} $@'..."
    log "info" "--------------------------------------------------------------------------------"
    process_paws_if_needed
    command=${1}
    case "$command" in
        "help" )
            script_usage
            ;;
        * )
            setup_sceptre_migration_tool_run
            run_sceptre_migration_tool ${@}
            ;;
    esac
}

#------------------------------------------------------------------------------
# Execute main script entry point
#------------------------------------------------------------------------------
trap finish EXIT
main ${@}

# >>>>>> End of File <<<<<<

#!/bin/bash

IFS=' ' read -r MAILBOX ALIAS < alias_maps
psql -U postfix mail -c "delete from alias_maps where mailbox like '$MAILBOX';"


#!/bin/bash

IFS=' ' read -r MAILBOX ALIAS < alias_maps
psql -U postfix mail -c "insert into alias_maps values('$MAILBOX', '$ALIAS');"

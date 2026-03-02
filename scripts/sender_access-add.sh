#!/bin/bash

IFS=' ' read -r SENDER ACCESS < sender_access
psql -U postfix mail -c "insert into sender_access values('$SENDER', '$ACCESS');"

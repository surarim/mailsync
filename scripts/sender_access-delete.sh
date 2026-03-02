#!/bin/bash

IFS=' ' read -r SENDER ACCESS < sender_access
psql -U postfix mail -c "delete from sender_access where sender like '$SENDER';"

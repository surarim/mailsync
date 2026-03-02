#!/bin/bash

psql -U postfix mail -c "select * from sender_access;"


#!/bin/bash

psql -U postfix mail -c "select * from alias_maps;"


#!/bin/bash
ps afux | grep "^joker" > ps ; vi ps ; rm -f ps

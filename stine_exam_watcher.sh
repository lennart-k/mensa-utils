#!/bin/bash

i=$(./stine.py getexams | wc -l)
while true
do
  new=$(./stine.py getexams | wc -l)
  
  if [ "$i" == "$new" ];
  then
    echo nothing happened
  else
    echo AAAAHHH!!! Panik!
  fi
  i=$new

  sleep 2m
done

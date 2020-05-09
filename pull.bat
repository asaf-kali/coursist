@echo off

set BRANCHES=master shani evyatar kirsh avihai

for %%b in (%BRANCHES%) do (
   git checkout %%b
   git pull
)
echo Done

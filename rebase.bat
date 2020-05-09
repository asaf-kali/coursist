@echo off

set BRANCHES=master shani evyatar kirsh avihai

for %%b in (%BRANCHES%) do ( 
   git checkout %%b
   git pull
   git rebase asaf
   git push
)
echo Done

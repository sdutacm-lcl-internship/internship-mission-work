## git基本操作指令

**根据远程分支拉取创建本地分支**

git checkout -b [待创建的本地分支名称] remotes/origin/远程主分支

修改项目内容。。。

**查看自己修改的内容**

git status

**提交到缓存区**

git add .

或者

git commit -a

**提交到本地git仓库**

git commit -m '修改说明信息'

**提交到远程分支**

 git push <远程主机名> <本地分支名>:<远程分支名>

git push -u origin '远程自己的分支名'

**切换分支**

git checkout '分支名'

**删除本地分支**

git branch -d '分支名'






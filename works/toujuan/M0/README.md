如何从指定分支检出新分支
要从指定分支创建并检出一个新分支，可以使用以下命令：

git checkout -b 新分支名 指定分支名  
例如，如果想从 develop 分支检出一个名为 feature-x 的新分支，可以这样做：

git checkout -b feature-x develop  
git add 是 add 文件到哪里去？
git add 是将文件的更改添加到暂存区（staging area）。只有在暂存区中的更改，才会在下一次执行 git commit 时包含到提交里。

没有使用 git add 的文件，即使它们有改动，也不会被 git commit 包含。因此，确保在提交之前，使用 git add 将所有需要的更改添加到暂存区。
如果 master 更新了，你的分支要如何对齐它的更新？
如果 master 分支有了更新，你可以通过以下步骤将你的分支与 master 对齐：

切换到 master 分支并更新：

git checkout master  
git pull origin master  
切换回你的分支：

git checkout 你的分支名  
将 master 的更新合并到你的分支：

git merge master  
另外，你也可以在你的分支上直接执行 git pull 来进行变基，方法如下：

git pull origin master --rebase  
这会将你当前分支上的更改应用到 master 分支的更新之上。选择合适的方式取决于你的工作流和需求。